import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import DatabaseSessionService
from google.genai.types import Content, Part

# A plain Python script doesn't load .env the way `adk web` does, so load it here.
load_dotenv(Path(__file__).parent / ".env")

# Keep sessions.db next to this file, whichever folder the script is run from.
DB_PATH = Path(__file__).parent / "sessions.db"


async def main():

    # 1. Create the agent
    root_agent = LlmAgent(
        name="employee_assistant",
        model="gemini-2.5-flash",
        instruction="""
        You are an employee assistant.

        Answer the user's questions clearly and helpfully.

        Do not decide when the conversation should end.
        Even if the user says:
        - "Thanks"
        - "That's helpful"
        - "Perfect"
        - "That's all"

        continue the conversation normally.

        The application controls when the conversation ends.
        """
    )

    # 2. Create session service (stored in a SQLite file, so it survives restarts)
    session_service = DatabaseSessionService(
        db_url=f"sqlite+aiosqlite:///{DB_PATH}"
    )

    # 3. Create Runner
    runner = Runner(
        agent=root_agent,
        app_name="employee_assistant_app",
        session_service=session_service,
    )

    # 4. Reuse the session if it's already in the database, otherwise create it
    user_id = "user_123"
    session_id = "session_001"

    session = await session_service.get_session(
        app_name="employee_assistant_app",
        user_id=user_id,
        session_id=session_id,
    )

    if session:
        print(f"Resumed session {session_id} with {len(session.events)} saved events.")
    else:
        await session_service.create_session(
            app_name="employee_assistant_app",
            user_id=user_id,
            session_id=session_id,
        )
        print(f"Created new session {session_id}.")

    # 5. Keep the conversation running
    while True:

        # Get message from the user
        user_text = input("You: ")

        # Application controls termination
        if user_text.lower() == "exit":
            print("Conversation ended.")
            break

        # Create a user message
        message = Content(
            role="user",
            parts=[
                Part(text=user_text)
            ],
        )

        # Send the message to the agent (run_async: the database driver is async)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session_id,
            new_message=message,
        ):
            # Read the agent's final response
            if event.is_final_response():
                print("Agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
