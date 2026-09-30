# a006_wikipedia_agent: ADK agent that uses a built-in LangChain tool (Wikipedia)
# to answer factual questions.
#
# - Model access: Gemini on Vertex AI (Agent Platform) with gcloud ADC, same setup
#   as a002_vertex_agent. Copy .env.example to .env and set your project.
# - Tool: LangChain's WikipediaQueryRun, wrapped for ADK with LangchainTool.
#   ADK can use any LangChain tool this way.
# - Needs: pip install langchain-community wikipedia
# - Run locally: `adk web` (http://localhost:8000) and pick a006_wikipedia_agent.

import wikipedia
from google.adk.agents.llm_agent import Agent
from google.adk.integrations.langchain import LangchainTool
from google.adk.models import Gemini
from google.genai import types
from langchain_community.tools import WikipediaQueryRun
from langchain_community.utilities import WikipediaAPIWrapper

# Wikipedia rate-limits (429) the `wikipedia` package's shared default
# User-Agent, so identify this app with its own.
wikipedia.set_user_agent('adk-handson-wikipedia-agent/1.0 (learning project)')

# LangChain tool: searches Wikipedia and returns page summaries.
langchain_wikipedia = WikipediaQueryRun(
    api_wrapper=WikipediaAPIWrapper(top_k_results=2, doc_content_chars_max=3000)
)

# Wrap the LangChain tool so the ADK agent can call it.
wikipedia_tool = LangchainTool(tool=langchain_wikipedia)

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
    name='wikipedia_agent',
    description='An assistant that answers factual questions using Wikipedia.',
    instruction="""
You are a knowledgeable assistant. Whenever the user asks about any person,
place, event, organization, concept or other factual topic, use the wikipedia
tool to look it up before answering. Search with a short, specific query
(for example "Alan Turing" rather than a full sentence).

Base your answer on what the tool returns. Reply in a friendly, conversational
way, keep it concise, and mention that the information comes from Wikipedia.
If Wikipedia has nothing useful, say so honestly instead of guessing.
""",
    tools=[wikipedia_tool],
)
