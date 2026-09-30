import asyncio
import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.genai.types import Content, Part

# A plain Python script doesn't load .env the way `adk web` does, so load it here.
load_dotenv(Path(__file__).parent / ".env")

PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["AGENT_ENGINE_LOCATION"]

# Your deployed Agent Engine / Reasoning Engine resource (sessions are stored here)
REASONING_ENGINE_APP_NAME = (
    f"projects/{PROJECT_ID}/"
    f"locations/{LOCATION}/"
    f"reasoningEngines/{os.environ['AGENT_ENGINE_ID']}"
)


async def main():

    # 1. Create the agent
    root_agent = LlmAgent(
        name="employee_assistant",
        model="gemini-2.5-flash",
        instruction="""
        You are an employee assistant.

        Answer the user's questions clearly and helpfully.
        Use the conversation history when answering follow-up questions.
        """
    )

    # 2. Create Vertex AI Session Service
    session_service = VertexAiSessionService(
        project=PROJECT_ID,
        location=LOCATION,
    )

    # 3. Create Runner
    runner = Runner(
        agent=root_agent,
        app_name=REASONING_ENGINE_APP_NAME,
        session_service=session_service,
    )

    user_id = "user_123"

    # 4. Resume a session if its ID was passed on the command line,
    #    otherwise create a new persistent Vertex AI session
    if len(sys.argv) > 1:
        session = await session_service.get_session(
            app_name=REASONING_ENGINE_APP_NAME,
            user_id=user_id,
            session_id=sys.argv[1],
        )
        if session is None:
            sys.exit(f"Session {sys.argv[1]} not found.")
        print(f"Resumed session {session.id} with {len(session.events)} saved events.")
    else:
        session = await session_service.create_session(
            app_name=REASONING_ENGINE_APP_NAME,
            user_id=user_id,
        )
        print("Session ID:", session.id)
        print("To resume later, run this script with that ID as an argument.")

    # 5. Conversation loop
    while True:

        user_text = input("You: ")

        if user_text.lower() == "exit":
            print("Conversation ended.")
            break

        # Create user message
        message = Content(
            role="user",
            parts=[
                Part(text=user_text)
            ],
        )

        # 6. Run agent using the same session (run_async: the session service is async)
        async for event in runner.run_async(
            user_id=user_id,
            session_id=session.id,
            new_message=message,
        ):
            # 7. Display final response
            if event.is_final_response():
                print("Agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
