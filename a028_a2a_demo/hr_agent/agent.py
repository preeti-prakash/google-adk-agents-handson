# a028_a2a_demo / hr_agent: the CLIENT side of the A2A demo.
#
# - hr_agent is a normal local ADK agent (the root agent).
# - employee_details is a RemoteA2aAgent: a local stand-in for the agent served
#   by remote_agent.py. It only needs a name and the remote's Agent Card URL.
#   On first use it fetches the card, then forwards each delegated turn to the
#   remote server as an A2A "message/send" request and returns the reply.
# - To hr_agent it looks like any other sub-agent, so delegation (transfer)
#   works the same way; the network hop is hidden inside RemoteA2aAgent.
# - Run: start remote_agent.py first, then `adk web a028_a2a_demo`
#   (or `adk run a028_a2a_demo/hr_agent`).

from google.adk.agents import Agent
from google.adk.agents.remote_a2a_agent import RemoteA2aAgent

employee_details = RemoteA2aAgent(
    name="employee_details",
    description="Remote agent that knows employee names, designations and salaries.",
    agent_card="http://localhost:8001/.well-known/agent-card.json",
)

root_agent = Agent(
    model="gemini-3.5-flash",
    name="hr_agent",
    description="HR assistant that answers employee questions.",
    instruction="""
    You are an HR assistant.
    For any question about an employee's name, designation or salary, or about
    who works here, transfer to the employee_details agent.
    Answer general HR questions (policies, greetings) yourself, briefly.
    """,
    sub_agents=[employee_details],
)
