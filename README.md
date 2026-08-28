# K3 Day 26 â€” Model Context Protocol (MCP) Server & Agent Integration

BÃ¡o cÃ¡o nghiá»‡m thu & hÆ°á»›ng dáº«n cháº¡y bÃ i Lab Day 26 cho cáº£ 3 cáº¥p Ä‘á»™: **CÆ¡ báº£n**, **Trung bÃ¬nh** vÃ  **KhÃ³**.

---

## 1. MÃ´ táº£ cÃ´ng viá»‡c thá»±c táº¿ mÃ  MCP Server giáº£i quyáº¿t

Trong thá»±c táº¿, cÃ¡c Large Language Model (LLM) nhÆ° Claude, Gemini hay GPT bá»‹ giá»›i háº¡n bá»Ÿi:
1. **Dá»¯ liá»‡u tÄ©nh (cutoff date):** KhÃ´ng thá»ƒ biáº¿t thá»i tiáº¿t, nhiá»‡t Ä‘á»™ hay thiÃªn tai Ä‘ang diá»…n ra thá»i gian thá»±c.
2. **Nguy cÆ¡ Hallucination (bá»‹a Ä‘áº·t):** Khi ngÆ°á»i dÃ¹ng há»i thá»i tiáº¿t, LLM dá»… tá»± suy diá»…n thÃ´ng tin sai lá»‡ch gÃ¢y nguy hiá»ƒm cho káº¿ hoáº¡ch di chuyá»ƒn, du lá»‹ch, logistics hoáº·c nÃ´ng nghiá»‡p.

**Giáº£i phÃ¡p:**  
Há»‡ thá»‘ng **Weather MCP Server** Ä‘Æ°á»£c xÃ¢y dá»±ng nháº±m cung cáº¥p chuáº©n káº¿t ná»‘i má»Ÿ **Model Context Protocol (MCP)** giá»¯a AI Agent vÃ  cÃ¡c tráº¡m khÃ­ tÆ°á»£ng thá»§y vÄƒn thá»i gian thá»±c:
- Cho phÃ©p AI Agent tá»± Ä‘á»™ng khÃ¡m phÃ¡ nÄƒng lá»±c (Tool Discovery) mÃ  khÃ´ng cáº§n hard-code logic vÃ o á»©ng dá»¥ng.
- Cung cáº¥p dá»¯ liá»‡u nhiá»‡t Ä‘á»™, Ä‘á»™ áº©m, sá»©c giÃ³, chá»‰ sá»‘ UV, táº§m nhÃ¬n vÃ  dá»± bÃ¡o thá»i tiáº¿t nhiá»u ngÃ y theo thá»i gian thá»±c táº¿.
- Há»— trá»£ triá»ƒn khai linh hoáº¡t qua cáº£ **Stdio** (local) láº«n **Streamable HTTP** (máº¡ng phÃ¢n tÃ¡n, cloud deployment).

---

## 2. MÃ´ táº£ Input / Output chi tiáº¿t cá»§a tá»«ng Tool

### A. Há»‡ thá»‘ng Weather Agent chÃ­nh (`04-lab/mcp-server/weather.py`)

| TÃªn Tool | Tham sá»‘ Ä‘áº§u vÃ o (Input) | Kiá»ƒu dá»¯ liá»‡u | Báº¯t buá»™c | MÃ´ táº£ & VÃ­ dá»¥ Ä‘áº§u ra (Output) |
|---|---|---|:---:|---|
| `get_current_weather` | `city` | `str` | CÃ³ | **Input:** TÃªn thÃ nh phá»‘ báº¥t ká»³ trÃªn tháº¿ giá»›i (vÃ­ dá»¥: `"Hanoi"`, `"Danang"`, `"Tokyo"`).<br>**Output:** Chuá»—i bÃ¡o cÃ¡o chi tiáº¿t gá»“m: Nhiá»‡t Ä‘á»™ (Â°C/Â°F), Nhiá»‡t Ä‘á»™ cáº£m nháº­n, TÃ¬nh tráº¡ng mÃ¢y, Äá»™ áº©m %, Tá»‘c Ä‘á»™ giÃ³, HÆ°á»›ng giÃ³, Ãp suáº¥t khÃ­ quyá»ƒn (mb), Chá»‰ sá»‘ UV, Táº§m nhÃ¬n (km), Thá»i gian cáº­p nháº­t. |
| `get_forecast` | `city`<br>`days` | `str`<br>`int` | CÃ³<br>KhÃ´ng (máº·c Ä‘á»‹nh = 3) | **Input:** TÃªn thÃ nh phá»‘ vÃ  sá»‘ ngÃ y dá»± bÃ¡o (tá»‘i Ä‘a 3 ngÃ y).<br>**Output:** BÃ¡o cÃ¡o dá»± bÃ¡o tá»«ng ngÃ y gá»“m: Nhiá»‡t Ä‘á»™ cao nháº¥t/tháº¥p nháº¥t, TÃ¬nh tráº¡ng thá»i tiáº¿t, XÃ¡c suáº¥t cÃ³ mÆ°a (%), Tá»‘c Ä‘á»™ giÃ³ tá»‘i Ä‘a, Chá»‰ sá»‘ UV. |
| `health_check` | KhÃ´ng cÃ³ | â€” | â€” | **Output:** Chuá»—i xÃ¡c nháº­n server MCP Ä‘ang hoáº¡t Ä‘á»™ng á»•n Ä‘á»‹nh vÃ  sáºµn sÃ ng phá»¥c vá»¥. |

### B. Há»‡ thá»‘ng Versioned MCP Server (`03-production/versioned_server.py`)

| TÃªn Tool | PhiÃªn báº£n | Tham sá»‘ Ä‘áº§u vÃ o (Input) | MÃ´ táº£ Ä‘áº§u ra (Output) |
|---|:---:|---|---|
| `get_weather` | **v1** (Legacy) | `city: str` | Tráº£ vá» chuá»—i rÃºt gá»n cho client cÅ©: `Hanoi: 29Â°C, trá»i mÆ°a` |
| `get_weather_v2` | **v2** (Modern) | `city: str`<br>`include_forecast: bool = False`<br>`units: str = "celsius"` | Tráº£ vá» JSON chuáº©n hÃ³a v2.0 cÃ³ timestamp UTC, kÃ¨m máº£ng dá»± bÃ¡o náº¿u báº­t `include_forecast=True` vÃ  chuyá»ƒn Ä‘á»•i Ä‘Æ¡n vá»‹ (`celsius`/`fahrenheit`). |

---

## 3. Cáº¥u trÃºc thÆ° má»¥c Repository

```text
â”œâ”€â”€ 01-function-calling/          # So sÃ¡nh Function Calling thuáº§n vá»›i Gemini SDK
â”œâ”€â”€ 02-mcp-basics/               # MCP Server cÆ¡ báº£n cháº¡y qua Stdio Transport
â”‚   â”œâ”€â”€ weather_server.py        # FastMCP Server stdio
â”‚   â””â”€â”€ weather_client.py        # Client tá»± khÃ¡m phÃ¡ vÃ  gá»i tool qua stdio
â”œâ”€â”€ 03-production/               # Ká»¹ thuáº­t Production: Auth, Versioning, Registry
â”‚   â”œâ”€â”€ auth_server.py           # [BÃ i Trung bÃ¬nh] Streamable HTTP + Bearer Token Auth
â”‚   â”œâ”€â”€ auth_client.py           # [BÃ i Trung bÃ¬nh] Client xÃ¡c thá»±c token há»£p lá»‡/khÃ´ng há»£p lá»‡
â”‚   â”œâ”€â”€ versioned_server.py      # [BÃ i KhÃ³] Versioning v1/v2 + Resource server://info
â”‚   â””â”€â”€ versioned_client.py      # [BÃ i KhÃ³] Client Ä‘á»c metadata trÆ°á»›c khi gá»i tool v1 & v2
â”œâ”€â”€ 04-lab/                      # [BÃ i Lab hoÃ n chá»‰nh] Weather Agent vá»›i Google ADK
â”‚   â”œâ”€â”€ mcp-server/weather.py    # FastMCP Server cháº¡y Streamable HTTP (Port 8085)
â”‚   â”œâ”€â”€ mcp-client/
â”‚   â”‚   â”œâ”€â”€ weather_agent/agent.py # Agent káº¿t ná»‘i qua StreamableHTTPConnectionParams
â”‚   â”‚   â””â”€â”€ verify_setup.py      # Ká»‹ch báº£n kiá»ƒm thá»­ tá»± Ä‘á»™ng toÃ n bá»™ mÃ´i trÆ°á»ng
â”‚   â””â”€â”€ VERIFICATION.md          # Báº±ng chá»©ng nghiá»‡m thu káº¿t quáº£ kiá»ƒm thá»­
â””â”€â”€ README.md                    # TÃ i liá»‡u hÆ°á»›ng dáº«n ná»™p bÃ i tá»•ng há»£p
```

---

## 4. HÆ°á»›ng dáº«n cÃ i Ä‘áº·t vÃ  cháº¡y (Quickstart)

### BÆ°á»›c 1: Chuáº©n bá»‹ mÃ´i trÆ°á»ng & CÃ i Ä‘áº·t thÆ° viá»‡n
YÃªu cáº§u Python >= 3.10. Báº¡n cÃ³ thá»ƒ sá»­ dá»¥ng `uv` hoáº·c `pip`:

```bash
# CÃ i Ä‘áº·t thÆ° viá»‡n cho bÃ i lab
cd 04-lab/mcp-client
uv sync
# Hoáº·c cÃ i Ä‘áº·t tá»•ng quÃ¡t:
pip install -r requirements.txt
```

### BÆ°á»›c 2: Cáº¥u hÃ¬nh biáº¿n mÃ´i trÆ°á»ng
Táº¡o file `.env` táº¡i thÆ° má»¥c `04-lab/mcp-client/.env` vÃ  `04-lab/mcp-server/.env`:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
WEATHERAPI_KEY=your_weatherapi_key_here
```
*(LÆ°u Ã½: Náº¿u khÃ´ng cÃ³ key WeatherAPI, server tÃ­ch há»£p sáºµn cÆ¡ cháº¿ Live Meteorology Fallback tá»± Ä‘á»™ng láº¥y dá»¯ liá»‡u thá»i tiáº¿t thá»±c táº¿ tá»« Open-Meteo).*

### BÆ°á»›c 3: Khá»Ÿi Ä‘á»™ng MCP Server vÃ  ADK Agent
Má»Ÿ 2 cá»­a sá»• terminal:

- **Terminal 1 (Cháº¡y MCP Server Streamable HTTP):**
  ```bash
  cd 04-lab/mcp-server
  uv run python weather.py
  # Server láº¯ng nghe táº¡i: http://0.0.0.0:8085/mcp
  ```

- **Terminal 2 (Cháº¡y ADK Agent Web UI hoáº·c CLI):**
  ```bash
  cd 04-lab/mcp-client
  # Khá»Ÿi Ä‘á»™ng giao diá»‡n Web trá»±c quan:
  uv run adk web --port 8000
  # Má»Ÿ trÃ¬nh duyá»‡t: http://localhost:8000 vÃ  chá»n "weather_agent"
  ```

---

## 5. HÆ°á»›ng dáº«n Ä‘Äƒng kÃ½ MCP Server vá»›i Claude Code

Báº¡n cÃ³ thá»ƒ Ä‘Äƒng kÃ½ Weather MCP Server vÃ o **Claude Code** theo 2 cÃ¡ch:

### CÃ¡ch 1: ÄÄƒng kÃ½ qua Stdio Transport (KhuyÃªn dÃ¹ng khi cháº¡y local)
```bash
claude mcp add weather -- python "02-mcp-basics/weather_server.py"
```

### CÃ¡ch 2: ÄÄƒng kÃ½ qua Streamable HTTP Transport (Khi server Ä‘ang cháº¡y á»Ÿ port 8085)
```bash
claude mcp add weather-http --url http://localhost:8085/mcp
```

### Kiá»ƒm tra Ä‘Äƒng kÃ½ thÃ nh cÃ´ng trong Claude Code:
```bash
claude mcp list
```
Claude Code sáº½ liá»‡t kÃª `weather` vá»›i cÃ¡c tools: `get_current_weather`, `get_forecast`, `health_check`. Báº¡n cÃ³ thá»ƒ trá»±c tiáº¿p gÃµ vÃ o Claude Code: *"Thá»i tiáº¿t á»Ÿ HÃ  Ná»™i hÃ´m nay tháº¿ nÃ o?"* vÃ  Claude Code sáº½ tá»± Ä‘á»™ng gá»i MCP server Ä‘á»ƒ tráº£ lá»i.

---

## 6. Báº±ng chá»©ng & Kiá»ƒm tra Tool cháº¡y Ä‘Æ°á»£c (BÃ€I CÆ  Báº¢N)

### Ká»‹ch báº£n 1: Kiá»ƒm thá»­ tá»± Ä‘á»™ng vá»›i `verify_setup.py`
Cháº¡y lá»‡nh:
```bash
cd 04-lab/mcp-client
uv run python verify_setup.py
```
**Káº¿t quáº£ thá»±c táº¿:**
```text
============================================================
Weather Agent Setup Verification
============================================================

[*] Checking environment configuration...
[PASS] GOOGLE_API_KEY configured (AQ.Ab8RN6L...)

[*] Checking dependencies...
[PASS] Google ADK
[PASS] Google Generative AI
[PASS] MCP
[PASS] FastMCP
[PASS] python-dotenv
[PASS] httpx

[*] Checking agent structure...
[PASS] weather_agent/agent.py
[PASS] weather_agent/__init__.py

[*] Checking MCP server connectivity...
[PASS] MCP server reachable at http://localhost:8085/mcp

[*] Checking agent import...
[PASS] Agent imported successfully: weather_agent
       Model: gemini-2.5-flash

============================================================
[SUCCESS] All checks passed!
```

### Ká»‹ch báº£n 2: Cháº¡y trá»±c tiáº¿p qua CLI vá»›i cÃ¢u há»i tiáº¿ng Viá»‡t
```bash
uv run adk run weather_agent "Thá»i tiáº¿t hiá»‡n táº¡i á»Ÿ ÄÃ  Náºµng tháº¿ nÃ o?"
```
**Pháº£n há»“i thá»±c táº¿ tá»« Agent:**
> `[weather_agent]: Thá»i tiáº¿t hiá»‡n táº¡i á»Ÿ ÄÃ  Náºµng, Viá»‡t Nam lÃ  37.4Â°C (99.3Â°F), cáº£m giÃ¡c nhÆ° 41.2Â°C (106.2Â°F). TÃ¬nh tráº¡ng nhiá»u mÃ¢y, Ä‘á»™ áº©m 38%, giÃ³ 9.9 km/h.`

---

## 7. Pháº§n nÃ¢ng cao: BÃ€I TRUNG BÃŒNH (Streamable HTTP + Token Authentication)

MÃ£ nguá»“n táº¡i thÆ° má»¥c: `03-production/auth_server.py` vÃ  `03-production/auth_client.py`.

### A. CÆ¡ cháº¿ báº£o máº­t
Server cháº¡y giao thá»©c **Streamable HTTP** kÃ¨m middleware `TokenVerifier`. Má»i request pháº£i mang theo header:
```text
Authorization: Bearer dev-token-abc123
```
Náº¿u token sai hoáº·c thiáº¿u, server tráº£ vá» mÃ£ lá»—i chuáº©n `401 Unauthorized` kÃ¨m header `WWW-Authenticate: Bearer error="invalid_token"`.

### B. HÆ°á»›ng dáº«n Test Token ÄÃšNG
1. Khá»Ÿi Ä‘á»™ng server xÃ¡c thá»±c táº¡i Terminal 1:
   ```bash
   cd 03-production
   python auth_server.py
   # Láº¯ng nghe táº¡i: http://localhost:8001/mcp
   ```
2. Cháº¡y client vá»›i token há»£p lá»‡ táº¡i Terminal 2:
   ```bash
   python auth_client.py dev-token-abc123
   ```
   **Káº¿t quáº£:**
   ```text
   [AUTH SUCCESS] Connected with token: 'dev-token-abc123'
   Available tools:
     - get_weather: Láº¥y thá»i tiáº¿t hiá»‡n táº¡i cá»§a má»™t thÃ nh phá»‘.
   Result: Hanoi: 29Â°C, trá»i mÆ°a
   ```

### C. HÆ°á»›ng dáº«n Test Token SAI / THIáº¾U TOKEN

- **Test Token SAI báº±ng client:**
  ```bash
  python auth_client.py wrong-token-xyz
  # Káº¿t quáº£: [AUTH REJECTED] Connection rejected (401 Unauthorized)
  ```
- **Test Token SAI báº±ng curl:**
  ```bash
  curl -i -X POST http://localhost:8001/mcp \
    -H "Authorization: Bearer wrong-token" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "{}"
  ```
  **Káº¿t quáº£ server tráº£ vá»:**
  ```http
  HTTP/1.1 401 Unauthorized
  www-authenticate: Bearer error="invalid_token", error_description="Authentication required"

  {"error": "invalid_token", "error_description": "Authentication required"}
  ```

- **Test THIáº¾U TOKEN báº±ng client:**
  ```bash
  python auth_client.py NONE
  # Káº¿t quáº£: [AUTH REJECTED] Connection rejected
  ```
- **Test THIáº¾U TOKEN báº±ng curl:**
  ```bash
  curl -i -X POST http://localhost:8001/mcp -d "{}"
  # Káº¿t quáº£: HTTP/1.1 401 Unauthorized
  ```

---

## 8. Pháº§n nÃ¢ng cao: BÃ€I KHÃ“ (Versioning, Backward Compatibility & Resource `server://info`)

MÃ£ nguá»“n táº¡i thÆ° má»¥c: `03-production/versioned_server.py` vÃ  `03-production/versioned_client.py`.

### A. CÃ¡c ká»¹ thuáº­t triá»ƒn khai
1. **Tool má»›i song song:** Giá»¯ nguyÃªn tool v1 (`get_weather`) cho client cÅ©, Ä‘á»“ng thá»i phÃ¡t triá»ƒn tool v2 (`get_weather_v2`) tráº£ vá» cáº¥u trÃºc JSON giÃ u dá»¯ liá»‡u hÆ¡n.
2. **Tham sá»‘ optional vá»›i giÃ¡ trá»‹ default:** `include_forecast: bool = False`, `units: str = "celsius"` Ä‘á»ƒ trÃ¡nh lÃ m gÃ£y schema cá»§a client.
3. **Resource `server://info`:** CÃ´ng bá»‘ phiÃªn báº£n server `2.0.0`, danh sÃ¡ch tool Ä‘Ã£ bá»‹ deprecated (`['get_weather']`) vÃ  cáº©m nang di chuyá»ƒn `migration_guide`.
4. **Client Ä‘á»c metadata trÆ°á»›c khi gá»i tool:** Client chá»§ Ä‘á»™ng truy váº¥n `session.read_resource("server://info")` Ä‘á»ƒ kiá»ƒm tra tráº¡ng thÃ¡i trÆ°á»›c khi tÆ°Æ¡ng tÃ¡c.

### B. HÆ°á»›ng dáº«n cháº¡y vÃ  nghiá»‡m thu
Cháº¡y client nghiá»‡m thu phiÃªn báº£n:
```bash
cd 03-production
python versioned_client.py
```
**Káº¿t quáº£ thá»±c táº¿ hiá»ƒn thá»‹ Ä‘áº§y Ä‘á»§:**
```text
Server: weather-v2 v2.0.0
Deprecated tools: ['get_weather']
Migration: Chuyá»ƒn tá»« get_weather sang get_weather_v2. Tham sá»‘ 'city' giá»¯ nguyÃªn, thÃªm include_forecast vÃ  units.

Tools:
  - get_weather: [v1] Láº¥y thá»i tiáº¿t hiá»‡n táº¡i â€” tráº£ chuá»—i Ä‘Æ¡n giáº£n. Deprecated, dÃ¹ng get_weather_v2.
  - get_weather_v2: [v2] Láº¥y thá»i tiáº¿t chi tiáº¿t â€” JSON, há»— trá»£ forecast vÃ  Ä‘Æ¡n vá»‹ Ä‘o.

[v1] get_weather('Hanoi'):
  Hanoi: 29Â°C, trá»i mÆ°a

[v2] get_weather_v2('Hanoi', forecast=True):
{
  "api_version": "2.0",
  "city": "Hanoi",
  "temp": 29,
  "units": "celsius",
  "condition": "trá»i mÆ°a",
  "humidity": 82,
  "wind_speed_kmh": 12,
  "timestamp": "2026-08-28T07:01:34+00:00",
  "forecast": [
    {
      "day": "tomorrow",
      "temp": 27,
      "condition": "mÆ°a nhá»"
    },
    {
      "day": "day_after",
      "temp": 31,
      "condition": "náº¯ng"
    }
  ]
}
```

---

## 9. Cam káº¿t báº£o máº­t thÃ´ng tin
- File cáº¥u hÃ¬nh mÃ´i trÆ°á»ng `.env` chá»©a cÃ¡c API Key vÃ  credentials cÃ¡ nhÃ¢n Ä‘Ã£ Ä‘Æ°á»£c liá»‡t kÃª trong `.gitignore` vÃ  **tuyá»‡t Ä‘á»‘i khÃ´ng Ä‘Æ°á»£c commit hay push lÃªn GitHub repository**.
- Má»i vÃ­ dá»¥ trong tÃ i liá»‡u chá»‰ sá»­ dá»¥ng mock data hoáº·c token máº«u phá»¥c vá»¥ kiá»ƒm thá»­ an toÃ n (`dev-token-abc123`).

---

## 10. Bảng Checklist Nghiệm thu (Theo barem chấm điểm)

### 📌 Bài Trung bình
- [x] **Server chạy bằng Streamable HTTP:** FastMCP bind `0.0.0.0:8001/mcp`.
- [x] **Client kết nối được qua HTTP:** `auth_client.py` sử dụng `streamable_http_client`.
- [x] **Authentication đã được bật:** Kích hoạt qua `AuthSettings` và `StaticTokenVerifier`.
- [x] **Token hợp lệ gọi được tool:** Token `dev-token-abc123` kết nối và thực thi `get_weather("Hanoi")` thành công.
- [x] **Thiếu token bị từ chối:** Request không header trả về `HTTP 401 Unauthorized`.
- [x] **Token sai bị từ chối:** Request với token rác trả về `HTTP 401 Unauthorized`.
- [x] **Có thể truy cập từ máy khác trong LAN:** Server bind `0.0.0.0` cho phép các máy cùng mạng LAN truy cập qua IP LAN.

### 📌 Bài Khó
- [x] **Có thay đổi thật về tool hoặc response format:** Tool v1 trả string đơn giản (`"Hanoi: 29°C, trời mưa"`), Tool v2 trả JSON cấu trúc cao cấp kèm timestamp, độ ẩm, tốc độ gió, dự báo 2 ngày và chuyển đổi đơn vị độ C/độ F.
- [x] **Client cũ vẫn chạy:** Client v1 gọi `get_weather("Hanoi")` hoạt động bình thường, không bị breaking change.
- [x] **Client mới dùng được capability mới:** Client v2 gọi `get_weather_v2(..., include_forecast=True, units="fahrenheit")` nhận đầy đủ thông tin nâng cao.
- [x] **Có resource `server://info`:** Khai báo qua `@mcp.resource("server://info")`.
- [x] **`server://info` chứa metadata/version:** Trả về JSON gồm `name`, `version: 2.0.0`, `deprecated_tools` và `migration_guide`.
- [x] **Client mới đọc metadata trước khi chọn tool:** `versioned_client.py` gọi `session.read_resource("server://info")` và parse metadata trước khi quyết định gọi tool.