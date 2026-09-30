# a005_bigquery_agent: ADK agent that answers HR questions from BigQuery using the
# built-in BigQuery toolset (list datasets, list tables, inspect schemas, run SQL).
#
# - Model access: Gemini on Vertex AI (Agent Platform) with gcloud ADC, same setup
#   as a002_vertex_agent. Copy .env.example to .env and set your project.
# - BigQuery access: also uses your gcloud ADC login. Enable the API once:
#     gcloud services enable bigquery.googleapis.com
# - Data: dataset `hr_data` with tables `employee_info` and `employee_leaves`,
#   created by setup_hr_data.sql. The tables share emp_id (no foreign key).
# - Read-only: write_mode=BLOCKED, so the agent can only run SELECT queries.
# - Needs: pip install "google-adk[gcp]"
# - Run locally: `adk web` (http://localhost:8000) and pick a005_bigquery_agent.

import os

import google.auth
from google.adk.agents.llm_agent import Agent
from google.adk.integrations.bigquery import BigQueryCredentialsConfig
from google.adk.integrations.bigquery import BigQueryToolset
from google.adk.integrations.bigquery.config import BigQueryToolConfig
from google.adk.integrations.bigquery.config import WriteMode
from google.adk.models import Gemini
from google.genai import types

PROJECT_ID = os.getenv('GOOGLE_CLOUD_PROJECT')
DATASET_ID = 'hr_data'

# Use the same gcloud ADC login for BigQuery that the agent uses for Gemini.
credentials, _ = google.auth.default()

bigquery_toolset = BigQueryToolset(
    credentials_config=BigQueryCredentialsConfig(credentials=credentials),
    bigquery_tool_config=BigQueryToolConfig(write_mode=WriteMode.BLOCKED),
    tool_filter=[
        'list_dataset_ids',
        'get_dataset_info',
        'list_table_ids',
        'get_table_info',
        'execute_sql',
    ],
)

root_agent = Agent(
    # Retry with backoff on 429 (rate limit) and 503 (model overloaded).
    # One question makes several model calls (tool choice, tool results, answer),
    # so shared-quota 429s are common on newer models.
    model=Gemini(
        model='gemini-3.5-flash',
        retry_options=types.HttpRetryOptions(
            attempts=5,
            initial_delay=2,
            max_delay=30,
            http_status_codes=[429, 503],
        ),
    ),
    name='bigquery_agent',
    description='An HR assistant that answers questions about employees and leaves from BigQuery.',
    instruction=f"""
You are an HR data assistant. Answer questions using the BigQuery tools.

Data location:
- Project: {PROJECT_ID}
- Dataset: {DATASET_ID}
- Table `employee_info`: emp_id, emp_name, designation, salary (one row per employee)
- Table `employee_leaves`: emp_id, leave_date (one row per leave day applied)

The two tables have no foreign key, but they use the same emp_id values
(emp1 ... emp10). Join them on emp_id when a question needs both.

How to work:
1. If you are unsure of the tables or columns, use list_table_ids and get_table_info first.
2. Write standard BigQuery SQL with fully qualified names, e.g.
   `{PROJECT_ID}.{DATASET_ID}.employee_info`.
3. Run it with execute_sql, then answer in plain language.
4. Only read data. Never try to insert, update or delete.

How to respond:
- Reply in a friendly, conversational way, like a helpful colleague, in full sentences.
  Avoid rigid "Name: / Employee ID:" field lists; weave the details into the reply.
  Use a short list only when there are several people or items to compare.
- Do NOT show SQL, table names, project IDs or tool details in your answer.
- Only show the SQL you ran if the user explicitly asks for it (for example
  "show me the query" or "what SQL did you use?").
- If nothing matches, say so naturally and mention anything close that might help.
""",
    tools=[bigquery_toolset],
)
