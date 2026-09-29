"""Party Planner: ADK 2.0 collaborative agents.

The coordinator stays in charge and calls its helpers like tools. Each helper
does its part and hands the result BACK to the coordinator (no transfer).

    coordinator (root)
      ├── details_agent  mode='task'        chats with the user until it has the details, then finish_task
      ├── venue_agent    mode='single_turn' returns a venue idea, no chatting
      └── menu_agent     mode='single_turn' returns a menu idea, no chatting
"""

from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.genai import types

# Several agents call the model in one turn, so retry on 429 (rate limit) and 503 (overloaded).
MODEL = Gemini(
    model='gemini-3.5-flash',
    retry_options=types.HttpRetryOptions(attempts=6, initial_delay=5, max_delay=60, http_status_codes=[429, 503]),
)

# Task agent: may ask the user questions, then returns the result with finish_task.
details_agent = LlmAgent(
    model=MODEL,
    name='details_agent',
    description='Collects the party details from the user: occasion, number of guests and budget.',
    instruction="""
Collect three details for the party: occasion, number of guests, and budget.
Ask the user only for what is missing, one short question at a time.
When you have all three, finish the task with a one-line summary.
""",
    mode='task',
)

# Single-turn agents: do one job and return the answer.
venue_agent = LlmAgent(
    model=MODEL,
    name='venue_agent',
    description='Suggests one party venue for the given party details.',
    instruction='Suggest one suitable venue for the party details in the request, in one sentence.',
    mode='single_turn',
)

menu_agent = LlmAgent(
    model=MODEL,
    name='menu_agent',
    description='Suggests a short party menu for the given party details.',
    instruction='Suggest a short menu (3 items) for the party details in the request, one line each.',
    mode='single_turn',
)

root_agent = LlmAgent(
    model=MODEL,
    name='coordinator',
    instruction="""
You are a party planning coordinator. Work with your helpers:
1. Call details_agent to get the occasion, number of guests and budget.
2. Then call venue_agent and menu_agent with those details.
3. Combine their answers into a short, friendly party plan with the headings
   Details, Venue and Menu.
""",
    sub_agents=[details_agent, venue_agent, menu_agent],
)
