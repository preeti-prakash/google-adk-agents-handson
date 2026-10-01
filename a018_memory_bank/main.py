import asyncio
import os
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import VertexAiSessionService
from google.adk.memory import VertexAiMemoryBankService
from google.genai.types import Content, Part

# A plain Python script doesn't load .env the way `adk web` does, so load it here.
load_dotenv(Path(__file__).parent / ".env")


PROJECT_ID = os.environ["GOOGLE_CLOUD_PROJECT"]
LOCATION = os.environ["AGENT_ENGINE_LOCATION"]
AGENT_ENGINE_ID = os.environ["AGENT_ENGINE_ID"]

APP_NAME = "employee_memory_app"
USER_ID = "user_123"


async def main():

    # ------------------------------------------------
    # 1. Agent
    # ------------------------------------------------

    root_agent = LlmAgent(
        name="employee_assistant",
        model="gemini-2.5-flash",
        instruction="""
        You are an employee assistant.

        Answer the user's questions clearly.

        You can use information retrieved from long-term
        memory when answering questions.
        """
    )

    # ------------------------------------------------
    # 2. Vertex AI Session Service
    # ------------------------------------------------

    session_service = VertexAiSessionService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=AGENT_ENGINE_ID,
    )

    # ------------------------------------------------
    # 3. Vertex AI Memory Bank
    # ------------------------------------------------

    memory_service = VertexAiMemoryBankService(
        project=PROJECT_ID,
        location=LOCATION,
        agent_engine_id=AGENT_ENGINE_ID,
    )

    # ------------------------------------------------
    # 4. Runner
    # ------------------------------------------------

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # ------------------------------------------------
    # 5. Create Session 1
    # ------------------------------------------------

    session1 = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    print("Session 1:", session1.id)

    # ------------------------------------------------
    # 6. User tells the agent something
    # ------------------------------------------------

    message1 = Content(
        role="user",
        parts=[
            Part(
                text="My name is Preeti and I work in the Cloud Engineering team."
            )
        ],
    )

    # ------------------------------------------------
    # 7. Run the agent (run_async: the Vertex AI services are async)
    # ------------------------------------------------

    async for event in runner.run_async(
        user_id=USER_ID,
        session_id=session1.id,
        new_message=message1,
    ):
        if event.is_final_response():
            print("Agent:", event.content.parts[0].text)

    # ------------------------------------------------
    # 8. Save this conversation into Memory Bank
    # ------------------------------------------------

    # Re-fetch the session: `session1` above was returned before the
    # conversation, so it has no events. The stored copy has them.
    session1 = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1.id,
    )

    # Memory Bank extracts facts in the background. Wait for it to finish so
    # the search below can find them (add_session_to_memory doesn't wait).
    print("Generating memories (this can take a little while)...")
    await memory_service.add_events_to_memory(
        app_name=APP_NAME,
        user_id=USER_ID,
        events=session1.events,
        custom_metadata={"wait_for_completion": True},
    )

    print("Session added to Vertex AI Memory Bank.")

    # ------------------------------------------------
    # 9. Create a NEW session
    # ------------------------------------------------

    session2 = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
    )

    print("Session 2:", session2.id)

    # ------------------------------------------------
    # 10. Ask something from the previous conversation
    # ------------------------------------------------

    memory_results = await memory_service.search_memory(
        app_name=APP_NAME,
        user_id=USER_ID,
        query="What team does Preeti work in?",
    )

    print("\nMemory results:")
    for memory in memory_results.memories:
        print("-", memory.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
