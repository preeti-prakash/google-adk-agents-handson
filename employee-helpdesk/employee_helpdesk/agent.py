"""Employee Helpdesk: root agent that delegates to IT, HR and Finance agents.

Uses ADK's native multi-agent pattern: the specialists are passed as
`sub_agents`, and Gemini decides which one to transfer to based on each
sub-agent's `description`. There is no if/else routing in code.
"""

from google.adk.agents.llm_agent import Agent

from .config import MODEL
from .finance_agent import finance_agent
from .hr_agent import hr_agent
from .it_agent import it_agent

root_agent = Agent(
    model=MODEL,
    name='employee_helpdesk',
    description='Front desk for employee questions. Routes each request to the right specialist.',
    instruction="""
You are the Employee Helpdesk. Your only job is to understand the employee's
request and transfer it to the right specialist:

- it_agent: Wi-Fi, VPN, email, laptops, login or any technical problem.
- hr_agent: leave, vacation, time off, or company policies.
- finance_agent: expenses, reimbursements or spending limits.

Do not answer specialist questions yourself. Transfer as soon as the topic is
clear. If the request is unclear, ask one short question to clarify. For
greetings or "what can you do", briefly explain the three areas you can help
with.
""",
    sub_agents=[it_agent, hr_agent, finance_agent],
)
