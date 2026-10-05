from google.adk.agents import LlmAgent
from google.adk.models.lite_llm import LiteLlm


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


root_agent = LlmAgent(
    name="ollama_agent",
    # LiteLLM routes "ollama_chat/<model>" to the local Ollama server
    # (address from OLLAMA_API_BASE in .env) instead of Gemini.
    model=LiteLlm(model="ollama_chat/llama3.2"),
    instruction="""
    You are a helpful HR assistant.
    Use the get_leave_balance tool when asked about an employee's leave days.
    Answer other questions directly and briefly.
    """,
    tools=[get_leave_balance],
)
