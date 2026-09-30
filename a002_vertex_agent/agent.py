# a002_vertex_agent: ADK agent created with `adk create`, using Google Cloud instead of an API key.
#
# - Model access: Gemini on Vertex AI (shown as "Agent Platform" in the Console).
# - Auth: gcloud Application Default Credentials (ADC), no API key:
#     gcloud auth application-default login
#     gcloud auth application-default set-quota-project <project>
#     gcloud services enable aiplatform.googleapis.com
# - .env: GOOGLE_GENAI_USE_ENTERPRISE=1, GOOGLE_CLOUD_PROJECT=<project>,
#   GOOGLE_CLOUD_LOCATION=global (newer models like gemini-3.5-flash need "global").
# - Run locally: `adk run a002_vertex_agent` or `adk web` (http://localhost:8000).
# - Deployed to Cloud Run with `adk deploy cloud_run` (can also use `adk deploy agent_engine`).
#   See the root README.md, section 2.

from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
