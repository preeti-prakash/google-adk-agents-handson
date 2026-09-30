"""IT specialist agent: system status and IT tickets (mock data)."""

import random

from google.adk.agents.llm_agent import Agent

from .config import MODEL

# Mock status of company systems.
SYSTEM_STATUS = {
    'vpn': 'degraded',
    'wifi': 'operational',
    'email': 'operational',
    'laptop_provisioning': 'operational',
    'sso_login': 'operational',
}


def check_system_status() -> dict:
    """Returns the current status of company IT systems.

    Returns:
        dict: Each system name mapped to 'operational', 'degraded' or 'down',
        plus a list of systems that currently have problems.
    """
    problems = [name for name, status in SYSTEM_STATUS.items() if status != 'operational']
    return {'systems': SYSTEM_STATUS, 'systems_with_issues': problems}


def create_it_ticket(issue: str) -> dict:
    """Creates an IT support ticket for the employee's issue.

    Args:
        issue: A short description of the problem, e.g. "VPN keeps disconnecting".

    Returns:
        dict: The new ticket ID, its status and the expected response time.
    """
    ticket_id = f'IT-{random.randint(1000, 9999)}'
    return {
        'ticket_id': ticket_id,
        'issue': issue,
        'status': 'open',
        'expected_response': 'within 4 business hours',
    }


it_agent = Agent(
    model=MODEL,
    name='it_agent',
    description=(
        'Handles IT support: Wi-Fi, VPN, email, laptops, login and other '
        'technical problems. Can check system status and create IT tickets.'
    ),
    instruction="""
You are the IT support specialist.

1. For any technical problem, call check_system_status first.
2. If the related system is degraded or down, tell the employee it's a known
   issue and create a ticket with create_it_ticket so they get updates.
3. If the system is operational, suggest one or two quick fixes (restart,
   reconnect, check cables), then create a ticket if the problem continues.
4. Always share the ticket ID when you create one.

Reply in a friendly, conversational way. If the question is not about IT,
transfer back to employee_helpdesk.
""",
    tools=[check_system_status, create_it_ticket],
)
