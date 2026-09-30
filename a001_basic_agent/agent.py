# a001_basic_agent: simplest ADK agent, created with `adk create`.
#
# - Model access: Gemini API (AI Studio) using an API key. No gcloud login needed.
# - API key: created at https://aistudio.google.com/apikey
#   (Create API key -> "Create API key in new project"; key starts with "AIza").
# - .env: GOOGLE_GENAI_USE_VERTEXAI=FALSE and GOOGLE_API_KEY=<your key>.
#   Use a project with no billing linked to stay on the free tier.
# - Run locally: `adk run a001_basic_agent` or `adk web` (http://localhost:8000).
# - Not deployed. See the root README.md, section 1.

from google.adk.agents.llm_agent import Agent

root_agent = Agent(
    model='gemini-3.5-flash',
    name='root_agent',
    description='A helpful assistant for user questions.',
    instruction='Answer user questions to the best of your knowledge',
)
