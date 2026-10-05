import os

from mcp.server.fastmcp import FastMCP

# Locally: 127.0.0.1:8000. In the container (Cloud Run): HOST=0.0.0.0 from the
# Dockerfile and PORT=8080 from Cloud Run.
# stateless_http: Cloud Run can send each request to a different instance, so
# don't keep MCP sessions in memory between requests.
mcp = FastMCP(
    "Employee MCP Server",
    host=os.getenv("HOST", "127.0.0.1"),
    port=int(os.getenv("PORT", "8000")),
    stateless_http=True,
)


employees = [
    {
        "id": 101,
        "name": "Preeti",
        "department": "Cloud Engineering",
        "role": "Cloud Engineer"
    },
    {
        "id": 102,
        "name": "John",
        "department": "Data Engineering",
        "role": "Data Engineer"
    },
    {
        "id": 103,
        "name": "Sarah",
        "department": "AI Engineering",
        "role": "AI Engineer"
    }
]


# -----------------------------
# MCP TOOL
# -----------------------------

@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Find an employee by ID."""

    for employee in employees:
        if employee["id"] == employee_id:
            return employee

    return {"error": "Employee not found"}


# -----------------------------
# MCP TOOL (was a resource; as a tool, agents such as ADK's McpToolset can call it)
# -----------------------------

@mcp.tool()
def get_all_employees() -> list:
    """Return the complete employee list."""

    return employees


if __name__ == "__main__":
    mcp.run(transport="streamable-http")
