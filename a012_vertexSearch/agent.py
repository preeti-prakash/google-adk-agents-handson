import os

from google.adk.agents import LlmAgent
from google.adk.tools import VertexAiSearchTool


# Your Vertex AI Search / Agent Search Data Store (values come from .env)
DATASTORE_ID = (
    f"projects/{os.environ['GOOGLE_CLOUD_PROJECT']}/"
    "locations/global/"
    "collections/default_collection/"
    f"dataStores/{os.environ['VERTEX_SEARCH_DATASTORE_ID']}"
)


# Create the Vertex AI Search tool
search_tool = VertexAiSearchTool(
    data_store_id=DATASTORE_ID
)


# Create the ADK agent
root_agent = LlmAgent(
    name="employee_onboarding_agent",

    model="gemini-2.5-flash",

    instruction="""
    You are an Employee Onboarding Assistant.

    Help employees answer questions about the company's
    onboarding process.

    Use the connected Vertex AI Search knowledge base to
    answer questions.

    Only provide information that is supported by the
    onboarding documentation.

    If the requested information is not available in the
    knowledge base, say that the information was not found
    in the employee onboarding documentation.
    """,

    tools=[
        search_tool
    ],
)
