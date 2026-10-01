import asyncio
from pathlib import Path

from dotenv import load_dotenv
from google.adk.agents import LlmAgent
from google.adk.runners import Runner
from google.adk.sessions import InMemorySessionService
from google.adk.memory import InMemoryMemoryService
from google.adk.tools import load_memory

from google.genai.types import Content, Part

# A plain Python script doesn't load .env the way `adk web` does, so load it here.
load_dotenv(Path(__file__).parent / ".env")


APP_NAME = "employee_memory_app"
USER_ID = "user_123"


async def main():

    # --------------------------------------------------
    # 1. Create the agent
    # --------------------------------------------------

    root_agent = LlmAgent(
        name="employee_assistant",
        model="gemini-2.5-flash",
        instruction="""
        You are an employee assistant.

        Answer the user's questions clearly.

        You can use the memory tool to retrieve
        information from previous conversations.
        """,
        tools=[load_memory],
    )

    # --------------------------------------------------
    # 2. Create Session Service
    # --------------------------------------------------

    session_service = InMemorySessionService()

    # --------------------------------------------------
    # 3. Create Memory Service
    # --------------------------------------------------

    memory_service = InMemoryMemoryService()

    # --------------------------------------------------
    # 4. Create Runner
    # --------------------------------------------------

    runner = Runner(
        agent=root_agent,
        app_name=APP_NAME,
        session_service=session_service,
        memory_service=memory_service,
    )

    # ==================================================
    # SESSION 1
    # ==================================================

    session1 = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="session_001",
    )

    print("\n--- SESSION 1 ---")

    message1 = Content(
        role="user",
        parts=[
            Part(
                text="My name is Preeti and I work in the Cloud Engineering team."
            )
        ],
    )

    events = runner.run(
        user_id=USER_ID,
        session_id=session1.id,
        new_message=message1,
    )

    for event in events:
        if event.is_final_response():
            print("Agent:", event.content.parts[0].text)

    # --------------------------------------------------
    # 5. Add Session 1 to Memory
    # --------------------------------------------------

    # Re-fetch the session: `session1` above was returned before the
    # conversation, so it has no events. The stored copy has them.
    session1 = await session_service.get_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id=session1.id,
    )

    await memory_service.add_session_to_memory(session1)

    print("\nSession 1 added to memory.")


    # ==================================================
    # SESSION 2
    # ==================================================

    session2 = await session_service.create_session(
        app_name=APP_NAME,
        user_id=USER_ID,
        session_id="session_002",
    )

    print("\n--- SESSION 2 ---")

    message2 = Content(
        role="user",
        parts=[
            Part(
                text="What team do I work in?"
            )
        ],
    )

    events = runner.run(
        user_id=USER_ID,
        session_id=session2.id,
        new_message=message2,
    )

    for event in events:
        if event.is_final_response():
            print("Agent:", event.content.parts[0].text)


if __name__ == "__main__":
    asyncio.run(main())
