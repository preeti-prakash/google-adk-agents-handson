# Product Catalog Onboarding: ADK 2.0 Graph Workflow

A simple **graph-based workflow** using `google.adk.workflow` (checked against google-adk 2.8.0). Each step is an agent with a model and an instruction. The graph decides the order.

```text
START -> validator_agent -> route --invalid--> reject_agent
                              |
                            valid
                              ├──> qr_agent ───────────┐   (parallel)
                              └──> description_agent ──┤
                                                      join -> catalog_agent
```

## The graph (actual ADK 2.0 code)

```python
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
```

| Concept | How it appears |
|---|---|
| **Nodes** | The agents, the `route` function and `join` |
| **Edges** | Each tuple in `edges`. `(A, B, C)` means A → B → C |
| **Sequential** | `START → validator_agent → route` |
| **Conditional** | `route` returns `valid` or `invalid`, and the dict picks the next node |
| **Parallel** | `(qr_agent, description_agent)` run at the same time |
| **Join** | `JoinNode` waits until both parallel agents have finished |
| **Final step** | `catalog_agent` runs only after the join |
| **Data between nodes** | `output_key` saves an agent's answer to state (`product`, `qr_id`, `description`), and later agents read it with `{placeholders}` |

`route` is the only non-agent node, and it's 3 lines. An agent can't pick an edge by itself, so this small function reads the validator's answer and returns the route.

## Run

From the `adk-fundamentals` folder (with `.env` set up like the other agents):

```bash
pip install -r workflow_agents/graph_agent/requirements.txt
adk web      # pick workflow_agents.graph_agent
```

## Sample input and output

**Valid:**
```text
Product Name: Wireless Headphones
Category: Electronics
Price: 79.99
```
```text
validator_agent:   VALID | Wireless Headphones | Electronics | 79.99
qr_agent:          QR-PROD-582
description_agent: Experience crystal-clear sound and ultimate freedom with these premium wireless headphones...
catalog_agent:     The product has been successfully stored in the catalog.
                   QR ID: QR-PROD-582 | Name: Wireless Headphones | Category: Electronics | Price: $79.99
```

**Invalid:**
```text
Product Name: Mystery Box
Category: Toys
Price: -5
```
```text
validator_agent: INVALID | The category must be Electronics, Clothing, Home, Sports or Books, and the price must be greater than 0.
reject_agent:    It looks like your product was rejected because it needs to belong to one of our approved categories...
```

The QR ID and the wording come from the model, so they change on each run.

## Why a graph instead of SequentialAgent / ParallelAgent / LoopAgent?

In ADK 2.x those three classes are **deprecated in favor of `Workflow`**.

- **ADK 1.x (conceptual):** one class per pattern, nested inside each other. There's no built-in "if valid, go here, else go there". You need a custom agent for that.
- **ADK 2.0 (conceptual):** one `Workflow`, drawn like a flowchart. A node is a step, a tuple is a parallel split, a dict is a decision, a `JoinNode` is a merge, and an edge pointing back is a loop.
