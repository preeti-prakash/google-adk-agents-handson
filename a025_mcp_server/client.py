import asyncio

from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client


async def main():

    server_url = "https://employee-mcp-854814512954.us-central1.run.app/mcp"

    async with streamable_http_client(server_url) as (
        read_stream,
        write_stream,
        _
    ):

        async with ClientSession(
            read_stream,
            write_stream
        ) as session:

            await session.initialize()

            # -------------------------
            # Discover TOOLS
            # -------------------------

            tools = await session.list_tools()

            print("TOOLS:")

            for tool in tools.tools:
                print("-", tool.name)

            # -------------------------
            # Call TOOL: one employee
            # -------------------------

            result = await session.call_tool(
                "get_employee",
                arguments={
                    "employee_id": 101
                }
            )

            print("\nTool Result:")
            print(result)

            # -------------------------
            # Call TOOL: all employees
            # -------------------------

            all_result = await session.call_tool(
                "get_all_employees",
                arguments={}
            )

            print("\nAll Employees Result:")
            print(all_result)


if __name__ == "__main__":
    asyncio.run(main())
