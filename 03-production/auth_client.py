"""MCP Client có Authentication — kết nối tới auth_server.py qua HTTP."""
from __future__ import annotations

import asyncio
import os
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

import httpx
from mcp import ClientSession
from mcp.client.streamable_http import streamable_http_client

PORT = int(os.getenv("AUTH_PORT", 8001))
SERVER_URL = f"http://localhost:{PORT}/mcp"
TOKEN = sys.argv[1] if len(sys.argv) > 1 else os.getenv("MCP_AUTH_TOKEN", "dev-token-abc123")


async def main() -> None:
    headers = {}
    if TOKEN and TOKEN.upper() != "NONE":
        headers["Authorization"] = f"Bearer {TOKEN}"

    http_client = httpx.AsyncClient(headers=headers)

    try:
        async with http_client:
            async with streamable_http_client(SERVER_URL, http_client=http_client) as (
                read,
                write,
                *rest,
            ):
                async with ClientSession(read, write) as session:
                    await session.initialize()

                    tools = await session.list_tools()
                    print(f"[AUTH SUCCESS] Connected with token: {TOKEN!r}")
                    print("Available tools:")
                    for t in tools.tools:
                        print(f"  - {t.name}: {t.description}")

                    result = await session.call_tool("get_weather", {"city": "Hanoi"})
                    print(f"\nResult: {result.content[0].text}")
    except Exception as e:
        print(f"[AUTH REJECTED] Connection rejected: {e}")


if __name__ == "__main__":
    asyncio.run(main())