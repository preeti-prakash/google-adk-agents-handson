# a028_a2a_demo / remote_agent.py: the REMOTE side of the A2A demo.
#
# - An ordinary ADK agent that owns employee data (name, designation, salary).
# - to_a2a() wraps it in an A2A server app (Starlette). It automatically:
#     * builds an Agent Card from the agent's name/description/tools and
#       serves it at http://localhost:8001/.well-known/agent-card.json
#     * exposes a JSON-RPC endpoint at http://localhost:8001/ that accepts
#       A2A "message/send" requests and runs this agent to answer them.
# - uvicorn serves that app, so any A2A client (here, the HR agent) can call it.
# - .env (a028_a2a_demo/.env): GOOGLE_GENAI_USE_ENTERPRISE, GOOGLE_CLOUD_PROJECT,
#   GOOGLE_CLOUD_LOCATION (Vertex AI, same as the other folders).
# - Run: python a028_a2a_demo/remote_agent.py   (keep it running)

from pathlib import Path

import uvicorn
from dotenv import load_dotenv
from google.adk.agents import Agent
from google.adk.a2a.utils.agent_to_a2a import to_a2a

# Plain `python` doesn't auto-load .env like `adk run/web` does.
load_dotenv(Path(__file__).parent / ".env")

EMPLOYEES = {
    "preeti": {"name": "Preeti", "designation": "Senior Engineer", "salary": 120000},
    "ravi": {"name": "Ravi", "designation": "Data Analyst", "salary": 85000},
    "anita": {"name": "Anita", "designation": "HR Manager", "salary": 95000},
}


def get_employee_details(employee_name: str) -> dict:
    """Returns the name, designation and salary of an employee.

    Args:
        employee_name: The employee's first name.
    """
    employee = EMPLOYEES.get(employee_name.lower())
    if employee is None:
        return {"status": "error", "message": f"No record for {employee_name}."}
    return {"status": "success", **employee}


def list_employees() -> dict:
    """Returns the names of all employees on record."""
    return {"status": "success", "employees": [e["name"] for e in EMPLOYEES.values()]}


employee_agent = Agent(
    model="gemini-3.5-flash",
    name="employee_details_agent",
    description="Looks up employee name, designation and salary from the employee records.",
    instruction="""
    You manage employee records.
    Use get_employee_details to answer questions about a specific employee's
    designation or salary, and list_employees when asked who works here.
    Only answer from the tool results.
    """,
    tools=[get_employee_details, list_employees],
)

# host/port here are what the Agent Card advertises, so they must match uvicorn.
a2a_app = to_a2a(employee_agent, host="localhost", port=8001)

if __name__ == "__main__":
    uvicorn.run(a2a_app, host="localhost", port=8001)
