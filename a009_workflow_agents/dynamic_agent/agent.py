"""Product Catalog: an ADK 2.0 DYNAMIC workflow.

A graph workflow fixes the path in `edges`. A dynamic workflow decides the path
in plain Python at run time: one parent node calls other nodes with
`ctx.run_node(...)`, using normal if/elif/else.

    START -> product_workflow
                 ├── ctx.run_node(check_product)
                 ├── if invalid: stop ("Product rejected")
                 ├── ctx.run_node(electronics / clothing / food processor)
                 └── ctx.run_node(store_product)

Input: "<name>, <category>", e.g. "Wireless Headphones, Electronics". A sentence
that mentions the category also works, e.g. "I have a Denim Jacket under category clothing".
"""

from google.adk import Context
from google.adk import Workflow
from google.adk.workflow import node
from google.genai import types


# ---------- Nodes ----------
# A parameter named `node_input` receives what ctx.run_node(..., node_input=...) passes in.

@node(name="check_product")
def check_product(node_input: dict):
    if node_input["category"] in ["electronics", "clothing", "food"]:
        return "valid"
    return "invalid"


@node(name="electronics_processor")
def electronics_processor(node_input: dict):
    return f"Electronics processing for {node_input['name']}"


@node(name="clothing_processor")
def clothing_processor(node_input: dict):
    return f"Clothing processing for {node_input['name']}"


@node(name="food_processor")
def food_processor(node_input: dict):
    return f"Food processing for {node_input['name']}"


@node(name="store_product")
def store_product(node_input: str):
    return f"Stored in catalog: {node_input}"


# ---------- Dynamic Workflow ----------

@node(rerun_on_resume=True)
async def product_workflow(ctx: Context, node_input: str):
    # The user's message, e.g. "Wireless Headphones, Electronics" or
    # "I have a Denim Jacket under category clothing".
    text = node_input.strip()
    name = text.partition(",")[0].strip()
    words = text.lower().replace(",", " ").split()
    category = next((c for c in ["electronics", "clothing", "food"] if c in words), words[-1] if words else "")
    product = {"name": name, "category": category}

    # Step 1: Check the product
    status = await ctx.run_node(check_product, node_input=product)

    # Step 2: Dynamically decide what to run
    if status == "invalid":
        return reply(
            f"Product rejected: '{product['category']}' is not electronics, clothing or food.\n"
            "Try: Denim Jacket, Clothing"
        )

    if product["category"] == "electronics":
        result = await ctx.run_node(electronics_processor, node_input=product)
    elif product["category"] == "clothing":
        result = await ctx.run_node(clothing_processor, node_input=product)
    else:
        result = await ctx.run_node(food_processor, node_input=product)

    # Step 3: Store the result
    final_result = await ctx.run_node(store_product, node_input=result)
    return reply(final_result)


def reply(text: str) -> types.Content:
    """Returns text as a chat message, so it shows up in adk web."""
    return types.Content(role="model", parts=[types.Part(text=text)])


# ---------- Root Workflow ----------

root_agent = Workflow(
    name="product_catalog_workflow",
    edges=[("START", product_workflow)],
)
