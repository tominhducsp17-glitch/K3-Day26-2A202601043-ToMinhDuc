"""MCP Server có Authentication — minh họa bảo mật cho production.

Server chạy qua HTTP (Streamable HTTP) thay vì stdio, kèm bearer token
verification. Chỉ request mang token hợp lệ mới được phép khám phá và gọi tool.

Luồng hoạt động:
  Client gửi request HTTP kèm header "Authorization: Bearer <token>"
    → MCP SDK tự chạy BearerAuthBackend để xác minh token
    → Token hợp lệ → cho phép truy cập tool
    → Token sai / thiếu → trả về 401/403

Cách chạy:
    python auth_server.py
    # Server lắng nghe tại http://localhost:8001/mcp
"""

from __future__ import annotations

import os
import sys

if sys.stdout:
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")
if sys.stderr:
    sys.stderr.reconfigure(encoding="utf-8", errors="replace")

from mcp.server.auth.provider import AccessToken, TokenVerifier
from mcp.server.auth.settings import AuthSettings
from mcp.server.fastmcp import FastMCP

PORT = int(os.getenv("AUTH_PORT", 8001))

# --- Token store (production: dùng DB, Redis, hoặc JWT verification) ---
VALID_TOKENS: dict[str, str] = {
    os.environ.get("MCP_AUTH_TOKEN", "dev-token-abc123"): "dev-user",
    "prod-key-xyz789": "prod-service",
}


class StaticTokenVerifier(TokenVerifier):
    """Kiểm tra bearer token dựa trên danh sách tĩnh."""

    async def verify_token(self, token: str) -> AccessToken | None:
        client_id = VALID_TOKENS.get(token)
        if client_id is None:
            return None
        return AccessToken(token=token, client_id=client_id, scopes=["weather:read"])


mcp = FastMCP(
    "weather-secure",
    auth=AuthSettings(
        issuer_url=f"http://localhost:{PORT}",
        resource_server_url=f"http://localhost:{PORT}",
    ),
    token_verifier=StaticTokenVerifier(),
    host="0.0.0.0",
    port=PORT,
)

_MOCK_DB = {
    "Hanoi": "29°C, trời mưa",
    "Haiphong": "33°C, mưa rào",
    "Danang": "30°C, nhiều mây",
}


@mcp.tool()
def get_weather(city: str) -> str:
    """Lấy thời tiết hiện tại của một thành phố."""
    return f"{city}: {_MOCK_DB.get(city, '28°C, không có dữ liệu chi tiết')}"


if __name__ == "__main__":
    print(f"Starting Authenticated MCP server on http://0.0.0.0:{PORT}/mcp")
    mcp.run(transport="streamable-http")