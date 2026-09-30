from google.adk.agents import LlmAgent
from google.genai import types

root_agent = LlmAgent(
    name="product_description_agent",
    model="gemini-2.5-flash",

    instruction="""
    You are a product description agent.

    Given a product name, generate a short and creative
    product description that is suitable for an online catalog.
    """,

    generate_content_config=types.GenerateContentConfig(
        temperature=0.8,
        max_output_tokens=600,
        # Gemini 2.5 "thinking" tokens count toward max_output_tokens; turn it off
        # so the full limit goes to the description.
        thinking_config=types.ThinkingConfig(thinking_budget=0),
    ),
)
