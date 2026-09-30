"""Trip Planner: a small parallel ADK workflow.

                 ┌─> weather_agent ─────┐
    START ──────>├─> attractions_agent ─┼──> join ──> planner_agent
                 └─> food_agent ────────┘

The three research agents run at the same time (they don't depend on each
other). `join` waits for all three, then planner_agent combines their results
from state. Run with `adk web` from adk-fundamentals.
"""

from google.adk.agents import LlmAgent
from google.adk.workflow import JoinNode
from google.adk.workflow import START
from google.adk.workflow import Workflow

MODEL = 'gemini-3.5-flash'

# Parallel step 1 -> state['weather']
weather_agent = LlmAgent(
    model=MODEL,
    name='weather_agent',
    instruction='For the city in the user\'s message, describe the typical weather and what to pack, in 2 bullet points.',
    output_key='weather',
)

# Parallel step 2 -> state['attractions']
attractions_agent = LlmAgent(
    model=MODEL,
    name='attractions_agent',
    instruction='For the city in the user\'s message, list the top 3 attractions, one line each.',
    output_key='attractions',
)

# Parallel step 3 -> state['food']
food_agent = LlmAgent(
    model=MODEL,
    name='food_agent',
    instruction='For the city in the user\'s message, list 3 local dishes to try, one line each.',
    output_key='food',
)

# Final step: runs after all three finish
planner_agent = LlmAgent(
    model=MODEL,
    name='planner_agent',
    instruction="""
Combine the research below into a short, friendly trip plan with the headings
Weather, Top Attractions and Food to Try.

Weather: {weather}
Attractions: {attractions}
Food: {food}
""",
)

# NEW WAY: Workflow. The tuple (a, b, c) runs in parallel; JoinNode waits for all.
root_agent = Workflow(
    name='trip_planner',
    edges=[(START, (weather_agent, attractions_agent, food_agent), JoinNode(name='join'), planner_agent)],
)

# OLD WAY: ParallelAgent inside a SequentialAgent (deprecated in ADK 2.x), kept for comparison
# from google.adk.agents import ParallelAgent, SequentialAgent
#
# root_agent = SequentialAgent(
#     name='trip_planner',
#     sub_agents=[
#         ParallelAgent(name='research', sub_agents=[weather_agent, attractions_agent, food_agent]),
#         planner_agent,
#     ],
# )
