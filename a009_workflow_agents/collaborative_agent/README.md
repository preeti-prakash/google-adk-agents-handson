# Party Planner: ADK 2.0 Collaborative Agents

A **coordinator** works together with three helper agents. Unlike a transfer (as in `a008_employee-helpdesk`), the coordinator **stays in charge**: it calls each helper like a tool, gets the result back, and combines everything.

```text
coordinator (root)
  ├── details_agent   mode='task'         asks the user questions, then returns the details (finish_task)
  ├── venue_agent     mode='single_turn'  returns one venue idea
  └── menu_agent      mode='single_turn'  returns a 3-item menu
```

## The `mode` setting on a sub-agent

| mode | What happens | Who talks to the user |
|---|---|---|
| `chat` (default) | Control is **transferred** to the sub-agent | The sub-agent, from then on |
| `task` | The sub-agent is called like a tool, may **ask the user questions**, then returns its result with the built-in `finish_task` tool | The sub-agent, until the task is done, then the coordinator again |
| `single_turn` | The sub-agent is called like a tool and returns an answer right away, with **no chatting** | The coordinator |

Setting `mode='task'` or `mode='single_turn'` is all it takes. ADK turns those sub-agents into tools for the coordinator automatically.

## Run

From the `adk-fundamentals` folder (with `.env` set up like the other agents):

```bash
adk web      # pick a009_workflow_agents.collaborative_agent
```

## Example conversation (real test run)

```text
You:            Help me plan a party
coordinator  →  calls details_agent
details_agent:  What is the occasion for the party?
You:            It's my sister's 30th birthday
details_agent:  How many guests will be attending?
You:            About 20 guests, budget 800 dollars
details_agent → finish_task("sister's 30th birthday, about 20 guests, $800")
coordinator  →  calls venue_agent and menu_agent
coordinator:    ### Details  ... ### Venue  ... ### Menu  ...
```

If you give everything at once ("Plan a 30th birthday for 20 guests, budget $800"), `details_agent` has nothing to ask and finishes right away.
