# a004_news_agent_with_tools: ADK agent that uses the built-in google_search tool
# to answer questions about current news.
#
# - Model access: Gemini on Vertex AI (Agent Platform) with gcloud ADC, same setup
#   as a002_vertex_agent. Copy .env.example to .env and set your project.
# - google_search is a Gemini built-in tool: the model runs the search itself and
#   grounds its answer in the results.
# - Run locally: `adk run a004_news_agent_with_tools` or `adk web` (http://localhost:8000).

from google.adk.agents.llm_agent import Agent
from google.adk.tools import google_search

root_agent = Agent(
    model='gemini-3.5-flash',
    name='news_agent',
    description='An assistant that finds and summarizes the latest news using Google Search.',
    instruction=(
        'You are a news assistant. For any question about current events or recent news, '
        'use the google_search tool to find up-to-date information. '
        'Summarize the key points clearly, mention when events happened, '
        'and list the sources you used.'
    ),
    tools=[google_search],
)
