# Product Catalog: ADK 2.0 Dynamic Workflow

In a **graph workflow** (`graph_agent`), the path is fixed in `edges`. In a **dynamic workflow**, one parent node decides the path **in Python at run time**. It calls other nodes with `ctx.run_node(...)`, using normal `if / elif / else`.

```text
START -> product_workflow
             ├── ctx.run_node(check_product)
             ├── if invalid → "Product rejected"
             ├── ctx.run_node(electronics / clothing / food processor)
             └── ctx.run_node(store_product)
```

The graph itself has only one edge: `("START", product_workflow)`. Everything else is decided inside `product_workflow`.

## Key points

- **`@node`** turns a function into a workflow node.
- **`await ctx.run_node(node, node_input=...)`** runs a node and returns its result.
- **Parameters named `node_input`** receive what's passed in. Any other parameter name is looked up in **session state** instead. A version using `product: dict` fails with "Missing value for parameter 'product'... not found in state".
- **The final step returns `types.Content`,** so the result appears as a chat message in `adk web`. A plain returned string is only the node's output, not a chat message.
- **No LLM:** this workflow runs on Python alone, so it needs no `.env` or Gemini.

## Run

From the `adk-fundamentals` folder:

```bash
adk web      # pick a009_workflow_agents.dynamic_agent
```

Input format: `<name>, <category>`

| Input | Path taken | Chat reply |
|---|---|---|
| `Wireless Headphones, Electronics` | check → electronics_processor → store | Stored in catalog: Electronics processing for Wireless Headphones |
| `Denim Jacket, Clothing` | check → clothing_processor → store | Stored in catalog: Clothing processing for Denim Jacket |
| `Organic Honey, Food` | check → food_processor → store | Stored in catalog: Food processing for Organic Honey |
| `Toy Car, Toys` | check → stop | Product rejected: 'toys' is not electronics, clothing or food. |

## Graph vs dynamic: when to use which

| | Graph (`graph_agent`) | Dynamic (`dynamic_agent`) |
|---|---|---|
| Path defined in | `edges` (a routing dict for decisions) | Python code (`if/else`, loops) |
| Easy to visualize | ✅ The graph shows every path | Only the parent node appears |
| Many branches / complex logic | Many edges | ✅ Plain code |
| Good for | Fixed, well-known flows | Flows that depend on the data at run time |
