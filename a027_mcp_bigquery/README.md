# Employee BigQuery MCP Server

The same MCP server and ADK agent as `a026_mcp_database`, but the data lives in a **Google BigQuery table** in the cloud instead of a local SQLite file.

```
You ──► ADK agent (agent.py, Gemini) ──McpToolset──► MCP server (server.py, :8002/mcp/bq) ──SQL──► BigQuery
                                                                                         employee_mcp.employees
```

## What changed from a026

| | a026 (SQLite) | a027 (BigQuery) |
|---|---|---|
| Where the data lives | `employees.db` file on your Mac | Table `employee_mcp.employees` in project `gen-lang-client-0540105794` |
| Connection | `sqlite3.connect(file)` | `bigquery.Client(project=...)` with your gcloud login (ADC) |
| Query parameters | `WHERE id = ?` | `WHERE id = @employee_id` + `ScalarQueryParameter` |
| Duplicate IDs | Rejected by the `PRIMARY KEY` | BigQuery has no enforced primary key, so `add_employee` checks first |
| Server port | 8001 | 8002 (so both can run alongside `adk web` on 8000) |
| Agent | — | Same, plus automatic retries on Gemini `429` / `503` |
| Tools | `get_employee`, `get_employees_by_department`, `add_employee`, `get_all_employees` | Same four tools, same names and inputs |

The agent doesn't know or care which database is behind the server. Only `database.py` and the SQL in `server.py` changed.

## Files

| File | Purpose |
|---|---|
| `database.py` | Connects to BigQuery; creates the dataset, table and three demo rows if they don't exist; `run_query()` helper |
| `server.py` | MCP server with the four tools, running BigQuery SQL |
| `agent.py` | ADK agent that gets the tools through `McpToolset`. Currently points to the **Cloud Run** server. |
| `.env` / `.env.example` | `GOOGLE_CLOUD_PROJECT` and Vertex AI settings (same as `a002_vertex_agent`) |
| `requirements.txt` | `mcp<2`, `google-cloud-bigquery`, `python-dotenv` (for the container) |
| `Dockerfile` | Container image for Cloud Run; copies only `server.py` and `database.py` |
| `.dockerignore` | Keeps `.env`, `agent.py` and the README out of the image |

## Two ways to run the server

| | Server runs | `agent.py` URL |
|---|---|---|
| **Local server** | On your Mac (`python server.py`) | `http://localhost:8002/mcp/bq` |
| **Cloud Run** | On Cloud Run (`employee-bq-mcp`) | `https://employee-bq-mcp-681195791124.us-central1.run.app/mcp/bq` |

In both cases the data is in the same BigQuery table, and only the URL in `agent.py` changes. See [Deploy to Cloud Run](#deploy-to-cloud-run) below.

## Setup

Uses the same gcloud login as the other Vertex AI agents (README section 2.2), plus BigQuery:

```bash
gcloud services enable bigquery.googleapis.com --project=YOUR_PROJECT_ID
pip install google-cloud-bigquery "mcp<2"
cp a027_mcp_bigquery/.env.example a027_mcp_bigquery/.env     # set GOOGLE_CLOUD_PROJECT
```

Create the table (optional; `server.py` also does it on startup):

```bash
python a027_mcp_bigquery/database.py
# Database initialized: <project>.employee_mcp.employees
```

## Run

Two terminals, both in the `adk-fundamentals` folder with the venv active.

**Terminal 1: MCP server**

```bash
python a027_mcp_bigquery/server.py
```

Wait for `Uvicorn running on http://127.0.0.1:8002`, and leave it running.

**Terminal 2: agent**

```bash
adk web
```

Open http://localhost:8000 and pick **`a027_mcp_bigquery`**. If `adk web` is already running, just pick it from the dropdown (restart `adk web` if it isn't listed).

## Try these

| Ask | Tool called | Result |
|---|---|---|
| *Who is employee 102?* | `get_employee` | John, Data Engineer |
| *Who works in AI Engineering?* | `get_employees_by_department` | Sarah |
| *Add employee 104, Ravi, Cloud Engineering, DevOps Engineer* | `add_employee` | "Employee Ravi added successfully." (written to BigQuery) |
| *List all employees* | `get_all_employees` | All four, including Ravi |
| *Add employee 101, Test, X, Y* | `add_employee` | Refused: ID 101 already exists |

Each answer takes a few seconds longer than with SQLite, because every tool call runs a BigQuery job in the cloud.

## See the data

**BigQuery Studio (Console):** open **BigQuery → `gen-lang-client-0540105794` → `employee_mcp` → `employees` → Preview**, or run:

```sql
SELECT * FROM `gen-lang-client-0540105794.employee_mcp.employees` ORDER BY id;
```

**Command line** (`bq` comes with the gcloud SDK):

```bash
bq query --use_legacy_sql=false \
  'SELECT * FROM `gen-lang-client-0540105794.employee_mcp.employees` ORDER BY id'
```

```bash
bq ls employee_mcp                  # tables in the dataset
bq show employee_mcp.employees      # schema and row count
```

Rows added through the agent show up here straight away. Anyone with access to the project sees the same data, which is the difference from the local SQLite file.

**Remove the test row:**

```bash
bq query --use_legacy_sql=false \
  'DELETE FROM `gen-lang-client-0540105794.employee_mcp.employees` WHERE id = 104'
```

## Things to know

- **Query parameters, not string formatting:** values from the model go in as `@parameters`, so they can't change the SQL (no SQL injection). Only the table name is in the f-string, and it comes from your own code.
- **`429 RESOURCE_EXHAUSTED`** comes from **Gemini** (Vertex AI rate limit), not BigQuery. In testing it happened after BigQuery had already returned the data. `agent.py` retries automatically, up to 5 times with backoff.
- **Cost:** queries on a table this small fall within BigQuery's free tier (1 TB of queries and 10 GB of storage per month).

## Deploy to Cloud Run

```
adk web (Mac) ──► Cloud Run: employee-bq-mcp ──► BigQuery
```

### What the server needed

| Change | Why |
|---|---|
| `host` / `port` from `HOST` / `PORT` env vars (`127.0.0.1:8002` locally, `0.0.0.0:8080` in Cloud Run) | Cloud Run reaches the container from outside, on the port it sets in `PORT` |
| `stateless_http=True` | Cloud Run can send each request to a different container |
| Its own service account `employee-bq-mcp` with `bigquery.jobUser` + `bigquery.dataEditor` | Locally the server used **your** login; on Cloud Run it runs as this account |
| `GOOGLE_CLOUD_PROJECT` set with `--set-env-vars` | `.env` isn't copied into the image |

### Commands

Run from the `a027_mcp_bigquery` folder. Add `--project` to every command so nothing goes to the wrong project.

```bash
gcloud config set project gen-lang-client-0540105794
gcloud config get-value project              # must print gen-lang-client-0540105794

# 1. APIs
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com bigquery.googleapis.com \
  --project gen-lang-client-0540105794

# 2. Let the default service account build the image
gcloud projects add-iam-policy-binding gen-lang-client-0540105794 \
  --member="serviceAccount:681195791124-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder"

# 3. Service account for the server, with BigQuery access
gcloud iam service-accounts create employee-bq-mcp \
  --display-name="Employee BigQuery MCP server" --project gen-lang-client-0540105794

gcloud projects add-iam-policy-binding gen-lang-client-0540105794 \
  --member="serviceAccount:employee-bq-mcp@gen-lang-client-0540105794.iam.gserviceaccount.com" \
  --role="roles/bigquery.jobUser"

gcloud projects add-iam-policy-binding gen-lang-client-0540105794 \
  --member="serviceAccount:employee-bq-mcp@gen-lang-client-0540105794.iam.gserviceaccount.com" \
  --role="roles/bigquery.dataEditor"

# 4. Image repository
gcloud artifacts repositories create mcp-servers --repository-format=docker --location=us-central1 \
  --project gen-lang-client-0540105794

# 5. Build the image with Cloud Build (no Docker needed locally)
gcloud builds submit \
  --tag us-central1-docker.pkg.dev/gen-lang-client-0540105794/mcp-servers/employee-bq-mcp:v1 \
  --project gen-lang-client-0540105794

# 6. Deploy
gcloud run deploy employee-bq-mcp \
  --image us-central1-docker.pkg.dev/gen-lang-client-0540105794/mcp-servers/employee-bq-mcp:v1 \
  --region us-central1 \
  --service-account employee-bq-mcp@gen-lang-client-0540105794.iam.gserviceaccount.com \
  --set-env-vars GOOGLE_CLOUD_PROJECT=gen-lang-client-0540105794 \
  --project gen-lang-client-0540105794
```

### Use it from the agent

`agent.py` points to the Cloud Run endpoint:

```python
url="https://employee-bq-mcp-681195791124.us-central1.run.app/mcp/bq"
```

```bash
adk web          # pick a027_mcp_bigquery; no local server.py needed
```

Ask *"Who is an AI engineer?"* (Sarah) or *"Add employee 104, Ravi, Cloud Engineering, DevOps Engineer"*, then check BigQuery: rows added through Cloud Run appear in the same table.

### Test without the agent

```bash
curl -X POST "https://employee-bq-mcp-681195791124.us-central1.run.app/mcp/bq" \
  -H "Content-Type: application/json" \
  -H "Accept: application/json, text/event-stream" \
  -d '{"jsonrpc":"2.0","id":1,"method":"tools/call","params":{"name":"get_employee","arguments":{"employee_id":103}}}'
```

Or with the MCP Inspector in the browser: `npx @modelcontextprotocol/inspector`, **Streamable HTTP**, enter the URL above, **Connect**.

### Logs

```bash
gcloud run services logs read employee-bq-mcp --region us-central1 --project gen-lang-client-0540105794 --limit 20
```

`Access Denied: ... bigquery.jobs.create` in the logs means the service account roles from step 3 are missing. `KeyError: 'GOOGLE_CLOUD_PROJECT'` means `--set-env-vars` was left out.

### Public or private

The service is currently **public**: a request without a token returns `HTTP 200`. Because `add_employee` writes to BigQuery, anyone with the URL can add rows. To make it private:

```bash
gcloud run services remove-iam-policy-binding employee-bq-mcp --region us-central1 \
  --project gen-lang-client-0540105794 --member="allUsers" --role="roles/run.invoker"
```

Then run the proxy on port 8002 and set `agent.py` back to `http://localhost:8002/mcp/bq`. The proxy adds your login token, so the agent works without code changes:

```bash
gcloud run services proxy employee-bq-mcp --region us-central1 --port 8002 --project gen-lang-client-0540105794
```

If the service was deployed with `--no-invoker-iam-check`, redeploy it with `--invoker-iam-check` instead.

### Update after a code change

```bash
gcloud builds submit --tag us-central1-docker.pkg.dev/gen-lang-client-0540105794/mcp-servers/employee-bq-mcp:v2 --project gen-lang-client-0540105794
gcloud run deploy employee-bq-mcp --image us-central1-docker.pkg.dev/gen-lang-client-0540105794/mcp-servers/employee-bq-mcp:v2 --region us-central1 --project gen-lang-client-0540105794
```

## Cleanup

Remove the Cloud Run deployment:

```bash
gcloud run services delete employee-bq-mcp --region us-central1 --project gen-lang-client-0540105794
gcloud artifacts repositories delete mcp-servers --location us-central1 --project gen-lang-client-0540105794
gcloud iam service-accounts delete employee-bq-mcp@gen-lang-client-0540105794.iam.gserviceaccount.com --project gen-lang-client-0540105794
```

Delete the dataset and table:

```bash
bq rm -r -f gen-lang-client-0540105794:employee_mcp
```

This doesn't touch a005's `hr_data` dataset.
