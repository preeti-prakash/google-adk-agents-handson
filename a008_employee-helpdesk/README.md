# Employee Helpdesk: ADK Multi-Agent Demo

A small **Google ADK multi-agent** demo. A root agent reads each employee request and hands it to the right specialist: IT, HR or Finance. Each specialist has its own mock tools.

```text
                    employee_helpdesk (root)
                  /          |           \
                 ▼           ▼            ▼
            it_agent      hr_agent     finance_agent
               |             |              |
   check_system_status   get_leave_balance   check_expense_policy
   create_it_ticket      get_company_policy  calculate_reimbursement
```

## How the delegation works

The routing uses ADK's native **sub-agent** pattern, not `if/else` code:

```python
root_agent = Agent(
    name='employee_helpdesk',
    instruction='...transfer to the right specialist...',
    sub_agents=[it_agent, hr_agent, finance_agent],
)
```

1. Because the root agent has `sub_agents`, ADK automatically gives it a **`transfer_to_agent`** tool.
2. Gemini reads each sub-agent's **`description`** and decides which one fits the request.
3. It calls `transfer_to_agent(agent_name='it_agent')`, for example, and the conversation continues with that specialist.
4. The specialist uses **its own tools** to answer. If a new question is outside its area, it can transfer back to `employee_helpdesk`.

So the **`description`** of each sub-agent is what drives the routing. Keep it clear and specific.

## Project structure

```text
a008_employee-helpdesk/
├── employee_helpdesk/
│   ├── __init__.py
│   ├── agent.py          # root_agent (employee_helpdesk) with sub_agents
│   ├── it_agent.py       # IT specialist + tools
│   ├── hr_agent.py       # HR specialist + tools
│   ├── finance_agent.py  # Finance specialist + tools
│   ├── config.py         # shared Gemini model config (with retries)
│   └── .env.example
├── requirements.txt
└── README.md
```

## Mock data

| Agent | Tool | Mock data |
|---|---|---|
| IT | `check_system_status()` | VPN is **degraded**; Wi-Fi, email, laptop provisioning and SSO are operational |
| IT | `create_it_ticket(issue)` | Returns a ticket ID like `IT-1234` |
| HR | `get_leave_balance(employee_id)` | `emp1`, `emp2`, `emp3`, each with vacation, sick and personal days |
| HR | `get_company_policy(policy_name)` | `vacation`, `sick_leave`, `remote_work`, `parental_leave` |
| Finance | `check_expense_policy(expense_type)` | Limits: hotel $200/night, meals $75/day, travel $1000, software $300, training $1500/yr |
| Finance | `calculate_reimbursement(amount, category)` | `min(amount, limit)`, plus the amount not covered |

## Setup

Uses Gemini on **Vertex AI / Agent Platform** with your gcloud login (ADC). No API key is needed.

```bash
# 1. Install
pip install -r requirements.txt

# 2. Log in and pick your project
gcloud auth application-default login
gcloud auth application-default set-quota-project YOUR_PROJECT_ID
gcloud services enable aiplatform.googleapis.com --project=YOUR_PROJECT_ID

# 3. Configure the agent
cp employee_helpdesk/.env.example employee_helpdesk/.env
# then set GOOGLE_CLOUD_PROJECT in employee_helpdesk/.env
```

## Run locally

Run from the `a008_employee-helpdesk` folder:

```bash
adk web      # http://localhost:8000, then pick employee_helpdesk
# or
adk run employee_helpdesk
```

In the web UI, the **Events** panel shows each `transfer_to_agent` call and which agent answered. This is the easiest way to see the multi-agent flow.

### Try these

| Ask | What happens |
|---|---|
| "My VPN is not working." | Root transfers to **it_agent**, which runs `check_system_status`, sees the VPN is degraded, and runs `create_it_ticket` |
| "How many vacation days do I have?" then "emp1" | Root transfers to **hr_agent**, which asks for the ID and then runs `get_leave_balance`: 12 vacation days |
| "I spent $250 on a hotel. How much can I claim?" | Root transfers to **finance_agent**, which runs `calculate_reimbursement`: $200 covered, $50 not covered |
| "What's the remote work policy?" | **hr_agent** runs `get_company_policy` |
| "Hi, what can you help with?" | The root answers itself and lists the three areas |

## Deploy to Vertex AI Agent Engine

Run from the `a008_employee-helpdesk` folder:

```bash
adk deploy agent_engine \
  --project=YOUR_PROJECT_ID \
  --region=us-central1 \
  --display_name=employee-helpdesk \
  employee_helpdesk
```

- The whole package is deployed together: root agent, sub-agents and tools.
- Agent Engine needs a real region (not `global`).
- `gemini-3.5-flash` may only be available at the `global` location. If the deployed agent returns `404 model not found`, switch `config.py` to a model offered in your region (for example `gemini-2.5-flash`).
- To **update** an existing deployment, add `--agent_engine_id=<ID>`. Without it, each run creates a new, billable instance.
- View, test and delete it in the Console under **Agent Platform → Agent Engine**.

## Notes

- **Retries:** all agents share one `Gemini` config with retries on 429 and 503. A multi-agent turn makes several model calls (routing, tool calls, answer), so rate limits are more likely.
- **Context caching warning:** ADK may log that the app "can transfer between agents but has no context_cache_config". That's a cost optimization hint, not an error. The demo works without it.
- **Mock tools:** replace the hardcoded dictionaries with real systems (ServiceNow, Workday, SAP and so on). The agents don't need to change.
