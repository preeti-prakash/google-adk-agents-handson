"""News Summarizer: a small loop ADK workflow.

    START -> news_agent -> summarizer_agent -> check_length --ok--> final_agent
                                  ^                  |
                                  └── too_long ──────┘

news_agent writes a detailed news report with Google Search. summarizer_agent
shortens it, and check_length counts the words in Python. While the summary is
MAX_WORDS or longer, it loops back and shortens again (up to MAX_ROUNDS).
Run with `adk web` from adk-fundamentals.
"""

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.events import Event
from google.adk.models import Gemini
from google.adk.models import LlmResponse
from google.adk.tools import google_search
from google.adk.workflow import START
from google.adk.workflow import Workflow
from google.genai import types

# A loop makes many model calls, so retry on 429 (rate limit) and 503 (overloaded).
MODEL = Gemini(
    model='gemini-3.5-flash',
    retry_options=types.HttpRetryOptions(attempts=6, initial_delay=5, max_delay=60, http_status_codes=[429, 503]),
)
MAX_WORDS = 500
MAX_ROUNDS = 4


def save_draft(callback_context: CallbackContext, llm_response: LlmResponse) -> LlmResponse | None:
    """Saves the full draft to state and shows only a short status line in the chat."""
    parts = llm_response.content.parts if llm_response.content else []
    text = ''.join(p.text for p in parts if p.text and not p.thought)
    if not text or llm_response.partial:
        return None
    words = len(text.split())
    callback_context.state['draft'] = text
    callback_context.state['word_count'] = words
    callback_context.state['target_words'] = max(int(words * 0.75), 300)
    status = f'📰 News report ready: {words} words' if callback_context.agent_name == 'news_agent' else f'✂️ Shortened to {words} words'
    return LlmResponse(content=types.Content(role='model', parts=[types.Part(text=status)]))


# Step 1: gather the news -> state['draft']
news_agent = LlmAgent(
    model=MODEL,
    name='news_agent',
    instruction="""
Use google_search to find the latest news on the topic in the user's message.
Write a detailed news report (about 1,000 words) covering the main stories,
key facts, dates and background. Use a short paragraph per story.
Output only the report.
""",
    tools=[google_search],
    after_model_callback=save_draft,
)

# Loop step: shorten the current draft -> state['draft'] (overwrites it)
summarizer_agent = LlmAgent(
    model=MODEL,
    name='summarizer_agent',
    instruction="""
Shorten the news text below from {word_count} words to about {target_words}
words. Cut the least important sentences and details; keep the key facts,
names and dates, and keep one short paragraph per story.

Output ONLY the shortened news text itself. Do not describe what you changed,
do not list what you kept or removed, and do not mention word counts.

News text:
{draft}
""",
    after_model_callback=save_draft,
)


def check_length(word_count: int, rounds: int = 0) -> Event:
    """Checks the word count: 'too_long' loops back to the summarizer; 'ok' ends the loop."""
    rounds += 1
    if word_count < MAX_WORDS:
        route, note = 'ok', f'✅ Round {rounds}: {word_count} words, under {MAX_WORDS}. Done.'
    elif rounds >= MAX_ROUNDS:
        route, note = 'ok', f'⏹️ Round {rounds}: {word_count} words. Round limit reached.'
    else:
        route, note = 'too_long', f'🔁 Round {rounds}: {word_count} words, still {MAX_WORDS} or more. Shortening again.'
    status = types.Content(role='model', parts=[types.Part(text=note)])
    return Event(content=status, route=route, state={'rounds': rounds})


# After the loop: present the summary nicely
final_agent = LlmAgent(
    model=MODEL,
    name='final_agent',
    instruction="""
Format the news summary below for easy reading. Don't add or remove facts.

- Start with a short title (## heading).
- Then one ### heading per story, with its paragraph underneath.
- End with this line in italics: Summary: {word_count} words after {rounds} round(s).

News summary:
{draft}
""",
)

# NEW WAY: Workflow. The routing map sends 'too_long' back to summarizer_agent (the loop).
root_agent = Workflow(
    name='news_summarizer',
    edges=[(START, news_agent, summarizer_agent, check_length,
            {'too_long': summarizer_agent, 'ok': final_agent})],
)

# OLD WAY: LoopAgent (deprecated in ADK 2.x), kept for comparison.
# A LoopAgent can't count words by itself, so a small custom agent (or a tool
# that calls exit_loop) would check the length and stop the loop.
# from google.adk.agents import LoopAgent, SequentialAgent
#
# root_agent = SequentialAgent(
#     name='news_summarizer',
#     sub_agents=[
#         news_agent,
#         LoopAgent(name='summarize_loop', sub_agents=[summarizer_agent, length_checker],
#                   max_iterations=MAX_ROUNDS),
#         final_agent,
#     ],
# )
