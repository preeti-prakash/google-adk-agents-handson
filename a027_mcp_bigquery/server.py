import os

from google.cloud import bigquery
from mcp.server.fastmcp import FastMCP

from database import TABLE, initialize_database, run_query


# Locally: http://127.0.0.1:8002/mcp/bq (adk web uses 8000, a026 uses 8001).
# In Cloud Run: HOST=0.0.0.0 from the Dockerfile, PORT=8080 from Cloud Run.
# stateless_http: Cloud Run can send each request to a different instance.
mcp = FastMCP(
    "Employee BigQuery MCP Server",
    host=os.getenv("HOST", "127.0.0.1"),
    port=int(os.getenv("PORT", "8002")),
    streamable_http_path="/mcp/bq",
    stateless_http=True,
)


# --------------------------------
# TOOL 1: Get employee
# --------------------------------

@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Get an employee by employee ID."""

    rows = run_query(
        f"""
        SELECT id, name, department, role
        FROM `{TABLE}`
        WHERE id = @employee_id
        """,
        [bigquery.ScalarQueryParameter("employee_id", "INT64", employee_id)]
    )

    if not rows:
        return {
            "error": "Employee not found"
        }

    return rows[0]


# --------------------------------
# TOOL 2: Get employees by department
# --------------------------------

@mcp.tool()
def get_employees_by_department(
    department: str
) -> list:
    """Get employees belonging to a department."""

    return run_query(
        f"""
        SELECT id, name, department, role
        FROM `{TABLE}`
        WHERE LOWER(department) = LOWER(@department)
        ORDER BY id
        """,
        [bigquery.ScalarQueryParameter("department", "STRING", department)]
    )


# --------------------------------
# TOOL 3: Add employee
# --------------------------------

@mcp.tool()
def add_employee(
    employee_id: int,
    name: str,
    department: str,
    role: str
) -> str:
    """Add a new employee to the database."""

    try:

        # BigQuery has no enforced primary key, so check for a duplicate ID first
        if get_employee(employee_id).get("id") is not None:
            return f"Error: an employee with ID {employee_id} already exists."

        run_query(
            f"""
            INSERT INTO `{TABLE}` (id, name, department, role)
            VALUES (@employee_id, @name, @department, @role)
            """,
            [
                bigquery.ScalarQueryParameter("employee_id", "INT64", employee_id),
                bigquery.ScalarQueryParameter("name", "STRING", name),
                bigquery.ScalarQueryParameter("department", "STRING", department),
                bigquery.ScalarQueryParameter("role", "STRING", role),
            ]
        )

        return f"Employee {name} added successfully."

    except Exception as e:

        return f"Error: {str(e)}"


# --------------------------------
# TOOL 4: Get all employees
# --------------------------------

@mcp.tool()
def get_all_employees() -> list:
    """Return all employees."""

    return run_query(
        f"""
        SELECT id, name, department, role
        FROM `{TABLE}`
        ORDER BY id
        """
    )


# --------------------------------
# START SERVER
# --------------------------------

if __name__ == "__main__":

    initialize_database()

    mcp.run(
        transport="streamable-http"
    )
