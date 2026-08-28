"""MCP CLIENT minh họa — kết nối tới weather_server.py qua giao thức MCP."""
import asyncio
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main() -> None:
    params = StdioServerParameters(command=sys.executable, args=["weather_server.py"])

    async with stdio_client(params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()

            # 1. KHÁM PHÁ tool mà server công bố (không hard-code)
            tools = await session.list_tools()
            print("Tools server cung cap:")
            for t in tools.tools:
                print(f"  - {t.name}: {t.description}")

            # 2. Gọi tool — SERVER thực thi rồi trả kết quả về qua MCP
            for city in ["Hanoi", "Danang", "Haiphong"]:
                result = await session.call_tool("get_weather", {"city": city})
                print(f"\ncall_tool get_weather(city={city!r}):")
                print("  ->", result.content[0].text)


if __name__ == "__main__":
    asyncio.run(main())