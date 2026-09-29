"""Customer Support Ticket Triage: a small sequential ADK workflow.

    START -> analyze_agent -> reply_agent -> ticket_agent

Each step saves its output to state (`output_key`), and the next step reads
it with `{key}` in its instruction. Run with `adk web` from adk-fundamentals.
"""

from google.adk.agents import LlmAgent
from google.adk.workflow import START
from google.adk.workflow import Workflow

MODEL = 'gemini-3.5-flash'

_tickets: list[dict] = []


def create_ticket(customer_name: str, category: str, priority: str, summary: str) -> dict:
    """Creates a support ticket (mock) and returns its ID."""
    ticket = {'ticket_id': f'TKT-{1001 + len(_tickets)}', 'customer_name': customer_name,
              'category': category, 'priority': priority, 'summary': summary}
    _tickets.append(ticket)
    return ticket


# Step 1: understand the message -> state['analysis']
analyze_agent = LlmAgent(
    model=MODEL,
    name='analyze_agent',
    instruction="""
From the customer's message, identify:
- customer name ("Unknown" if not given)
- product
- one-line issue summary
- category: Returns, Delivery, Billing, Technical or Other
- priority: High (damaged or urgent), Medium, or Low
Output these as a short list.
""",
    output_key='analysis',
)

# Step 2: write the customer reply -> state['reply']
reply_agent = LlmAgent(
    model=MODEL,
    name='reply_agent',
    instruction="""
Analysis: {analysis}

Write a short, friendly reply (2-3 sentences) to the customer that apologizes
and says what happens next. Output only the reply.
""",
    output_key='reply',
)

# Step 3: create the ticket and show the result -> state['ticket']
ticket_agent = LlmAgent(
    model=MODEL,
    name='ticket_agent',
    instruction="""
Analysis: {analysis}
Reply: {reply}

Call create_ticket with the customer name, category, priority and summary.
Then show the ticket created:" with the
ticket ID, category and priority.
""",
    tools=[create_ticket],
    output_key='ticket',
)

# NEW WAY: Workflow, steps connected by edges (START -> a -> b -> c)
root_agent = Workflow(
    name='support_ticket_triage',
    edges=[(START, analyze_agent, reply_agent, ticket_agent)],
)

# OLD WAY: SequentialAgent (deprecated in ADK 2.x), kept for comparison
# from google.adk.agents import SequentialAgent
#
# root_agent = SequentialAgent(
#     name='support_ticket_triage',
#     sub_agents=[analyze_agent, reply_agent, ticket_agent],
# )
