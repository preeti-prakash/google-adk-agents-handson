# Employee Database MCP Server

An **MCP server backed by a real database** (SQLite), and an **ADK agent** that uses it. Unlike a025, where the data was a Python list, the tools here run SQL, and changes are saved to `employees.db`.

```
You ──► ADK agent (agent.py, Gemini) ──McpToolset──► MCP server (server.py, :8001/mcp/local) ──SQL──► employees.db
```

## Files

| File | Purpose |
|---|---|
| `database.py` | Creates `employees.db` with an `employees` table and three demo rows (only if empty) |
| `server.py` | MCP server with four tools that query or update the database |
| `agent.py` | ADK agent that gets the server's tools through `McpToolset` |
| `.env` / `.env.example` | Vertex AI settings for Gemini (same as `a002_vertex_agent`) |

## The database

Table `employees`:

| id | name | department | role |
|---|---|---|---|
| 101 | Preeti | Cloud Engineering | Cloud Engineer |
| 102 | John | Data Engineering | Data Engineer |
| 103 | Sarah | AI Engineering | AI Engineer |

`employees.db` is always created next to `database.py`, whichever folder you run from. It's git-ignored.

## The MCP tools

| Tool | SQL | Type |
|---|---|---|
| `get_employee(employee_id)` | `SELECT ... WHERE id = ?` | Read |
| `get_employees_by_department(department)` | `SELECT ... WHERE LOWER(department) = LOWER(?)` | Read |
| `get_all_employees()` | `SELECT ... FROM employees` | Read |
| `add_employee(employee_id, name, department, role)` | `INSERT INTO employees ...` | **Write** |

- Each tool opens a connection, runs one query and closes it.
- The queries use `?` placeholders, so values from the model are passed as parameters, never pasted into the SQL. This protects against SQL injection.
- `get_all_employees` was a resource (`employees://all`) in the original code. It's a tool here because ADK's `McpToolset` gives the agent only tools, not resources.
- `add_employee` returns `Error: UNIQUE constraint failed` for an ID that already exists. The agent turns that into a friendly reply.

## Why port 8001

`adk web` runs on port 8000, which is also `FastMCP`'s default. If both used 8000, the server couldn't start, or the agent would call `adk web` instead of the MCP server. So `server.py` uses `FastMCP(..., port=8001)`, and `agent.py` connects to `http://localhost:8001/mcp/local`.

## Run

Use two terminals, both in the `adk-fundamentals` folder with the venv active.

**Terminal 1: start the MCP server**

```bash
python a026_mcp_database/server.py
```

It creates the database if needed, then shows `Uvicorn running on http://127.0.0.1:8001`. Leave it running.

**Terminal 2: start the agent**

```bash
adk web
```

Open http://localhost:8000 and pick **`a026_mcp_database`**. Only `agent.py` is loaded; the **Events** panel shows each MCP tool call.

Start the server **before** sending a message. Otherwise the agent can't reach its tools.

## Try these

Ask in this order, in one session:

| Ask | Tool called | Result |
|---|---|---|
| *Who is employee 102?* | `get_employee` | John, Data Engineer |
| *Who works in AI Engineering?* | `get_employees_by_department` | Sarah |
| *Add employee 104, Ravi, Cloud Engineering, DevOps Engineer* | `add_employee` | "Employee Ravi added successfully." |
| *List all employees* | `get_all_employees` | All four, including Ravi |
| *Who works in Cloud Engineering?* | `get_employees_by_department` | Preeti and Ravi |
| *Add employee 101, Test, X, Y* | `add_employee` | Fails: ID 101 already exists |

Ravi is saved in `employees.db`, so he's still there after restarting the server, or in a new `adk web` session.

## Look at the database

```bash
sqlite3 -header -column a026_mcp_database/employees.db "SELECT * FROM employees;"
```

To reset to the three demo employees, stop the server, delete the file, and start the server again:

```bash
rm a026_mcp_database/employees.db
```

## Custom MCP server vs. MCP Toolbox for Databases

This is a **custom** MCP server: you write each tool and its SQL in Python. Google's **MCP Toolbox for Databases** (`brew install mcp-toolbox`) does the same job with configuration instead of code:

| | Custom server (this folder) | MCP Toolbox for Databases |
|---|---|---|
| Tools defined in | Python (`@mcp.tool()` + SQL) | `tools.yaml` (SQL + parameters) |
| Databases | Whatever your Python code connects to | Built-in support for BigQuery, Cloud SQL, AlloyDB, Postgres, MySQL, Spanner, SQLite and more |
| Connection pooling, auth, tracing | You build it | Built in |
| Good for | Learning, custom logic | Production database access |

ADK connects to either one the same way, with `McpToolset`.
