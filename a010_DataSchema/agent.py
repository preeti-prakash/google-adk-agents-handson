from google.adk.agents import LlmAgent
from pydantic import BaseModel


# Input schema
class ProductInput(BaseModel):
    product_name: str
    description: str


# Output schema
class ProductOutput(BaseModel):
    category: str
    summary: str


# ADK Agent
root_agent = LlmAgent(
    name="product_classifier",
    model="gemini-2.5-flash",
    instruction="""
    You are a product classification agent.

    Given a product name and description:
    1. Identify the most appropriate product category.
    2. Provide a short summary of the product.
    """,

    input_schema=ProductInput,
    output_schema=ProductOutput,
)
