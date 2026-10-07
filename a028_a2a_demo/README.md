# a028_a2a_demo: Agent-to-Agent (A2A) communication

Two agents running as separate processes talk to each other over the A2A protocol.

| File | Role |
|---|---|
| `remote_agent.py` | **Remote agent** (`employee_details_agent`). It owns the employee data (name, designation, salary). `to_a2a()` turns it into an A2A server, and uvicorn serves it on port 8001. |
| `hr_agent/agent.py` | **Client agent** (`hr_agent`). Its sub-agent `employee_details` is a `RemoteA2aAgent` that points at the remote's Agent Card URL. |

## How it flows

```
User ──> hr_agent (adk web, :8000)
           │  transfer_to_agent("employee_details")
           ▼
         RemoteA2aAgent "employee_details"
           │ 1. GET  http://localhost:8001/.well-known/agent-card.json   (discover)
           │ 2. POST http://localhost:8001/   JSON-RPC message/send     (ask)
           ▼
         A2A server (to_a2a + uvicorn, :8001)
           │  runs employee_details_agent ──> get_employee_details tool
           ▼
         reply travels back as an A2A message ──> shown to the user
```

1. **Agent Card**: `to_a2a()` builds it from the agent's name, description, and tools. It is the remote's "business card": who the agent is, which skills it has, and which URL to call.
2. **Discovery**: on first use, `RemoteA2aAgent` downloads the card to learn the RPC endpoint.
3. **Delegation**: `hr_agent` treats `employee_details` like any local sub-agent and transfers to it. `RemoteA2aAgent` converts the turn into an A2A message and POSTs it.
4. **Execution**: the remote server runs its own agent with its own model, tools, and data, then returns the answer. The client never sees the employee data or the tools directly, only the A2A reply.

## Run

```bash
pip install "google-adk[a2a]"

# Terminal 1: remote agent (A2A server)
python a028_a2a_demo/remote_agent.py
curl http://localhost:8001/.well-known/agent-card.json   # inspect the card

# Terminal 2: client HR agent
adk web a028_a2a_demo        # pick "hr_agent" at http://localhost:8000
```

Try: *"What is Ravi's designation and salary?"* or *"Who works here?"*. Terminal 1 logs the `GET /.well-known/agent-card.json` and `POST /` calls as they happen.
