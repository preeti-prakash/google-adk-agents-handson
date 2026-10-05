# Employee MCP Server

A small **MCP (Model Context Protocol)** server that shares employee data through two tools, and a client that connects to it, finds out what it offers, and uses it. The server is **deployed to Cloud Run**, and the client on the laptop calls it there.

## What is MCP?

MCP is an open standard for connecting AI apps to tools and data. Instead of writing custom code for every app, you write **one MCP server**, and **any MCP client** can use it: an ADK agent, Claude Desktop, Claude Code, an IDE, or your own script.

```
┌───────────── MCP client ─────────────┐         ┌──────── MCP server ─────────┐
│ client.py, an ADK agent,             │  HTTP   │ server.py                   │
│ Claude Desktop, an IDE, ...          │ ──────► │  tool: get_employee         │
│                                      │  /mcp   │  tool: get_all_employees    │
└──────────────────────────────────────┘         └─────────────────────────────┘
```

A server can offer three kinds of things:

| | What it is | Who uses it | In this server |
|---|---|---|---|
| **Tool** | A function that **does** something; can take arguments | The model decides to call it | `get_employee(employee_id)`, `get_all_employees()` |
| **Resource** | **Read-only data**, found by a URI | The app reads it and gives it to the model as context | none |
| **Prompt** | A reusable prompt template | The user picks it | none |

**Why everything here is a tool.** `get_all_employees` started as a resource (`@mcp.resource("employees://all")`). Resources are part of MCP, but many clients only use tools. ADK's `McpToolset`, for example, gives the agent the server's **tools** and ignores its resources. Making it a tool means an agent can call it when it needs the full list.

## What we did

```
laptop                                   Google Cloud (newaiproject-510015, us-central1)
┌──────────────┐   HTTPS POST /mcp       ┌───────────────────────────────────────────┐
│ client.py    │ ──────────────────────► │ Cloud Run service: employee-mcp           │
│ (local run)  │ ◄────────────────────── │   container built from this Dockerfile    │
└──────────────┘   tools + results       │   runs server.py on port 8080             │
                                         └───────────────────────────────────────────┘
```

1. Wrote the server (`server.py`) and tested it locally with `client.py`.
2. Made the server cloud-ready: it reads `HOST` and `PORT` from the environment and runs stateless.
3. Added a `Dockerfile`, built the image with **Cloud Build**, stored it in **Artifact Registry**, and deployed it to **Cloud Run** as `employee-mcp`.
4. Pointed `client.py` at the Cloud Run URL and ran it **on the laptop**: it found both tools and called them on Cloud Run.
5. Also tested it with `curl` and the **MCP Inspector** in the browser.

Service URL: `https://employee-mcp-854814512954.us-central1.run.app` (MCP endpoint: `/mcp`)

## Files

| File | Purpose |
|---|---|
| `server.py` | The MCP server with two tools |
| `client.py` | Connects to the server, lists the tools, calls both. Currently points to the **Cloud Run URL**. |
| `agent.py` | An **ADK agent** (`root_agent`) that uses the Cloud Run server's tools through `McpToolset`; run it with `adk web` |
| `.env` / `.env.example` | Vertex AI settings for Gemini, used by `agent.py` |
| `requirements.txt` | `mcp<2` |
| `Dockerfile` | Container image for Cloud Run |
| `.dockerignore` | Keeps `.env`, `client.py`, the README and caches out of the image |

## The code

### `server.py`

```python
mcp = FastMCP(
    "Employee MCP Server",
    host=os.getenv("HOST", "127.0.0.1"),     # 0.0.0.0 in the container
    port=int(os.getenv("PORT", "8000")),     # Cloud Run sets PORT=8080
    stateless_http=True,
)

@mcp.tool()
def get_employee(employee_id: int) -> dict:
    """Find an employee by ID."""            # ← the description clients see
    ...

@mcp.tool()
def get_all_employees() -> list:
    """Return the complete employee list."""
    ...

mcp.run(transport="streamable-http")          # serves MCP at /mcp
```

- `@mcp.tool()` turns a function into a tool. `FastMCP` builds the tool's input schema from the type hints (`employee_id: int`; none for `get_all_employees`) and its description from the docstring.
- `transport="streamable-http"` serves MCP over HTTP at `/mcp`, so clients on other machines can connect. The other common transport is `stdio`, where the client starts the server as a subprocess and talks through stdin/stdout. That only works on the same machine, so it can't be used on Cloud Run.

Why the three settings are needed for Cloud Run:

| Setting | Locally | In Cloud Run | Why |
|---|---|---|---|
| `host` | `127.0.0.1` | `0.0.0.0` (from the Dockerfile) | Cloud Run sends traffic into the container from outside. On `127.0.0.1` the server only accepts requests addressed to `localhost` and rejects the `*.run.app` address. |
| `port` | `8000` | `8080` (Cloud Run sets `PORT`) | Cloud Run sends requests to the port in `PORT` |
| `stateless_http` | — | `True` | Cloud Run can send each request to a different container, so the server mustn't depend on MCP sessions kept in memory |

### `client.py`

```python
server_url = "https://employee-mcp-854814512954.us-central1.run.app/mcp"
```

| Step | Call | What happens |
|---|---|---|
| 1 | `streamable_http_client(url)` + `ClientSession(...)` | Opens the HTTP connection |
| 2 | `session.initialize()` | Handshake: client and server agree on protocol version and features |
| 3 | `session.list_tools()` | **Discovery**: asks what tools exist, with their names, descriptions and input schemas |
| 4 | `session.call_tool("get_employee", {"employee_id": 101})` | Runs that tool on the server for one employee |
| 5 | `session.call_tool("get_all_employees", {})` | Runs the tool with no arguments for the full list |

Discovery in step 3 is what lets one server work with any client: a client, or an agent's model, learns the tools and their inputs from the server instead of having them hard-coded.

Only `server_url` changes between local and Cloud Run; the rest of the client is identical.

## Setup

```bash
pip install -r a025_mcp_server/requirements.txt     # mcp<2
```

The code uses the **MCP v1 API**. In `mcp` 2.x, `FastMCP` was renamed to `MCPServer`, so `pip install mcp` (which gets 2.x) fails with `No module named 'mcp.server.fastmcp'`.

## Option A: run everything locally

Set the URL in `client.py` to the local server:

```python
server_url = "http://localhost:8000/mcp"
```

Use two terminals, both in the `adk-fundamentals` folder with the venv active.

**Terminal 1: start the server**

```bash
python a025_mcp_server/server.py
```

You should see `Uvicorn running on http://127.0.0.1:8000`. Leave it running.

**Terminal 2: run the client**

```bash
python a025_mcp_server/client.py
```

Terminal 1 logs each request: `ListToolsRequest`, then `CallToolRequest` twice. Stop the server with `Ctrl+C`.

**Port 8000 is also `adk web`'s port.** If `adk web` is running, the server fails with `address already in use`, and the client errors with `Session terminated` because it reached `adk web` instead. Stop `adk web`, or use another port:

```bash
PORT=8001 python a025_mcp_server/server.py      # and use http://localhost:8001/mcp in client.py
```

## Option B: deploy to Cloud Run and call it from the laptop

These are the commands used, for project `newaiproject-510015` (project number `854814512954`). For another project, replace both.

### 1. One-time setup

```bash
gcloud config set project newaiproject-510015

gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com

# Let the default service account build the container
gcloud projects add-iam-policy-binding newaiproject-510015 \
  --member="serviceAccount:854814512954-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder"

# Docker repository for the image
gcloud artifacts repositories create mcp-servers \
  --repository-format=docker \
  --location=us-central1
```

Get a project's number with `gcloud projects describe PROJECT_ID --format="value(projectNumber)"`. If the service account "does not exist", run `gcloud services enable compute.googleapis.com` first, which creates it.

### 2. Build the image

Run from **inside the `a025_mcp_server` folder**. Cloud Build uploads the folder, builds the `Dockerfile`, and pushes the image to Artifact Registry, so Docker isn't needed on the laptop.

```bash
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/newaiproject-510015/mcp-servers/employee-mcp:v1
```

### 3. Deploy

```bash
gcloud run deploy employee-mcp \
  --image us-central1-docker.pkg.dev/newaiproject-510015/mcp-servers/employee-mcp:v1 \
  --region us-central1 \
  --allow-unauthenticated
```

It prints the service URL: `https://employee-mcp-854814512954.us-central1.run.app`.

`--allow-unauthenticated` makes it **public**, which we used for testing. With `--no-allow-unauthenticated` (private), requests need a login token; see [Private service](#private-service) below.

### 4. Test from the laptop

**With `client.py`** (its `server_url` already points to Cloud Run):

```bash
python a025_mcp_server/client.py
```

```
TOOLS:
- get_employee
- get_all_employees

Tool Result:
meta=None content=[TextContent(type='text', text='{\n  "id": 101,\n  "name": "Preeti", ... }')] isError=False

All Employees Result:
meta=None content=[TextContent(... Preeti ...), TextContent(... John ...), TextContent(... Sarah ...)] isError=False
```

It's the same output as the local run; only now the tools run on Cloud Run. A list result comes back as one `TextContent` per item.

**With `curl`:**

```bash
curl -X POST "https://employee-mcp-854814512954.us-central1.run.app/mcp" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_employee","arguments":{"employee_id":101}}}'
```

The reply is an event stream:

```
event: message
data: {"jsonrpc":"2.0","id":1,"result":{"content":[{"type":"text","text":"{\"id\": 101, \"name\": \"Preeti\", ...}"}],"isError":false}}
```

Use `"method":"tools/list","params":{}` to list the tools.

**In the browser, with the MCP Inspector:**

```bash
npx @modelcontextprotocol/inspector
```

It opens http://localhost:6274. Set **Transport Type** to **Streamable HTTP**, enter the URL `https://employee-mcp-854814512954.us-central1.run.app/mcp`, and click **Connect**. Then **Tools → List Tools**, pick a tool, and click **Run Tool**. The **History** panel shows the raw JSON-RPC messages.

**Opening the URL directly in a browser doesn't work.** `/` shows **Not Found** and `/mcp` shows **Not Acceptable**. Both are expected, because MCP needs `POST` requests with JSON-RPC, which the address bar can't send.

### 5. Logs

```bash
gcloud run services logs read employee-mcp --region us-central1 --limit 20
```

Or in the Console: **Cloud Run → employee-mcp → Logs**. Each call shows up as `ListToolsRequest` or `CallToolRequest`.

### 6. Update after a code change

Build with a new tag, then deploy that tag:

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/newaiproject-510015/mcp-servers/employee-mcp:v2
gcloud run deploy employee-mcp --image us-central1-docker.pkg.dev/newaiproject-510015/mcp-servers/employee-mcp:v2 --region us-central1
```

### Private service

Public means anyone with the URL can read the employee data. To make it private again:

```bash
gcloud run services remove-iam-policy-binding employee-mcp \
  --region us-central1 --member="allUsers" --role="roles/run.invoker"
```

Then the easiest way to test from the laptop is the proxy, which adds your login token to each request:

```bash
gcloud run services proxy employee-mcp --region us-central1 --port 8000
```

Set `server_url = "http://localhost:8000/mcp"` in `client.py` and run it. With `curl`, add `-H "Authorization: Bearer $(gcloud auth print-identity-token)"`.

A private service opened in the browser shows **Forbidden** ("Your client does not have permission to get URL /"), because Cloud Run blocks requests without a token before they reach the server.

### Errors we hit

| Error | Cause | Fix |
|---|---|---|
| `INVALID_ARGUMENT: Request contains an invalid argument` | `YOUR_PROJECT_ID` placeholder left in the command | Use the real project ID |
| `Service account -compute@developer.gserviceaccount.com does not exist` | `${PROJECT_NUMBER}` was empty | Use the project number directly (`854814512954-compute@...`) |
| `invalid image name ".../YOUR_PROJECT_ID/..."` | Placeholder in the image tag | Use the real project ID |
| `curl: (3) URL rejected: Malformed input` | A leftover pasted fragment broke the command | Paste each command as one complete block |
| **Forbidden** in the browser | Service is private; the browser sends no token | Use the proxy or a token, or make it public for testing |
| **Not Found** in the browser | `/` isn't an MCP endpoint | Use `/mcp` with an MCP client, `curl` or the Inspector |

### 7. Delete when done

```bash
gcloud run services delete employee-mcp --region us-central1
gcloud artifacts repositories delete mcp-servers --location us-central1
```

## Things to try

- Change `employee_id` in `client.py` to `103` (Sarah) or `999` (`{"error": "Employee not found"}`).
- Add a tool to `server.py`, for example `find_by_department(department: str)`, redeploy (step 6), and run the client: it appears under `TOOLS:` without any client changes.

## ADK agent using the Cloud Run MCP server (`agent.py`)

`client.py` calls the tools directly from code. In `agent.py`, an **ADK agent** is the MCP client: Gemini reads your question and decides which MCP tool to call.

```
You ──► ADK agent (Gemini on Vertex AI) ──McpToolset──► Cloud Run: employee-mcp ──► get_employee / get_all_employees
```

```python
mcp_toolset = McpToolset(
    connection_params=StreamableHTTPConnectionParams(
        url="https://employee-mcp-854814512954.us-central1.run.app/mcp"
    )
)

root_agent = LlmAgent(
    name="employee_agent",
    model="gemini-2.5-flash",
    instruction="...use get_employee for one employee, get_all_employees for the list...",
    tools=[mcp_toolset],
)
```

`McpToolset` connects to the server, discovers its tools and gives them to the agent like any other tool. The agent's code has no copy of the tools; add a tool to `server.py`, redeploy, and the agent can use it.

`McpToolset` only passes **tools** to the agent, not resources. That's why `get_all_employees` is a tool on the server.

**Setup:** `.env` in this folder needs the Vertex AI settings for Gemini (the same as `a002_vertex_agent`; copy `.env.example`). The MCP server must be public, or run the proxy and use `http://localhost:8000/mcp` as the URL (see [Private service](#private-service)).

**Run** from the `adk-fundamentals` folder:

```bash
adk web
```

Open http://localhost:8000 and pick **`a025_mcp_server`**. `adk web` finds `agent.py` in this folder; `server.py` and `client.py` aren't loaded. The **Events** panel shows each MCP tool call.

| Ask | Tool the agent calls | Reply |
|---|---|---|
| *Who is employee 101?* | `get_employee {"employee_id": 101}` | Preeti, Cloud Engineer in Cloud Engineering |
| *List all employees* | `get_all_employees {}` | Preeti, John and Sarah with their IDs, departments and roles |
| *Which department does Sarah work in?* | `get_all_employees {}` | AI Engineering |
| *Who is employee 999?* | `get_employee {"employee_id": 999}` | Not found |

The agent picks the tool itself: `get_employee` for an ID, `get_all_employees` for the list or a name.

Because `adk web` uses port 8000, run the local MCP server on another port (`PORT=8001`) if you test the agent against it instead of Cloud Run.
