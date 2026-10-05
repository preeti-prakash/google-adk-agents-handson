from typing import Any, Optional

from google.adk.agents import LlmAgent
from google.adk.agents.callback_context import CallbackContext
from google.adk.models import LlmRequest, LlmResponse
from google.adk.tools import ToolContext
from google.adk.tools.base_tool import BaseTool
from google.genai import types


# --------------------------------------------------
# Tool
# --------------------------------------------------

def get_leave_balance(employee_name: str) -> dict:
    """Returns how many leave days an employee has left.

    Args:
        employee_name: The employee's first name.
    """
    balances = {"preeti": 12, "ravi": 5, "anita": 0}
    days = balances.get(employee_name.lower())
    if days is None:
        return {"status": "error", "message": f"No record for {employee_name}."}
    return {"status": "success", "employee": employee_name, "days_left": days}


# --------------------------------------------------
# Callbacks
#
# Every callback can either:
#   - return None  -> ADK carries on as normal
#   - return a value -> ADK uses that value and skips the normal step
# --------------------------------------------------

# 1. Before the agent starts handling a message
def before_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    print(f"\n[1 before_agent]  agent '{callback_context.agent_name}' starting")
    return None


# 2. Before each call to Gemini: a simple guardrail on the user's message
BLOCKED_WORDS = ["password", "salary of"]

def before_model(
    callback_context: CallbackContext, llm_request: LlmRequest
) -> Optional[LlmResponse]:
    last_message = ""
    if llm_request.contents and llm_request.contents[-1].role == "user":
        last_message = " ".join(
            p.text for p in llm_request.contents[-1].parts if p.text
        ).lower()

    print(f"[2 before_model]  sending {len(llm_request.contents)} message(s) to Gemini")

    for word in BLOCKED_WORDS:
        if word in last_message:
            print(f"[2 before_model]  BLOCKED: message contains '{word}', Gemini not called")
            # Returning a response skips the Gemini call entirely
            return LlmResponse(
                content=types.Content(
                    role="model",
                    parts=[types.Part(text="Sorry, I can't help with that request.")],
                )
            )
    return None


# 3. After Gemini replies
def after_model(
    callback_context: CallbackContext, llm_response: LlmResponse
) -> Optional[LlmResponse]:
    parts = llm_response.content.parts if llm_response.content else []
    if any(p.function_call for p in parts):
        print("[3 after_model]   Gemini asked to call a tool")
    else:
        print("[3 after_model]   Gemini replied with text")
    return None


# 4. Before a tool runs
def before_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext
) -> Optional[dict]:
    print(f"[4 before_tool]   running '{tool.name}' with {args}")
    return None


# 5. After a tool runs: add a note to the result
def after_tool(
    tool: BaseTool, args: dict[str, Any], tool_context: ToolContext, tool_response: dict
) -> Optional[dict]:
    print(f"[5 after_tool]    '{tool.name}' returned {tool_response}")
    if tool_response.get("days_left") == 0:
        # Returning a dict replaces the tool's result
        return {**tool_response, "note": "No leave left. Suggest talking to HR."}
    return None


# 6. After the agent has finished the message
def after_agent(callback_context: CallbackContext) -> Optional[types.Content]:
    print(f"[6 after_agent]   agent '{callback_context.agent_name}' finished\n")
    return None


# --------------------------------------------------
# Agent
# --------------------------------------------------

root_agent = LlmAgent(
    name="leave_assistant",
    model="gemini-2.5-flash",
    instruction="""
    You are an HR leave assistant.
    Use the get_leave_balance tool to answer questions about leave days.
    If the tool result includes a note, pass it on to the user.
    """,
    tools=[get_leave_balance],
    before_agent_callback=before_agent,
    before_model_callback=before_model,
    after_model_callback=after_model,
    before_tool_callback=before_tool,
    after_tool_callback=after_tool,
    after_agent_callback=after_agent,
)
