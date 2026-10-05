from mcp.server.fastmcp import FastMCP

from database import get_connection, initialize_database


# Port 8001: adk web uses 8000. MCP endpoint: http://localhost:8001/mcp/local
mcp = FastMCP(
    "Employee Database MCP Server",
    port=8001,
    streamable_http_path="/mcp/local",
)


# --------------------------------
# TOOL 1: Get employee
# --------------------------------

@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Get an employee by employee ID."""

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, department, role
        FROM employees
        WHERE id = ?
        """,
        (employee_id,)
    )

    row = cursor.fetchone()

    conn.close()

    if row is None:
        return {
            "error": "Employee not found"
        }

    return {
        "id": row[0],
        "name": row[1],
        "department": row[2],
        "role": row[3]
    }


# --------------------------------
# TOOL 2: Get employees by department
# --------------------------------

@mcp.tool()
def get_employees_by_department(
    department: str
) -> list:
    """Get employees belonging to a department."""

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, department, role
        FROM employees
        WHERE LOWER(department) = LOWER(?)
        """,
        (department,)
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "department": row[2],
            "role": row[3]
        }
        for row in rows
    ]


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

    conn = get_connection()

    cursor = conn.cursor()

    try:

        cursor.execute(
            """
            INSERT INTO employees
            (id, name, department, role)
            VALUES (?, ?, ?, ?)
            """,
            (
                employee_id,
                name,
                department,
                role
            )
        )

        conn.commit()

        return f"Employee {name} added successfully."

    except Exception as e:

        return f"Error: {str(e)}"

    finally:

        conn.close()


# --------------------------------
# TOOL 4: Get all employees
# (a tool rather than a resource, so ADK's McpToolset can give it to the agent)
# --------------------------------

@mcp.tool()
def get_all_employees() -> list:
    """Return all employees."""

    conn = get_connection()

    cursor = conn.cursor()

    cursor.execute(
        """
        SELECT id, name, department, role
        FROM employees
        """
    )

    rows = cursor.fetchall()

    conn.close()

    return [
        {
            "id": row[0],
            "name": row[1],
            "department": row[2],
            "role": row[3]
        }
        for row in rows
    ]


# --------------------------------
# START SERVER
# --------------------------------

if __name__ == "__main__":

    initialize_database()

    mcp.run(
        transport="streamable-http"
    )
