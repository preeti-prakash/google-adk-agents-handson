import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.genai.types import Content, Part

# A plain Python script doesn't load .env the way `adk web` does, so load it here.
load_dotenv(Path(__file__).parent / ".env")


async def main():

    # 1. Create the agent
    root_agent = LlmAgent(
        name="employee_assistant",
        model="gemini-2.5-flash",
        instruction="""
        You are an employee assistant.
        Answer the user's questions clearly and helpfully.
        Keep the conversation going even if the user says
        things like "thanks", "that's helpful", or "perfect".
        Do not decide when the conversation should end.
        """
    )

    # 2. Create session service
    session_service = InMemorySessionService()

    # 3. Create Runner
    runner = Runner(
        agent=root_agent,
        app_name="employee_assistant_app",
        session_service=session_service,
    )

    # 4. Create a session
    user_id = "user_123"
    session_id = "session_001"

    await session_service.create_session(
        app_name="employee_assistant_app",
        user_id=user_id,
        session_id=session_id,
    )

    # 5. Static user message
    message = Content(
        role="user",
        parts=[
            Part(
                text="My name is Preeti and I work in the Cloud Engineering team."
            )
        ],
    )

    # 6. Send message to the agent
    events = runner.run(
        user_id=user_id,
        session_id=session_id,
        new_message=message,
    )

    # 7. Read the final response
    for event in events:
        if event.is_final_response():
            print("Agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
