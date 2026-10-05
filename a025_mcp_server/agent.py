from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool import (
    McpToolset,
    StreamableHTTPConnectionParams,
)


# Connect to the remote MCP server (server.py deployed to Cloud Run)
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://employee-mcp-854814512954.us-central1.run.app/mcp"
    )
)


root_agent = LlmAgent(
    name="employee_agent",
    model="gemini-2.5-flash",

    instruction="""
    You are an Employee Assistant.

    You can use the MCP server to retrieve employee information.

    When the user asks for a specific employee,
    use the get_employee MCP tool.

    When the user asks for the complete employee list,
    or about an employee by name, department or role,
    use the get_all_employees MCP tool.

    Provide the information clearly.
    """,

    tools=[
        mcp_toolset
    ],
)
