# ADK Fundamentals: Setup, Local Testing and Deployment

Hands-on examples for Google's **Agent Development Kit (ADK)**, numbered in the order they were built. They start with connecting to Gemini and deploying, then cover tools, multi-agent and workflow agents, schemas and model settings, sessions, memory, artifacts, callbacks, and local models with Ollama.

| # | Folder | What it shows | How to run | Section |
|---|---|---|---|---|
| 1 | `a001_basic_agent/` | Simplest agent, **AI Studio API key** | `adk web` | [1](#1-a001_basic_agent-api-key-ai-studio) |
| 2 | `a002_vertex_agent/` | **gcloud login (ADC)** → Vertex AI; deploy to Cloud Run / Agent Engine | `adk web` | [2](#2-a002_vertex_agent-gcloud-adc-with-vertex-ai--agent-platform) |
| 3 | `a003_my-first-agent/` | Full project from the **Agent Starter Pack** | `make playground` | [3](#3-a003_my-first-agent-agent-starter-pack) |
| 4 | `a004_news_agent_with_tools/` | Built-in **`google_search`** tool | `adk web` | [4](#4-a004_news_agent_with_tools-google-search-tool) |
| 5 | `a005_bigquery_agent/` | ADK **BigQuery toolset** (read-only HR data) | `adk web` | [5](#5-a005_bigquery_agent-bigquery-tools-hr-chatbot) |
| 6 | `a006_wikipedia_agent/` | **LangChain** tool (Wikipedia) | `adk web` | [6](#6-a006_wikipedia_agent-langchain-tool) |
| 7 | `a007_crewai_scraper_agent/` | **CrewAI** tool (web scraper), own venv | `.venv-crewai/bin/adk web` | [7](#7-a007_crewai_scraper_agent-crewai-tool) |
| 8 | `a008_employee-helpdesk/` | **Multi-agent**: root transfers to IT / HR / Finance | `adk web` | [8](#8-a008_employee-helpdesk-multi-agent) |
| 9 | `a009_workflow_agents/` | **Workflow agents**: sequential, parallel, loop, graph, dynamic, collaborative | `adk web` | [9](#9-a009_workflow_agents-workflow-agents) |
| 10 | `a010_DataSchema/` | **`input_schema` / `output_schema`** (structured JSON) | `adk web` | [10](#10-a010_dataschema-input-and-output-schemas) |
| 11 | `a011_AgentConfig/` | **Model settings**: temperature, max tokens, thinking | `adk web` | [11](#11-a011_agentconfig-model-settings) |
| 12 | `a012_vertexSearch/` | **Vertex AI Search** over your own documents (RAG) | `adk web` | [12](#12-a012_vertexsearch-vertex-ai-search-rag) |
| 13–16 | `a013_runner_session/` … `a016_vertex_session/` | **Runner and sessions**: in-memory, database, Vertex AI | `python main.py` | [13](#13-runner-and-sessions-a013a016) |
| 17–18 | `a017_memory_service/`, `a018_memory_bank/` | **Long-term memory** across sessions | `python main.py` | [14](#14-memory-a017a018) |
| 19–20 | `a019_artifact/`, `a020_dynamic_report/` | **Artifacts**: saving files, with versions | `adk web` | [15](#15-artifacts-a019a020) |
| 21 | `a021_callbacks/` | **Callbacks**: logging, a guardrail, changing tool results | `adk web` | [16](#16-a021_callbacks-callbacks) |
| 22–24 | `a022_ollama_chat/` … `a024_ollama_agent/` | **Local models with Ollama**, and an ADK agent on Ollama via **LiteLLM** | `python main.py` / `adk web` | [17](#17-local-models-with-ollama-a022a024) |

> Note: Google renamed **Vertex AI** to **Agent Platform** in the Console. The API ID is still `aiplatform.googleapis.com`, and the code and environment variables still use the old "Vertex" names.

> **Folder names start with a letter** (`a001_`, `a002_`, …). ADK needs agent folder names to be valid Python identifiers, so a name like `001_basic_agent` would fail with a 404 when you send a message.

### Running agents with `adk web`

Run everything from the `adk-fundamentals` folder with the venv active:

```bash
source .venv/bin/activate
adk web          # http://localhost:8000, then pick the agent from the dropdown
```

The dropdown lists every agent, including nested ones like `a009_workflow_agents.sequential_agent` and `a008_employee-helpdesk.employee_helpdesk`. `adk web` reads each agent's `.env` only at startup, so restart it after changing one.

The folders with a `main.py` (a013–a018, a022, a023) are plain Python scripts, not `adk web` agents. Run them with `python <folder>/main.py`.

Most agents use the same Vertex AI `.env` as `a002_vertex_agent` (section 2). Copy it with `cp <folder>/.env.example <folder>/.env` and set `GOOGLE_CLOUD_PROJECT`. **Never commit `.env` files**; `.gitignore` already excludes them.

---

## Prerequisites

```bash
# Python virtual environment with ADK installed
python -m venv .venv
source .venv/bin/activate
pip install google-adk

# uv (needed for uvx and the Agent Starter Pack)
brew install uv

# Google Cloud CLI (gcloud)
brew install --cask google-cloud-sdk
```

Check the installs:

```bash
adk --version
uvx --version
gcloud --version
```

Extra packages some folders need (all in `.venv`):

| Package | Needed by |
|---|---|
| `google-adk[gcp]` | a005 (BigQuery) |
| `langchain-community wikipedia` | a006 (Wikipedia) |
| `greenlet` | a015 (`DatabaseSessionService` with async SQLAlchemy) |
| `ollama` | a022 |
| `litellm` | a024 (non-Gemini models in ADK) |
| [Ollama app](https://ollama.com) + `ollama pull llama3.2` / `ollama pull gemma3` | a022–a024 |

a007 (CrewAI) needs Python < 3.14, so it uses a separate venv; see section 7.

> **If you move or rename this folder,** recreate the venvs. A venv stores its absolute path, so after a rename `adk` fails with `command not found` or `bad interpreter`. Save the package list with `.venv/bin/python -m pip freeze > reqs.txt`, delete `.venv`, run `python -m venv .venv`, then `pip install -r reqs.txt`.

---

## 1. `a001_basic_agent`: API key (AI Studio)

This is the simplest setup. The agent calls the **Gemini API** with an API key and doesn't need a gcloud login.

### 1.1 Create the API key

1. Open **https://aistudio.google.com/apikey** in an incognito window, signed in with **one personal Gmail account**.
   - A work or Workspace account may be blocked by the organization. That shows up as "permission denied" when AI Studio lists or creates projects.
2. Click **Create API key**, then **Create API key in new project**.
3. Copy the key. A standard AI Studio key starts with `AIza`.

### 1.2 Set the `.env`

`a001_basic_agent/.env`:

```
GOOGLE_GENAI_USE_VERTEXAI=FALSE
GOOGLE_API_KEY=AIza...your_key...
```

Never commit this file.

### 1.3 Run it

Run from the `adk-fundamentals` folder:

```bash
adk run a001_basic_agent      # chat in the terminal
adk web                  # browser UI at http://localhost:8000, then pick a001_basic_agent
```

Restart `adk web` / `adk run` after every `.env` change, because the file is only read at startup.

### 1.4 Errors we hit and what they mean

| Error | Meaning | Fix |
|---|---|---|
| `403 API_KEY_SERVICE_BLOCKED` | The key has API restrictions that don't include the Gemini API. Common with keys created in Cloud Console, often starting with `AQ.`. | Create the key in AI Studio, or in **Credentials → key → API restrictions**, allow **Generative Language API** or choose **Don't restrict key**. |
| `403 SERVICE_DISABLED` | The Gemini API is turned off in that project. | Open the link in the error while signed in as the project owner and click **Enable**. |
| `402 RESOURCE_EXHAUSTED`: prepayment credits depleted | The project has **billing linked** (for example the Cloud free trial), so it's on the paid or prepaid tier with a $0 balance. | Use a project with **no billing linked** (free tier), or add prepaid credit in AI Studio. |
| `503 UNAVAILABLE`: high demand | Google's servers for that model are overloaded. The key works. | Retry later, or use another model (for example `gemini-2.5-flash`). |
| `429` | Free-tier rate limit reached. | Wait and retry. |

---

## 2. `a002_vertex_agent`: gcloud ADC with Vertex AI / Agent Platform

This agent has **no API key**. It signs in with your **gcloud login** (Application Default Credentials, ADC) and calls Gemini through **Vertex AI / Agent Platform** in your Google Cloud project. Usage is billed to the project, and Cloud free-trial credit applies.

### 2.1 Set the `.env`

`a002_vertex_agent/.env`:

```
GOOGLE_GENAI_USE_ENTERPRISE=1
GOOGLE_CLOUD_PROJECT=YOUR_PROJECT_ID
GOOGLE_CLOUD_LOCATION=global
```

- `GOOGLE_CLOUD_LOCATION=global` is needed for newer models such as `gemini-3.5-flash`, which may not be offered in a specific region.

### 2.2 Set up gcloud and ADC

```bash
# 1. Log in to the gcloud CLI
gcloud auth login

# 2. Make your own project the default
gcloud config set project YOUR_PROJECT_ID

# 3. Log in for application code (this is what Python / ADK uses)
gcloud auth application-default login

# 4. Charge API usage to your project
gcloud auth application-default set-quota-project YOUR_PROJECT_ID

# 5. Turn on Vertex AI / Agent Platform in the project
gcloud services enable aiplatform.googleapis.com
```

What each step does:

- **`gcloud auth login`** logs in the `gcloud` command-line tool only.
- **`gcloud config set project`** sets the default project for gcloud and for ADC.
- **`gcloud auth application-default login`** saves credentials that **Python code** can use. It's separate from `gcloud auth login`.
- **`set-quota-project`** says which project usage is billed and counted against.
- **`services enable aiplatform.googleapis.com`** turns on the API (shown as **Agent Platform API** in the Console). APIs are off by default in new projects.

The project must have **billing linked**, because Vertex AI requires it.

Check the setup:

```bash
gcloud config list                                   # account + project
gcloud services list --enabled | grep aiplatform     # API enabled?
```

### 2.3 Test locally in the browser

Run from the `adk-fundamentals` folder:

```bash
adk web
```

Open **http://localhost:8000**, choose **a002_vertex_agent** from the dropdown, and chat. The web UI also shows events, tool calls and session state, which helps with debugging.

For a terminal-only test: `adk run a002_vertex_agent`.

### 2.4 Deploy to Cloud Run with `adk`

Steps 1 and 2 are **one-time setup per project**.

**Step 1: enable the APIs**

```bash
gcloud services enable run.googleapis.com cloudbuild.googleapis.com \
  artifactregistry.googleapis.com aiplatform.googleapis.com \
  --project=YOUR_PROJECT_ID
```

**Step 2: grant the service account its permissions**

The build and the running service use the **default compute service account** (`PROJECT_NUMBER-compute@developer.gserviceaccount.com`), not your user account. New projects don't give it these permissions automatically.

```bash
# Get the project number
gcloud projects describe YOUR_PROJECT_ID --format="value(projectNumber)"
# -> PROJECT_NUMBER

# Allow it to build the container (read source from Cloud Storage, push to Artifact Registry, write logs)
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/run.builder"

# Allow the running service to call Gemini
gcloud projects add-iam-policy-binding YOUR_PROJECT_ID \
  --member="serviceAccount:PROJECT_NUMBER-compute@developer.gserviceaccount.com" \
  --role="roles/aiplatform.user"
```

**Step 3: deploy.** Run from the `adk-fundamentals` folder:

```bash
adk deploy cloud_run \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --service_name=vertex-agent \
  --with_ui \
  a002_vertex_agent \
  -- --set-env-vars=GOOGLE_CLOUD_LOCATION=global
```

- `--with_ui` also deploys the ADK web UI. Use it for testing only, not in production.
- Everything after `--` goes to `gcloud run deploy`.
- `--set-env-vars=GOOGLE_CLOUD_LOCATION=global` makes Gemini calls go to `global` while the service runs in `us-central1`. Without it you get `404 model not found`.
- If asked **"Allow unauthenticated invocations?"**, answer **N** to keep the service private.
- You don't need a Dockerfile. `adk` generates one in a temporary folder. To see it, add `--temp_folder=./cr_build`.

What happens during a deploy:

```
laptop --zip--> Cloud Storage --> Cloud Build (builds image) --> Artifact Registry --> Cloud Run
```

**Step 4: test the deployed service**

```bash
gcloud run services proxy vertex-agent --region us-central1 --project YOUR_PROJECT_ID
```

Open **http://localhost:8080**.

View it in the Console under **☰ Menu → Cloud Run → vertex-agent**, which has revisions, logs, metrics and the service account.

**Update:** run Step 3 again. Cloud Run creates a new revision, and old revisions stay available for rollback.

**Delete** when you're done:

```bash
gcloud run services delete vertex-agent --region us-central1 --project YOUR_PROJECT_ID
```

### 2.5 Deploy to Agent Engine with `adk` (alternative)

```bash
adk deploy agent_engine \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --display_name=vertex-agent \
  a002_vertex_agent
```

- Agent Engine needs a real region, not `global`.
- To update an existing instance, add `--agent_engine_id=<ID>`. Without it, each run creates a **new** billable instance.
- View and delete it in the Console: **Agent Platform → Agent Engine**.

### 2.6 Errors we hit and what they mean

| Error | Meaning | Fix |
|---|---|---|
| `403 aiplatform.endpoints.predict denied` | gcloud or ADC pointed to a project you don't have access to (a company project). | Run `gcloud config set project <your project>` and `set-quota-project`, as in section 2.2. |
| `PERMISSION_DENIED: Build failed ... default service account is missing required IAM permissions` | The Cloud Build service account can't read the uploaded source. | Grant `roles/run.builder`, as in step 2 of 2.4. |
| `404 Publisher model ... locations/us-central1 ... gemini-3.5-flash not found` | The model isn't offered in `us-central1`. | Set `GOOGLE_CLOUD_LOCATION=global` on the service, or use a model available in that region. |

Fix the location on a running service without redeploying:

```bash
gcloud run services update vertex-agent --region us-central1 --project YOUR_PROJECT_ID \
  --update-env-vars GOOGLE_CLOUD_LOCATION=global
```

---

## 3. `a003_my-first-agent`: Agent Starter Pack

The **Agent Starter Pack** generates a **complete project** around the agent: code, a Makefile, tests, evals, a deploy script, logging and feedback. It can also add CI/CD and Terraform. It's already set up for deployment. It doesn't deploy anything until you run `make deploy`.

### 3.1 Create the project

Run from the parent folder where the new project should go:

```bash
uvx agent-starter-pack create
```

It asks for a project name, a template and a **deployment target** (Agent Engine or Cloud Run).

To add the Starter Pack setup to an **existing** agent (back it up or commit it first):

```bash
cd a002_vertex_agent
uvx agent-starter-pack enhance
```

### 3.2 What it creates

| File / folder | Purpose |
|---|---|
| `app/agent.py` | The agent. It uses ADC and Vertex AI and sets the project from `google.auth.default()`. |
| `app/agent_engine_app.py` | Wraps the agent for Agent Engine, with logging and feedback. |
| `Makefile` | Shortcuts: `install`, `playground`, `test`, `eval`, `lint`, `deploy`. |
| `tests/` | Unit, integration and eval tests. |
| `pyproject.toml`, `uv.lock` | Dependencies with pinned versions. |
| `deployment_metadata.json` | Filled in with the Agent Engine ID after a deploy. |

The project comes from **gcloud / ADC**, so complete section 2.2 first.

### 3.3 Test locally

```bash
cd a003_my-first-agent
make install        # install dependencies with uv
make playground     # ADK web UI at http://localhost:8501, then select the "app" folder
make test           # unit + integration tests
make eval           # score the agent against eval sets
```

### 3.4 Deploy to Agent Engine

When the project was created with the **Agent Engine** target (as `my-first-agent` was):

```bash
make deploy
```

This packages `./app`, exports the requirements, and creates or updates the Agent Engine instance. Afterwards, `deployment_metadata.json` contains the `remote_agent_engine_id`.

View, test and delete it in the Console under **Agent Platform → Agent Engine**.

### 3.5 Deploy to Cloud Run

Create the project with **Cloud Run** as the deployment target:

```bash
uvx agent-starter-pack create my-cloudrun-agent -d cloud_run
cd my-cloudrun-agent
make install
make playground     # test locally
make deploy         # build + deploy to Cloud Run
```

The Cloud Run permissions from section 2.4 (APIs, `roles/run.builder`, `roles/aiplatform.user`) apply here too.

---

## 4. `a004_news_agent_with_tools`: Google Search tool

A news assistant that uses Gemini's built-in **`google_search`** tool. Gemini runs the search itself and bases its answer on the results, so it can answer questions about current events.

### 4.1 Setup

It uses the same Vertex AI + ADC setup as `a002_vertex_agent` (section 2.2).

```bash
cp a004_news_agent_with_tools/.env.example a004_news_agent_with_tools/.env
# then set GOOGLE_CLOUD_PROJECT in the new .env
```

### 4.2 How it's built

```python
from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-3.5-flash',
    name='news_agent',
    instruction='...use google_search, summarize key points, mention dates, list sources...',
    tools=[google_search],
)
```

### 4.3 Run and test

```bash
adk web      # http://localhost:8000, then pick a004_news_agent_with_tools
```

Try: *"What are today's top tech news headlines?"*

### 4.4 Things to know

- **`google_search` must be the agent's only tool.** Gemini won't accept it alongside your own function tools in the same agent. If you need both, put the search in a separate sub-agent or wrap it with `AgentTool`.
- Google Search grounding may be **billed separately** from normal model usage.

---

## 5. `a005_bigquery_agent`: BigQuery tools (HR chatbot)

An HR assistant that answers questions about employees and their leaves. It uses ADK's **BigQuery toolset** to find tables, read their schemas and run SQL, then replies in plain, conversational language.

### 5.1 Data model

Dataset **`hr_data`**, with two tables that share `emp_id` (**no foreign key**; the agent joins them on `emp_id`):

| Table | Columns | Rows |
|---|---|---|
| `employee_info` | `emp_id` (emp1–emp10), `emp_name`, `designation`, `salary` | 10 |
| `employee_leaves` | `emp_id`, `leave_date` | 15 (emp8 and emp10 have no leaves) |

### 5.2 Setup

```bash
# 1. Install the BigQuery / Dataplex client libraries for ADK
pip install "google-adk[gcp]"

# 2. Set the project
cp a005_bigquery_agent/.env.example a005_bigquery_agent/.env
# then set GOOGLE_CLOUD_PROJECT in the new .env

# 3. Enable BigQuery (once per project)
gcloud services enable bigquery.googleapis.com --project=YOUR_PROJECT_ID

# 4. Create the dataset, tables and sample rows
bq query --project_id=YOUR_PROJECT_ID --use_legacy_sql=false < a005_bigquery_agent/setup_hr_data.sql
```

You can also paste `setup_hr_data.sql` into **BigQuery Studio** in the Console instead of step 4.

If `pip install` upgrades `opentelemetry-api` past the version ADK allows, pin it back: `pip install "opentelemetry-api==1.42.1"`. Then check with `pip check`.

### 5.3 How it's built

- **Tools** (from `google.adk.integrations.bigquery`): `list_dataset_ids`, `get_dataset_info`, `list_table_ids`, `get_table_info`, `execute_sql`.
- **Credentials:** the same gcloud ADC login is used for BigQuery (`google.auth.default()`).
- **Read-only:** `BigQueryToolConfig(write_mode=WriteMode.BLOCKED)`, so the agent can't insert, update or delete.
- **Retries:** the model is wrapped in `Gemini(..., retry_options=HttpRetryOptions(...))` to retry on **429** and **503**.
- **Response style:** friendly, conversational answers. The SQL is shown **only when the user asks for it**.

### 5.4 Run and test

```bash
adk web      # http://localhost:8000, then pick a005_bigquery_agent
```

Try:
- *"How many employees do we have?"*
- *"Who has the highest salary?"*
- *"Which employees haven't taken any leave?"*
- *"How many leaves has each employee taken?"*
- *"What query did you use for that?"* (shows the SQL)

### 5.5 Errors we hit and what they mean

| Error | Meaning | Fix |
|---|---|---|
| `ModuleNotFoundError: google.cloud` / `cannot import name 'dataplex_v1'` | The BigQuery client libraries aren't installed. | `pip install "google-adk[gcp]"` |
| `429 RESOURCE_EXHAUSTED` | Rate limit. Each question makes several Gemini calls, and newer models run on shared capacity. | Retries are already built in. Otherwise wait a minute, or use `gemini-2.5-flash`. |

---

## 6. `a006_wikipedia_agent`: LangChain tool

Answers factual questions by looking them up on Wikipedia. The tool is LangChain's `WikipediaQueryRun`, wrapped with ADK's **`LangchainTool`**. Any LangChain tool can be used this way.

```python
from google.adk.integrations.langchain import LangchainTool
from langchain_community.tools import WikipediaQueryRun

wikipedia_tool = LangchainTool(tool=WikipediaQueryRun(api_wrapper=...))
root_agent = Agent(..., tools=[wikipedia_tool])
```

**Setup:** `pip install langchain-community wikipedia`, then the Vertex AI `.env`.

**Run:** `adk web`, pick `a006_wikipedia_agent`.

Try: *"Who was Alan Turing?"*, *"Tell me about the Eiffel Tower"*

The code sets its own Wikipedia User-Agent, because Wikipedia rate-limits (`429`) the `wikipedia` package's shared default one.

---

## 7. `a007_crewai_scraper_agent`: CrewAI tool

Reads a web page and answers questions about it. The tool is CrewAI's `ScrapeWebsiteTool`, wrapped with ADK's **`CrewaiTool`**.

**Setup:** CrewAI needs Python < 3.14, so this agent has its own venv:

```bash
uv venv .venv-crewai --python 3.13
uv pip install --python .venv-crewai/bin/python "google-adk==2.8.0" crewai-tools
```

**Run:** `.venv-crewai/bin/adk web`, pick `a007_crewai_scraper_agent`.

Try: *"Summarize https://adk.dev"*

> If the folder was renamed after `.venv-crewai` was created, the venv is broken (it points to the old path). Delete it and run the two setup commands again.

---

## 8. `a008_employee-helpdesk`: Multi-agent

A root agent reads each request and **transfers** it to an IT, HR or Finance specialist, each with its own mock tools. ADK gives the root a `transfer_to_agent` tool automatically because it has `sub_agents`, and Gemini picks the specialist from each sub-agent's `description`.

**Run:** `adk web`, pick `a008_employee-helpdesk.employee_helpdesk`. The **Events** panel shows each transfer.

Try: *"My VPN is not working"*, *"I spent $250 on a hotel. How much can I claim?"*

Full details, mock data and deployment: [a008_employee-helpdesk/README.md](a008_employee-helpdesk/README.md).

---

## 9. `a009_workflow_agents`: Workflow agents

Six agents that run steps in a set structure instead of leaving every decision to the LLM. They use the ADK 2.0 `Workflow` API; the older `SequentialAgent` / `ParallelAgent` / `LoopAgent` versions are kept as comments.

| Agent | Pattern | Example |
|---|---|---|
| `sequential_agent` | Steps in order | Support ticket triage: analyze → reply → create ticket |
| `parallel_agent` | Steps at the same time, then join | Trip planner: weather + attractions + food → plan |
| `loop_agent` | Repeat until a condition is met | News summarizer that shortens until under a word limit |
| `graph_agent` | Graph with branches and joins | Product catalog onboarding |
| `dynamic_agent` | Steps chosen at runtime | Product catalog, dynamic version |
| `collaborative_agent` | Coordinator working with helper agents | Party planner |

**Run:** `adk web`, pick `a009_workflow_agents.<agent>` (for example `a009_workflow_agents.sequential_agent`). `graph_agent` also needs `pip install -r a009_workflow_agents/graph_agent/requirements.txt`.

Prompts and explanations: [a009_workflow_agents/README.md](a009_workflow_agents/README.md) and the README in each sub-folder.

---

## 10. `a010_DataSchema`: Input and output schemas

A product classifier with Pydantic schemas for both input and output:

```python
class ProductInput(BaseModel):
    product_name: str
    description: str

class ProductOutput(BaseModel):
    category: str
    summary: str

root_agent = LlmAgent(..., input_schema=ProductInput, output_schema=ProductOutput)
```

- **`input_schema`:** the message must be JSON with these fields. Plain text fails validation.
- **`output_schema`:** the reply is JSON with these fields, so other code can use it directly.

**Run:** `adk web`, pick `a010_DataSchema`, and send JSON:

```json
{"product_name": "AirPods Pro", "description": "Wireless noise-cancelling earbuds with spatial audio"}
```

Reply: `{"category": "Wireless Earbuds", "summary": "Premium wireless earbuds featuring active noise cancellation..."}`

To see the schema enforced, leave out `description`.

---

## 11. `a011_AgentConfig`: Model settings

A product-description writer that sets the model's generation options:

```python
generate_content_config=types.GenerateContentConfig(
    temperature=0.8,                      # more creative wording
    max_output_tokens=600,                # cap on reply length
    thinking_config=types.ThinkingConfig(thinking_budget=0),
)
```

- These settings go **inside `generate_content_config`**. Passing `temperature=` directly to `LlmAgent` raises `Extra inputs are not permitted`.
- Gemini 2.5's **thinking tokens count toward `max_output_tokens`**. With a low limit and thinking on, replies get cut off after a few words (`finish_reason: MAX_TOKENS`). `thinking_budget=0` turns thinking off so the whole limit goes to the answer.

**Run:** `adk web`, pick `a011_AgentConfig`, and type a product name such as *"Wireless ergonomic mouse"*. Send the same name twice to see `temperature` change the wording.

---

## 12. `a012_vertexSearch`: Vertex AI Search (RAG)

An employee onboarding assistant that answers only from your own documents, using **`VertexAiSearchTool`** connected to a Vertex AI Search data store.

**Setup:**
1. In the Console, go to **AI Applications → Data Stores**, create a data store and import your documents (PDFs, Word files and so on). Wait until the import finishes (green tick); it can take 10–30 minutes.
2. `.env`: the Vertex AI settings plus
   ```
   VERTEX_SEARCH_DATASTORE_ID=your-datastore-id
   ```

**Run:** `adk web`, pick `a012_vertexSearch`.

Try: *"What should I do on my first day?"*, *"What documents do I need for onboarding?"*, and something not in the documents (*"What is the company's stock price?"*) to check that it says the information wasn't found.

**How retrieval works:** Gemini rewrites your question into search queries. Vertex AI Search runs them as **hybrid search** (keywords plus semantic, using embeddings it creates and manages for you) and returns matching passages, which Gemini uses to answer. You don't manage chunking or embeddings yourself.

**Empty replies** usually mean the data store has no documents yet (the import is still running or failed).

---

## 13. Runner and sessions (a013–a016)

These are **plain Python scripts** (`main.py`). Your code creates the `Runner` and the session service, which `adk web` normally does for you. Each script loads its folder's `.env` with `load_dotenv()`.

| Folder | Session service | Survives a restart? |
|---|---|---|
| `a013_runner_session` | `InMemorySessionService`, one fixed message | No |
| `a014_conversation_loop` | `InMemorySessionService`, chat loop | No |
| `a015_database_session` | `DatabaseSessionService` (SQLite file) | ✅ Yes |
| `a016_vertex_session` | `VertexAiSessionService` (Agent Engine) | ✅ Yes |

### Key ideas

- **Runner:** runs the agent for one message: `runner.run_async(user_id=..., session_id=..., new_message=...)`. The scripts that use a database or Vertex AI call `run_async`, because those services are async.
- **Session:** one conversation, found by `app_name` + `user_id` + `session_id`. Every message and reply is saved to it as an **event**.
- **The app decides when the conversation ends.** Typing `exit` only stops the script; the session stays stored until something deletes it.
- **To resume a conversation, reuse its session ID.** a015 always uses the fixed ID `session_001`, so every run continues the same conversation. a016 gets a new random ID each run unless you pass an old one. Both services work the same way; only the ID handling in the scripts differs.
- A **new session ID starts empty**, with any service. Remembering a user across different sessions needs memory (section 14).

### a013 and a014: in-memory

```bash
python a013_runner_session/main.py         # one message, one reply
python a014_conversation_loop/main.py      # chat; type exit to stop
```

In a014, try telling it your name, saying *"Thanks!"* (it keeps going), asking *"What is my name?"* (it remembers within the run), then `exit`. Run it again and it has forgotten.

### a015: database sessions

```python
session_service = DatabaseSessionService(db_url=f"sqlite+aiosqlite:///{DB_PATH}")
```

Needs `pip install greenlet`.

```bash
python a015_database_session/main.py
```

Chat, `exit`, run it again: it prints `Resumed session session_001 with N saved events.` and remembers. Ctrl+C is fine too, because each message is saved as it's sent.

Look inside the database (`sessions.db`, next to `main.py`):

```bash
sqlite3 a015_database_session/sessions.db "SELECT * FROM sessions;"
sqlite3 -header -column a015_database_session/sessions.db \
  "SELECT json_extract(event_data,'\$.author') AS author,
          substr(json_extract(event_data,'\$.content.parts[0].text'),1,80) AS text
   FROM events ORDER BY timestamp;"
```

Delete `sessions.db` to start fresh.

### a016: Vertex AI sessions

Sessions are stored in an **Agent Engine** instance in Google Cloud. Create a sessions-only instance (no agent code; usage is billed):

```bash
python -c "import vertexai; ae = vertexai.Client(project='YOUR_PROJECT_ID', location='us-central1').agent_engines.create(config={'display_name': 'employee-assistant-sessions'}); print(ae.api_resource.name)"
```

Put the number at the end of the printed name into `a016_vertex_session/.env`:

```
AGENT_ENGINE_LOCATION=us-central1
AGENT_ENGINE_ID=1234567890123456789
```

```bash
python a016_vertex_session/main.py                 # new session, prints its ID
python a016_vertex_session/main.py <SESSION_ID>    # resume that session
```

Test: tell it about yourself and `exit`; resume with the ID and ask *"What do you know about me?"* (it remembers); then run without an ID and ask again (it doesn't). Sessions are visible in the Console under **Agent Engine → your instance → Sessions**.

---

## 14. Memory (a017–a018)

Sessions remember one conversation. **Memory** stores facts about a **user** that any later session can search.

| | Session | Memory |
|---|---|---|
| Stores | The full conversation | Facts, e.g. "Preeti works in Cloud Engineering" |
| Scope | One session ID | One user, across all their sessions |
| Filled by | The Runner, automatically | Your code: `add_session_to_memory` / `add_events_to_memory` |
| Read by | Loaded when you resume the session | `search_memory`, or the agent's `load_memory` tool |

Both scripts tell the agent something in Session 1, save Session 1 to memory, then find it from a new, empty Session 2.

> **Re-fetch the session before saving it to memory.** The object returned by `create_session()` is a snapshot from before the conversation and has no events. Call `get_session()` first, or you save an empty session.

### a017: `InMemoryMemoryService`

```bash
python a017_memory_service/main.py
```

```
--- SESSION 1 ---
Agent: It's nice to meet you, Preeti! ...
Session 1 added to memory.
--- SESSION 2 ---
Agent: You work in the Cloud Engineering team.
```

The agent finds the fact with the `load_memory` tool. It's local and free, but memory is lost when the script ends, and search only matches **words**, not meaning.

### a018: Vertex AI Memory Bank

`VertexAiMemoryBankService` stores memories in an Agent Engine instance and uses Gemini to **extract facts** from conversations and find them **by meaning**.

**Setup:** create an Agent Engine instance (same command as a016, for example with `display_name: 'employee-memory-bank'`) and set `AGENT_ENGINE_LOCATION` and `AGENT_ENGINE_ID` in `a018_memory_bank/.env`.

```bash
python a018_memory_bank/main.py
```

```
Session 1: 1580...
Agent: Hello Preeti, ...
Generating memories (this can take a little while)...
Session added to Vertex AI Memory Bank.
Session 2: 8006...

Memory results:
- My name is Preeti and I work in the Cloud Engineering team.
```

- The script uses `add_events_to_memory(..., custom_metadata={"wait_for_completion": True})`. Memory Bank extracts facts in the background, so without waiting, a search right after saving may come back empty.
- `search_memory` only **looks up** stored facts; it doesn't write an answer. Instructions in the query (like "answer in a certain style") are ignored. For a styled answer, give the agent the `load_memory` tool and ask it in Session 2.
- Only sessions you explicitly add go into memory. Session 2 isn't added.

View the results in the Console under **Agent Engine → your instance → Memory Bank** and **Sessions**.

---

## 15. Artifacts (a019–a020)

**Artifacts** are files an agent saves (reports, images, PDFs), stored per session with **versions**: saving the same filename again creates version 1, 2, … and keeps the old ones.

### a019: save a fixed report

A tool saves a hard-coded sales report:

```python
async def create_report(tool_context: ToolContext):
    await tool_context.save_artifact(filename="sales_report.txt", artifact=types.Part(text=report))
```

`save_artifact` is **async**: the tool must be `async def` and `await` it. Without `await`, nothing is saved, though the agent still says it was.

**Run:** `adk web`, pick `a019_artifact`, ask *"Give me the sales report"*, then open the **Artifacts** tab.

### a020: dynamic reports with versions

Writes reports from your details and keeps every change as a new version. Each save stores a one-line change note in `custom_metadata`.

| Tool | Does |
|---|---|
| `create_report` | Writes a new report and saves it as version 0 |
| `read_report` | Shows the latest version, or a specific one |
| `update_report` | Saves your changes as a new version, with a change note |
| `report_history` | Lists every version with its save time and change note |
| `list_reports` | Lists the session's reports |

**Run:** `adk web`, pick `a020_dynamic_report`, and in one session:

1. *"Create a Q3 sales report: total sales $40,000, 220 orders, top product laptops."* → version 0
2. *"Update the Q3 report: total sales are actually $42,500 and add that returns were 5."* → version 1
3. *"Show the version history of the Q3 report."*
4. *"Show me version 0 of the Q3 report."* → the original
5. *"What reports do I have?"*

Then check the **Artifacts** tab, and click **New Session** to see that artifacts belong to a session.

**Where `adk web` stores them:** `<agent folder>/.adk/artifacts/apps/<app>/users/<user>/sessions/<session>/artifacts/<filename>/versions/<n>/` (git-ignored).

---

## 16. `a021_callbacks`: Callbacks

Callbacks are your own functions that ADK runs at fixed points. They can **watch**, **block** or **change** what the agent does, without changing its instruction or tools.

```
before_agent → before_model → [Gemini] → after_model
                                  └─ tool call → before_tool → [tool] → after_tool → back to before_model
→ after_agent
```

- **Return `None`:** ADK carries on as normal.
- **Return a value:** ADK uses it and skips or replaces the normal step.

In this HR leave assistant:

| Callback | Does here |
|---|---|
| `before_agent` / `after_agent` | Log start and finish |
| `before_model` | **Guardrail**: messages containing "password" or "salary of" get a fixed refusal, and Gemini is never called |
| `after_model` | Logs whether Gemini asked for a tool or replied with text |
| `before_tool` | Logs the tool name and arguments |
| `after_tool` | **Changes the result**: adds "Suggest talking to HR" when leave days are 0 |

**Run:** `adk web`, pick `a021_callbacks`, and **watch the terminal** where `adk web` runs, where each callback prints a line like `[1 before_agent] ...`.

| Prompt | Shows |
|---|---|
| *How many leave days does Preeti have?* | All six callbacks, in order |
| *How many leave days does Anita have?* | `after_tool` adds the HR note |
| *What is the salary of Ravi?* | `before_model` blocks it |
| *Hi, what can you do?* | No tool, so no `before_tool` / `after_tool` |

Sample data: Preeti 12 days, Ravi 5, Anita 0.

---

## 17. Local models with Ollama (a022–a024)

[Ollama](https://ollama.com) runs open models on your own machine: no API key, no cloud, no cost.

```bash
ollama pull llama3.2      # 2 GB, used by a022 and a024
ollama pull gemma3        # 3.3 GB, used by a023
curl http://localhost:11434   # should reply "Ollama is running"
```

### a022: `ollama` Python package

```bash
pip install ollama
python a022_ollama_chat/main.py
```

`llama3.2` is a small 3B model. Asked just *"What is RAG?"*, it may explain the word "rag" instead of Retrieval-Augmented Generation; add context such as *"What is RAG (Retrieval-Augmented Generation) in AI?"*.

### a023: plain HTTP API

The same kind of request without the package, as a `POST` to Ollama's REST API:

```bash
python a023_ollama_http/main.py
```

It prints the full JSON response. For just the answer, use `response.json()["message"]["content"]`. The `ollama` package makes this same HTTP call for you.

### a024: ADK agent on Ollama via LiteLLM

An ADK agent with a tool, running on local `llama3.2` instead of Gemini:

```python
from google.adk.models.lite_llm import LiteLlm

root_agent = LlmAgent(..., model=LiteLlm(model="ollama_chat/llama3.2"), tools=[get_leave_balance])
```

`.env`:

```
OLLAMA_API_BASE=http://localhost:11434
```

**Setup:** `pip install litellm`. **Run:** `adk web`, pick `a024_ollama_agent`.

Try: *"How many leave days does Preeti have?"* (calls the tool → 12 days).

Small local models are reliable at **calling** a tool but not at deciding **when not to**. For greetings or general questions, `llama3.2` may call the tool anyway or reply with tool-call JSON as text. Gemini doesn't have this problem with the same code. A bigger model such as `qwen2.5:7b` or `llama3.1:8b` does much better: `ollama pull qwen2.5:7b`, then `LiteLlm(model="ollama_chat/qwen2.5:7b")`.

---

## 18. Comparison

### Ways to deploy

| | `adk deploy ...` | Starter Pack `make deploy` | Python SDK |
|---|---|---|---|
| Setup | Almost none | Generated for you | You write it |
| Includes | Deployment only | Deploy, tests, evals, logging, CI/CD and Terraform (optional) | Whatever you build |
| Good for | Learning, quick demos | Team and production projects | Custom pipelines |

### Where it runs

| | Agent Engine | Cloud Run |
|---|---|---|
| What you manage | Almost nothing | The container, scaling settings and networking |
| Sessions and memory | Built in | You set them up (default is in-memory, lost on restart) |
| Custom APIs and UI | Limited | Anything in a container |
| Scale to zero | Depends on the setup | Yes |

### How companies usually do it

- Separate **dev / staging / prod** projects.
- Infrastructure defined in **Terraform**.
- **CI/CD** (Cloud Build or GitHub Actions): lint, tests and evals, then deploy to staging, then deploy to prod after approval.
- **Dedicated service accounts** with least-privilege roles. No API keys or personal logins.
- Secrets in **Secret Manager**, not `.env`.
- **Image-based deploys** (build once, push to Artifact Registry, deploy the same image everywhere).
- **Monitoring** with Cloud Logging and Cloud Trace (OpenTelemetry).
- **Network security** with VPC Service Controls and private Cloud Build worker pools.

---

### Session services

| | In-memory | Database | Vertex AI |
|---|---|---|---|
| Class | `InMemorySessionService` | `DatabaseSessionService` | `VertexAiSessionService` |
| Stored in | Python memory | SQLite / Postgres / MySQL / Cloud SQL | Agent Engine (Google Cloud) |
| Survives a restart | No | Yes | Yes |
| Managed by | — | You | Google |
| Works with Memory Bank | No | No | Yes |
| Cost | Free | Free locally | Billed on usage |

The agent code is the same for all three; only the line that creates the session service changes.

---

## 19. Cleanup and cost

Deployed services use billable resources, which draw down the free-trial credit first. Remove them after testing:

```bash
gcloud run services delete vertex-agent --region us-central1 --project YOUR_PROJECT_ID
```

Delete Agent Engine instances (a003, a016, a018) in the Console under **Agent Platform → Agent Engine**, or with Python. `force=True` also deletes the sessions and memories inside:

```bash
python -c "import vertexai; vertexai.Client(project='YOUR_PROJECT_ID', location='us-central1').agent_engines.delete(name='projects/YOUR_PROJECT_ID/locations/us-central1/reasoningEngines/ENGINE_ID', force=True)"
```

Remove the sample BigQuery data:

```bash
bq rm -r -f --project_id=YOUR_PROJECT_ID hr_data
```

Delete the a012 data store in the Console under **AI Applications → Data Stores**.

Free up disk space from local models with `ollama rm gemma3` / `ollama rm llama3.2`.

Check spending under **Cloud Console → Billing**.
