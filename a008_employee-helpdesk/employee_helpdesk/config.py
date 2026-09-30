"""Shared model settings for all helpdesk agents."""

from google.adk.models import Gemini
from google.genai import types

# One Gemini model config reused by the root agent and every sub-agent.
# Retries with backoff on 429 (rate limit) and 503 (model overloaded), which
# matter more here because a multi-agent turn makes several model calls.
MODEL = Gemini(
    model='gemini-3.5-flash',
    retry_options=types.HttpRetryOptions(
        attempts=5,
        initial_delay=2,
        max_delay=30,
        http_status_codes=[429, 503],
    ),
)
