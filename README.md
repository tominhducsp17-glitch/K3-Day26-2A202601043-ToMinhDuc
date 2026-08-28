# K3 Day 26 — Model Context Protocol (MCP) Server & Agent Integration

Báo cáo nghiệm thu & hướng dẫn chạy bài Lab Day 26 cho cả 3 cấp độ: **Cơ bản**, **Trung bình** và **Khó**.

---

## 1. Mô tả công việc thực tế mà MCP Server giải quyết

Trong thực tế, các Large Language Model (LLM) như Claude, Gemini hay GPT bị giới hạn bởi:
1. **Dữ liệu tĩnh (cutoff date):** Không thể biết thời tiết, nhiệt độ hay thiên tai đang diễn ra thời gian thực.
2. **Nguy cơ Hallucination (bịa đặt):** Khi người dùng hỏi thời tiết, LLM dễ tự suy diễn thông tin sai lệch gây nguy hiểm cho kế hoạch di chuyển, du lịch, logistics hoặc nông nghiệp.

**Giải pháp:**  
Hệ thống **Weather MCP Server** được xây dựng nhằm cung cấp chuẩn kết nối mở **Model Context Protocol (MCP)** giữa AI Agent và các trạm khí tượng thủy văn thời gian thực:
- Cho phép AI Agent tự động khám phá năng lực (Tool Discovery) mà không cần hard-code logic vào ứng dụng.
- Cung cấp dữ liệu nhiệt độ, độ ẩm, sức gió, chỉ số UV, tầm nhìn và dự báo thời tiết nhiều ngày theo thời gian thực tế.
- Hỗ trợ triển khai linh hoạt qua cả **Stdio** (local) lẫn **Streamable HTTP** (mạng phân tán, cloud deployment).

---

## 2. Mô tả Input / Output chi tiết của từng Tool

### A. Hệ thống Weather Agent chính (`04-lab/mcp-server/weather.py`)

| Tên Tool | Tham số đầu vào (Input) | Kiểu dữ liệu | Bắt buộc | Mô tả & Ví dụ đầu ra (Output) |
|---|---|---|:---:|---|
| `get_current_weather` | `city` | `str` | Có | **Input:** Tên thành phố bất kỳ trên thế giới (ví dụ: `"Hanoi"`, `"Danang"`, `"Tokyo"`).<br>**Output:** Chuỗi báo cáo chi tiết gồm: Nhiệt độ (°C/°F), Nhiệt độ cảm nhận, Tình trạng mây, Độ ẩm %, Tốc độ gió, Hướng gió, Áp suất khí quyển (mb), Chỉ số UV, Tầm nhìn (km), Thời gian cập nhật. |
| `get_forecast` | `city`<br>`days` | `str`<br>`int` | Có<br>Không (mặc định = 3) | **Input:** Tên thành phố và số ngày dự báo (tối đa 3 ngày).<br>**Output:** Báo cáo dự báo từng ngày gồm: Nhiệt độ cao nhất/thấp nhất, Tình trạng thời tiết, Xác suất có mưa (%), Tốc độ gió tối đa, Chỉ số UV. |
| `health_check` | Không có | — | — | **Output:** Chuỗi xác nhận server MCP đang hoạt động ổn định và sẵn sàng phục vụ. |

### B. Hệ thống Versioned MCP Server (`03-production/versioned_server.py`)

| Tên Tool | Phiên bản | Tham số đầu vào (Input) | Mô tả đầu ra (Output) |
|---|:---:|---|---|
| `get_weather` | **v1** (Legacy) | `city: str` | Trả về chuỗi rút gọn cho client cũ: `Hanoi: 29°C, trời mưa` |
| `get_weather_v2` | **v2** (Modern) | `city: str`<br>`include_forecast: bool = False`<br>`units: str = "celsius"` | Trả về JSON chuẩn hóa v2.0 có timestamp UTC, kèm mảng dự báo nếu bật `include_forecast=True` và chuyển đổi đơn vị (`celsius`/`fahrenheit`). |

---

## 3. Cấu trúc thư mục Repository

```text
├── 01-function-calling/          # So sánh Function Calling thuần với Gemini SDK
├── 02-mcp-basics/               # MCP Server cơ bản chạy qua Stdio Transport
│   ├── weather_server.py        # FastMCP Server stdio
│   └── weather_client.py        # Client tự khám phá và gọi tool qua stdio
├── 03-production/               # Kỹ thuật Production: Auth, Versioning, Registry
│   ├── auth_server.py           # [Bài Trung bình] Streamable HTTP + Bearer Token Auth
│   ├── auth_client.py           # [Bài Trung bình] Client xác thực token hợp lệ/không hợp lệ
│   ├── versioned_server.py      # [Bài Khó] Versioning v1/v2 + Resource server://info
│   └── versioned_client.py      # [Bài Khó] Client đọc metadata trước khi gọi tool v1 & v2
├── 04-lab/                      # [Bài Lab hoàn chỉnh] Weather Agent với Google ADK
│   ├── mcp-server/weather.py    # FastMCP Server chạy Streamable HTTP (Port 8085)
│   ├── mcp-client/
│   │   ├── weather_agent/agent.py # Agent kết nối qua StreamableHTTPConnectionParams
│   │   └── verify_setup.py      # Kịch bản kiểm thử tự động toàn bộ môi trường
│   └── VERIFICATION.md          # Bằng chứng nghiệm thu kết quả kiểm thử
└── README.md                    # Tài liệu hướng dẫn nộp bài tổng hợp
```

---

## 4. Hướng dẫn cài đặt và chạy (Quickstart)

### Bước 1: Chuẩn bị môi trường & Cài đặt thư viện
Yêu cầu Python >= 3.10. Bạn có thể sử dụng `uv` hoặc `pip`:

```bash
# Cài đặt thư viện cho bài lab
cd 04-lab/mcp-client
uv sync
# Hoặc cài đặt tổng quát:
pip install -r requirements.txt
```

### Bước 2: Cấu hình biến môi trường
Tạo file `.env` tại thư mục `04-lab/mcp-client/.env` và `04-lab/mcp-server/.env`:
```bash
GOOGLE_API_KEY=your_gemini_api_key_here
WEATHERAPI_KEY=your_weatherapi_key_here
```
*(Lưu ý: Nếu không có key WeatherAPI, server tích hợp sẵn cơ chế Live Meteorology Fallback tự động lấy dữ liệu thời tiết thực tế từ Open-Meteo).*

### Bước 3: Khởi động MCP Server và ADK Agent
Mở 2 cửa sổ terminal:

- **Terminal 1 (Chạy MCP Server Streamable HTTP):**
  ```bash
  cd 04-lab/mcp-server
  uv run python weather.py
  # Server lắng nghe tại: http://0.0.0.0:8085/mcp
  ```

- **Terminal 2 (Chạy ADK Agent Web UI hoặc CLI):**
  ```bash
  cd 04-lab/mcp-client
  # Khởi động giao diện Web trực quan:
  uv run adk web --port 8000
  # Mở trình duyệt: http://localhost:8000 và chọn "weather_agent"
  ```

---

## 5. Hướng dẫn đăng ký MCP Server với Claude Code

Bạn có thể đăng ký Weather MCP Server vào **Claude Code** theo 2 cách:

### Cách 1: Đăng ký qua Stdio Transport (Khuyên dùng khi chạy local)
```bash
claude mcp add weather -- python "02-mcp-basics/weather_server.py"
```

### Cách 2: Đăng ký qua Streamable HTTP Transport (Khi server đang chạy ở port 8085)
```bash
claude mcp add weather-http --url http://localhost:8085/mcp
```

### Kiểm tra đăng ký thành công trong Claude Code:
```bash
claude mcp list
```
Claude Code sẽ liệt kê `weather` với các tools: `get_current_weather`, `get_forecast`, `health_check`. Bạn có thể trực tiếp gõ vào Claude Code: *"Thời tiết ở Hà Nội hôm nay thế nào?"* và Claude Code sẽ tự động gọi MCP server để trả lời.

---

## 6. Bằng chứng & Kiểm tra Tool chạy được (BÀI CƠ BẢN)

### Kịch bản 1: Kiểm thử tự động với `verify_setup.py`
Chạy lệnh:
```bash
cd 04-lab/mcp-client
uv run python verify_setup.py
```
**Kết quả thực tế:**
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

### Kịch bản 2: Chạy trực tiếp qua CLI với câu hỏi tiếng Việt
```bash
uv run adk run weather_agent "Thời tiết hiện tại ở Đà Nẵng thế nào?"
```
**Phản hồi thực tế từ Agent:**
> `[weather_agent]: Thời tiết hiện tại ở Đà Nẵng, Việt Nam là 37.4°C (99.3°F), cảm giác như 41.2°C (106.2°F). Tình trạng nhiều mây, độ ẩm 38%, gió 9.9 km/h.`

---

## 7. Phần nâng cao: BÀI TRUNG BÌNH (Streamable HTTP + Token Authentication)

Mã nguồn tại thư mục: `03-production/auth_server.py` và `03-production/auth_client.py`.

### A. Cơ chế bảo mật
Server chạy giao thức **Streamable HTTP** kèm middleware `TokenVerifier`. Mọi request phải mang theo header:
```text
Authorization: Bearer dev-token-abc123
```
Nếu token sai hoặc thiếu, server trả về mã lỗi chuẩn `401 Unauthorized` kèm header `WWW-Authenticate: Bearer error="invalid_token"`.

### B. Hướng dẫn Test Token ĐÚNG
1. Khởi động server xác thực tại Terminal 1:
   ```bash
   cd 03-production
   python auth_server.py
   # Lắng nghe tại: http://localhost:8001/mcp
   ```
2. Chạy client với token hợp lệ tại Terminal 2:
   ```bash
   python auth_client.py dev-token-abc123
   ```
   **Kết quả:**
   ```text
   [AUTH SUCCESS] Connected with token: 'dev-token-abc123'
   Available tools:
     - get_weather: Lấy thời tiết hiện tại của một thành phố.
   Result: Hanoi: 29°C, trời mưa
   ```

### C. Hướng dẫn Test Token SAI / THIẾU TOKEN

- **Test Token SAI bằng client:**
  ```bash
  python auth_client.py wrong-token-xyz
  # Kết quả: [AUTH REJECTED] Connection rejected (401 Unauthorized)
  ```
- **Test Token SAI bằng curl:**
  ```bash
  curl -i -X POST http://localhost:8001/mcp \
    -H "Authorization: Bearer wrong-token" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json, text/event-stream" \
    -d "{}"
  ```
  **Kết quả server trả về:**
  ```http
  HTTP/1.1 401 Unauthorized
  www-authenticate: Bearer error="invalid_token", error_description="Authentication required"

  {"error": "invalid_token", "error_description": "Authentication required"}
  ```

- **Test THIẾU TOKEN bằng client:**
  ```bash
  python auth_client.py NONE
  # Kết quả: [AUTH REJECTED] Connection rejected
  ```
- **Test THIẾU TOKEN bằng curl:**
  ```bash
  curl -i -X POST http://localhost:8001/mcp -d "{}"
  # Kết quả: HTTP/1.1 401 Unauthorized
  ```

---

## 8. Phần nâng cao: BÀI KHÓ (Versioning, Backward Compatibility & Resource `server://info`)

Mã nguồn tại thư mục: `03-production/versioned_server.py` và `03-production/versioned_client.py`.

### A. Các kỹ thuật triển khai
1. **Tool mới song song:** Giữ nguyên tool v1 (`get_weather`) cho client cũ, đồng thời phát triển tool v2 (`get_weather_v2`) trả về cấu trúc JSON giàu dữ liệu hơn.
2. **Tham số optional với giá trị default:** `include_forecast: bool = False`, `units: str = "celsius"` để tránh làm gãy schema của client.
3. **Resource `server://info`:** Công bố phiên bản server `2.0.0`, danh sách tool đã bị deprecated (`['get_weather']`) và cẩm nang di chuyển `migration_guide`.
4. **Client đọc metadata trước khi gọi tool:** Client chủ động truy vấn `session.read_resource("server://info")` để kiểm tra trạng thái trước khi tương tác.

### B. Hướng dẫn chạy và nghiệm thu
Chạy client nghiệm thu phiên bản:
```bash
cd 03-production
python versioned_client.py
```
**Kết quả thực tế hiển thị đầy đủ:**
```text
Server: weather-v2 v2.0.0
Deprecated tools: ['get_weather']
Migration: Chuyển từ get_weather sang get_weather_v2. Tham số 'city' giữ nguyên, thêm include_forecast và units.

Tools:
  - get_weather: [v1] Lấy thời tiết hiện tại — trả chuỗi đơn giản. Deprecated, dùng get_weather_v2.
  - get_weather_v2: [v2] Lấy thời tiết chi tiết — JSON, hỗ trợ forecast và đơn vị đo.

[v1] get_weather('Hanoi'):
  Hanoi: 29°C, trời mưa

[v2] get_weather_v2('Hanoi', forecast=True):
{
  "api_version": "2.0",
  "city": "Hanoi",
  "temp": 29,
  "units": "celsius",
  "condition": "trời mưa",
  "humidity": 82,
  "wind_speed_kmh": 12,
  "timestamp": "2026-08-28T07:01:34+00:00",
  "forecast": [
    {
      "day": "tomorrow",
      "temp": 27,
      "condition": "mưa nhỏ"
    },
    {
      "day": "day_after",
      "temp": 31,
      "condition": "nắng"
    }
  ]
}
```

---

## 9. Cam kết bảo mật thông tin
- File cấu hình môi trường `.env` chứa các API Key và credentials cá nhân đã được liệt kê trong `.gitignore` và **tuyệt đối không được commit hay push lên GitHub repository**.
- Mọi ví dụ trong tài liệu chỉ sử dụng mock data hoặc token mẫu phục vụ kiểm thử an toàn (`dev-token-abc123`).