"""Product Catalog Onboarding: a simple ADK 2.0 graph-based workflow.

    START -> validator_agent -> route --invalid--> reject_agent
                                  |
                                valid
                                  ├──> qr_agent ───────────┐   (parallel)
                                  └──> description_agent ──┤
                                                          join -> catalog_agent
"""

from google.adk.agents import LlmAgent
from google.adk.events import Event
from google.adk.workflow import JoinNode
from google.adk.workflow import START
from google.adk.workflow import Workflow

MODEL = 'gemini-3.5-flash'

validator_agent = LlmAgent(
    model=MODEL,
    name='validator_agent',
    instruction="""
Check the product in the user's message. It is valid only if it has a product
name, a category (Electronics, Clothing, Home, Sports or Books) and a price
greater than 0.
If valid, reply: VALID | <name> | <category> | <price>
If not, reply: INVALID | <reason>
""",
    output_key='product',
)


def route(product: str) -> Event:
    """Sends the flow down the 'valid' or 'invalid' edge."""
    return Event(route='valid' if product.startswith('VALID') else 'invalid')


reject_agent = LlmAgent(
    model=MODEL,
    name='reject_agent',
    instruction='The product was rejected: {product}. Tell the user why in one friendly sentence.',
)

qr_agent = LlmAgent(
    model=MODEL,
    name='qr_agent',
    instruction='Create a product ID in the format QR-PROD-XXX (XXX = 3 random digits). Output only the ID.',
    output_key='qr_id',
)

description_agent = LlmAgent(
    model=MODEL,
    name='description_agent',
    instruction='Write a 2-sentence catalog description for this product (ignore the word VALID): {product}. Output only the description.',
    output_key='description',
)

catalog_agent = LlmAgent(
    model=MODEL,
    name='catalog_agent',
    instruction="""
Confirm the product was stored in the catalog, then list QR ID, Name,
Category, Price and Description (drop the word VALID).
QR ID: {qr_id}
Product: {product}
Description: {description}
""",
)

join = JoinNode(name='join')  # waits for both parallel agents

root_agent = Workflow(
    name='product_catalog_onboarding',
    edges=[
        (START, validator_agent, route, {
            'valid': (qr_agent, description_agent),   # tuple = run in parallel
            'invalid': reject_agent,                  # dict = conditional routing
        }),
        (qr_agent, join),
        (description_agent, join),
        (join, catalog_agent),
    ],
)
