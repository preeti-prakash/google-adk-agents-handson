from google.adk.agents import LlmAgent
from google.adk.tools.mcp_tool.mcp_toolset import (
    McpToolset,
    StreamableHTTPConnectionParams,
)

# The MCP server (server.py) runs on port 8001, because adk web uses 8000
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="http://localhost:8001/mcp/local"
    )
)

root_agent = LlmAgent(
    name="employee_database_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are an Employee Database Assistant.

    Use the MCP tools to answer employee questions.
    """,
    tools=[mcp_toolset],
)
