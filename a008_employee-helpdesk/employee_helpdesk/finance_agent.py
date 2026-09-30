"""Finance specialist agent: expense policy and reimbursements (mock data)."""

from google.adk.agents.llm_agent import Agent

from .config import MODEL

# Mock expense policy: maximum reimbursable amount per claim, in USD.
EXPENSE_POLICY = {
    'hotel': {'limit': 200, 'note': 'Per night. Receipt required.'},
    'meals': {'limit': 75, 'note': 'Per day. Alcohol is not reimbursable.'},
    'travel': {'limit': 1000, 'note': 'Economy class only. Book through the travel portal.'},
    'software': {'limit': 300, 'note': 'Needs manager approval before purchase.'},
    'training': {'limit': 1500, 'note': 'Per year. Must relate to your role.'},
}


def check_expense_policy(expense_type: str) -> dict:
    """Returns the reimbursement limit and rules for an expense type.

    Args:
        expense_type: One of "hotel", "meals", "travel", "software" or
            "training".

    Returns:
        dict: The limit in USD and any notes, or the list of known types.
    """
    policy = EXPENSE_POLICY.get(expense_type.strip().lower())
    if policy is None:
        return {'error': f'Unknown expense type "{expense_type}".', 'available': list(EXPENSE_POLICY)}
    return {'expense_type': expense_type, 'limit_usd': policy['limit'], 'note': policy['note']}


def calculate_reimbursement(amount: float, category: str) -> dict:
    """Calculates how much of an expense can be reimbursed.

    Args:
        amount: The amount spent, in USD.
        category: The expense category, e.g. "hotel" or "meals".

    Returns:
        dict: The amount claimed, the reimbursable amount and anything the
        employee has to cover themselves.
    """
    policy = EXPENSE_POLICY.get(category.strip().lower())
    if policy is None:
        return {'error': f'Unknown category "{category}".', 'available': list(EXPENSE_POLICY)}
    reimbursable = min(amount, policy['limit'])
    return {
        'category': category,
        'amount_spent_usd': amount,
        'limit_usd': policy['limit'],
        'reimbursable_usd': reimbursable,
        'not_covered_usd': round(amount - reimbursable, 2),
        'note': policy['note'],
    }


finance_agent = Agent(
    model=MODEL,
    name='finance_agent',
    description=(
        'Handles finance questions: expense policies, spending limits and how '
        'much of an expense (hotel, meals, travel, software, training) can be '
        'reimbursed.'
    ),
    instruction="""
You are the Finance specialist.

- For "what's the limit / rule for X" questions, use check_expense_policy.
- For "how much can I claim" questions with an amount, use
  calculate_reimbursement with the amount and the closest category.
- Mention anything not covered and any requirements (like receipts).
- Answer only from the tool results. Don't make up limits.

Reply in a friendly, conversational way. If the question is not about
finance or expenses, transfer back to employee_helpdesk.
""",
    tools=[check_expense_policy, calculate_reimbursement],
)
