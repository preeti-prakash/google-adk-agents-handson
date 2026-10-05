from google.adk.agents import LlmAgent
from google.adk.models import Gemini
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)
from google.genai import types

# The MCP server (server.py) runs on port 8002
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://employee-bq-mcp-681195791124.us-central1.run.app/mcp/bq"
    )
)

root_agent = LlmAgent(
    name="employee_database_agent",
    # Retry with backoff on 429 (rate limit) and 503 (model overloaded)
    model=Gemini(
        model="gemini-2.5-flash",
        retry_options=types.HttpRetryOptions(
            attempts=5,
            initial_delay=2,
            max_delay=30,
            http_status_codes=[429, 503],
        ),
    ),
    instruction="""
    You are an Employee Database Assistant.

    Use the MCP tools to answer employee questions. Every question about
    people, names, IDs, departments or roles is a question about the
    employees in the database, so always look it up with a tool:

    - An employee ID: use get_employee.
    - A department (e.g. "who works in AI Engineering"): use get_employees_by_department.
    - A role or job title (e.g. "who is an AI engineer"), a name, or
      the full list: use get_all_employees and find the matching employees.
    - Adding someone: use add_employee.

    Answer with the employees' names and details from the tool results.
    If nobody matches, say so.
    """,
    tools=[mcp_toolset],
)
