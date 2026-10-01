from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool, ToolContext
from google.genai import types


# save_artifact is async, so the tool must be async and await it.
async def create_report(tool_context: ToolContext):
    report = """
    Monthly Sales Report

    Total Sales: $25,000
    Orders: 150
    """

    await tool_context.save_artifact(
        filename="sales_report.txt",
        artifact=types.Part(text=report),
    )

    return "Sales report created."


report_tool = FunctionTool(create_report)


root_agent = LlmAgent(
    name="report_agent",
    model="gemini-2.5-flash",
    instruction="""
    You are a sales report assistant.
    When the user asks for a sales report,
    use the create_report tool.
    """,
    tools=[report_tool],
)
