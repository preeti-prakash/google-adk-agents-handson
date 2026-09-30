"""HR specialist agent: leave balances and company policies (mock data)."""

from google.adk.agents.llm_agent import Agent

from .config import MODEL

# Mock leave balances (days remaining this year).
LEAVE_BALANCES = {
    'emp1': {'vacation': 12, 'sick': 5, 'personal': 2},
    'emp2': {'vacation': 8, 'sick': 6, 'personal': 1},
    'emp3': {'vacation': 15, 'sick': 3, 'personal': 3},
}

# Mock company policies.
COMPANY_POLICIES = {
    'vacation': (
        'Full-time employees get 20 vacation days per year. Requests need '
        'manager approval at least 2 weeks in advance. Up to 5 unused days '
        'carry over to next year.'
    ),
    'sick_leave': (
        'Employees get 8 sick days per year. A doctor\'s note is required for '
        'absences longer than 3 consecutive days.'
    ),
    'remote_work': (
        'Employees may work remotely up to 3 days per week with manager '
        'approval. Core hours are 10am to 3pm local time.'
    ),
    'parental_leave': (
        'Primary caregivers get 16 weeks of paid leave; secondary caregivers '
        'get 6 weeks.'
    ),
}


def get_leave_balance(employee_id: str) -> dict:
    """Returns the remaining leave days for an employee.

    Args:
        employee_id: The employee ID, e.g. "emp1".

    Returns:
        dict: Remaining vacation, sick and personal days, or an error if the
        employee ID is unknown.
    """
    balance = LEAVE_BALANCES.get(employee_id.strip().lower())
    if balance is None:
        return {'error': f'No employee found with ID {employee_id}.'}
    return {'employee_id': employee_id, 'remaining_days': balance}


def get_company_policy(policy_name: str) -> dict:
    """Looks up a company HR policy.

    Args:
        policy_name: One of "vacation", "sick_leave", "remote_work" or
            "parental_leave".

    Returns:
        dict: The policy text, or the list of available policies if not found.
    """
    key = policy_name.strip().lower().replace(' ', '_')
    policy = COMPANY_POLICIES.get(key)
    if policy is None:
        return {'error': f'Policy "{policy_name}" not found.', 'available': list(COMPANY_POLICIES)}
    return {'policy': key, 'details': policy}


hr_agent = Agent(
    model=MODEL,
    name='hr_agent',
    description=(
        'Handles HR questions: leave and vacation balances, time off, and '
        'company policies such as vacation, sick leave, remote work and '
        'parental leave.'
    ),
    instruction="""
You are the HR specialist.

- For leave balance questions, use get_leave_balance. You need the employee's
  ID (e.g. emp1). If they haven't given it, ask for it before calling the tool.
- For policy questions, use get_company_policy with the closest policy name
  (vacation, sick_leave, remote_work, parental_leave).
- Answer only from the tool results. Don't make up numbers or rules.

Reply in a friendly, conversational way. If the question is not about HR,
transfer back to employee_helpdesk.
""",
    tools=[get_leave_balance, get_company_policy],
)
