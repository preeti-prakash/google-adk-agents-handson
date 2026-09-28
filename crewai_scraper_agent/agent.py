# crewai_scraper_agent: ADK agent that uses a built-in CrewAI tool
# (ScrapeWebsiteTool) to read web pages and answer questions about them.
#
# - Model access: Gemini on Vertex AI (Agent Platform) with gcloud ADC, same setup
#   as vertex_agent. Copy .env.example to .env and set your project.
# - Tool: CrewAI's ScrapeWebsiteTool, wrapped for ADK with CrewaiTool.
#   ADK can use any CrewAI tool this way.
# - CrewAI needs Python < 3.14, so this agent runs from its own venv:
#     uv venv .venv-crewai --python 3.13
#     uv pip install --python .venv-crewai/bin/python "google-adk==2.8.0" crewai-tools
# - Run locally: .venv-crewai/bin/adk web (http://localhost:8000),
#   then pick crewai_scraper_agent.

from crewai_tools import ScrapeWebsiteTool
from google.adk.agents.llm_agent import Agent
from google.adk.integrations.crewai import CrewaiTool
from google.adk.models import Gemini
from google.genai import types

# Wrap the CrewAI tool so the ADK agent can call it. ADK needs a
# function-style name (no spaces), so give it one explicitly.
scrape_website_tool = CrewaiTool(
    tool=ScrapeWebsiteTool(),
    name='scrape_website',
    description=(
        'Reads a web page and returns its text content. '
        'Input: website_url, the full URL of the page (https://...).'
    ),
)

root_agent = Agent(
    # Retry with backoff on 429 (rate limit) and 503 (model overloaded).
    model=Gemini(
        model='gemini-3.5-flash',
        retry_options=types.HttpRetryOptions(
            attempts=5,
            initial_delay=2,
            max_delay=30,
            http_status_codes=[429, 503],
        ),
    ),
    name='crewai_scraper_agent',
    description='An assistant that reads web pages and summarizes or answers questions about them.',
    instruction="""
You are a web research assistant. When the user gives you a URL, or asks about
the content of a specific web page, use the scrape_website tool to read it
before answering. Always pass the full URL, including https://.

Base your answer only on the scraped content. Reply in a friendly,
conversational way: summarize the main points, pull out the details the user
asked for, and mention which page the information came from.

If the page can't be read (blocked, empty or needs a login), say so honestly
and suggest trying another URL. If the user doesn't give a URL, ask for one.
""",
    tools=[scrape_website_tool],
)
