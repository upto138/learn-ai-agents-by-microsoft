# Phân Tích Lỗi Không Lưu Trữ Được Long-Term Memory 

Tài liệu này ghi chú lại một sự cố/lỗi hành vi bất thường gặp phải khi chạy notebook `13-agent-memory.ipynb` thuộc Lesson 13 (Agent Memory).

## 1. Bối Cảnh Xảy Ra
Trong quá trình thực hành khái niệm **Long-Term Memory** qua cơ chế Tool Calling, kịch bản (scenario) được xây dựng như sau:
- **Scenario 1**: Nhận thông tin chuyến đi (Kỷ niệm 10 năm ngày cưới, dị ứng đậu phộng, ăn chay, ngân sách 700-800$/đêm) và lưu vào `preference_store` (một in-memory dictionary) thông qua tool `save_preference`.
- **Scenario 2**: Trong một session hoàn toàn mới, Agent gọi tool `get_preferences` để lấy lại thông tin dài hạn của người dùng để tư vấn tiếp mà không cần hỏi lại.

Tuy nhiên, người dùng đã chủ động chỉnh sửa đoạn mã khởi tạo Agent. Đoạn code nguyên bản dùng `AzureAIProjectAgentProvider` bị comment lại và thay thế bằng `FoundryAgent`:

```python
# Code cũ (bị comment):
# travel_agent = await provider.create_agent(
#     tools=[save_preference, get_preferences],
#     name="TravelBookingAssistant",
#     ...
# )

# Code mới được thực thi:
travel_agent = FoundryAgent(
  name="TravelBookingAssistant",
  instructions=...,
  agent_name="TravelAvailabilityAgent", # Tên Agent trên Foundry
  tools=[save_preference, get_preferences],
  credential=AzureCliCredential(),
)
```

**Biểu hiện lỗi:**
1. Khi chạy kiểm tra biến `preference_store` bằng lệnh `print` ở Scenario 1, danh sách trả về hoàn toàn **rỗng**, không có preference nào được in ra. Dù trước đó Agent đã phản hồi rất tự tin: *"I'll save these now. I've saved your preferences..."*
2. Ở Scenario 2, thay vì sử dụng thông tin cũ đã nhớ, Agent lại hỏi lại từ đầu: *"Could you please confirm or update the following for your trip: Destination or city, Travel dates, Hotel preferences, Budget per night..."*. Cùng lúc đó, text hardcode trong Jupyter notebook vẫn in ra câu: *"💡 The agent retrieved Sarah's saved preferences from long-term memory..."* làm mâu thuẫn với câu trả lời của Agent.

## 2. Nguyên Nhân Gốc Rễ (Root Cause Analysis)

> Phần này được cập nhật sau khi đọc source code thực tế của `agent_framework_foundry` v1.4.0.

### 2.1. Kiến trúc `FoundryAgent` vs `FoundryChatClient` — Sự khác biệt cốt lõi

Trong Microsoft Agent Framework, có **hai cách** để gọi LLM trên Azure AI Foundry, mỗi cách có kiến trúc hoàn toàn khác nhau:

| | `Agent` + `FoundryChatClient` | `FoundryAgent` |
|---|---|---|
| **Vai trò** | Agent chạy **hoàn toàn ở local**. Client chỉ đóng vai trò gọi API chat completion. | Kết nối tới một **Prompt Agent / Hosted Agent đã được đăng ký trên Azure AI Foundry** |
| **Tool execution** | Framework tự quản lý vòng lặp tool calling: LLM trả về `tool_call` → framework gọi hàm Python local → gửi kết quả lại LLM | Gửi request lên server kèm `agent_reference`, server-side agent tự xử lý. Tools Python local **KHÔNG được gọi**. |
| **Yêu cầu `agent_name`** | ❌ Không cần | ✅ **Bắt buộc** — đọc từ tham số hoặc biến môi trường `FOUNDRY_AGENT_NAME` |

### 2.2. Tại sao tools Python không được gọi?

Khi dùng `FoundryAgent`, HTTP request gửi tới Azure có dạng:
```json
{
  "input": [ ... messages ... ],
  "extra_json": {
    "agent_reference": {
      "name": "TravelAvailabilityAgent",
      "type": "agent_reference"
    }
  }
}
```

Trường `agent_reference` báo cho server rằng: "*Hãy dùng Agent có tên `TravelAvailabilityAgent` đã được cấu hình trên Foundry portal để xử lý request này.*" Server-side agent này có instructions và tools riêng của nó trên cloud — nó **không biết gì** về các hàm Python (`save_preference`, `get_preferences`) đang chạy trên Jupyter Notebook của bạn.

Kết quả: LLM trả lời dựa trên kiến thức chung (general knowledge) mà không gọi tool → tạo ra **Hallucination** ("I've saved your preferences") → `preference_store` luôn rỗng.

### 2.3. Tại sao comment `agent_name` trong code Python mà vẫn khởi tạo thành công?

Source code của `RawFoundryAgentChatClient.__init__()` sử dụng hàm `load_settings()` với prefix `FOUNDRY_`:
```python
settings = load_settings(
    FoundryAgentSettings,
    env_prefix="FOUNDRY_",
    agent_name=agent_name,    # ← Nếu None (bạn comment rồi)
    ...
)
agent_name_setting = settings.get("agent_name")
if not agent_name_setting:
    raise ValueError("Agent name is required...")  # ← Sẽ raise lỗi nếu không tìm thấy
```

Nhưng trong file `.env` của bạn có dòng:
```
FOUNDRY_AGENT_NAME="TravelAvailabilityAgent"
```

→ Khi bạn comment `agent_name` trong code Python, `load_settings()` vẫn **tự động đọc** từ biến môi trường `FOUNDRY_AGENT_NAME` và dùng giá trị `"TravelAvailabilityAgent"`. Kết quả là `FoundryAgent` vẫn khởi tạo thành công và vẫn kết nối tới server-side agent.

### 2.4. Chuỗi lỗi dây chuyền

```
FoundryAgent + agent_name (từ code HOẶC .env)
  └─→ Gửi request với agent_reference lên server
       └─→ Server-side agent KHÔNG biết về local Python tools
            └─→ LLM hallucinate "I've saved your preferences"
                 └─→ preference_store luôn rỗng
                      └─→ Scenario 2: get_preferences() trả về rỗng
                           └─→ Agent hỏi lại từ đầu
```

### 2.5. Mâu thuẫn Output

Dòng `"💡 The agent retrieved Sarah's saved preferences..."` không phải do Agent sinh ra, mà là lệnh `print(...)` được code cứng (hardcode) trong Jupyter Notebook. Nó luôn in ra bất kể Agent có thực sự nhớ thông tin hay không, gây bối rối khi debug.

## 3. Cách Khắc Phục

### Cách 1 — Khuyến Nghị: Dùng `provider.create_agent()` (Code gốc của bài học)

Khôi phục lại đoạn code nguyên bản. `AzureAIProjectAgentProvider` tạo agent **chạy hoàn toàn ở local** với vòng lặp tool calling tự động, đảm bảo các hàm Python được gọi đúng cách.

```python
provider = AzureAIProjectAgentProvider(credential=AzureCliCredential())

travel_agent = await provider.create_agent(
    tools=[save_preference, get_preferences, search_hotels],
    name="TravelBookingAssistant",
    instructions=(
        "You are a personalized travel booking assistant with long-term memory.\n"
        "WORKFLOW:\n"
        "1. When a user starts a conversation, call get_preferences() to check for saved information.\n"
        "2. Store any new preferences the user mentions using save_preference().\n"
        "3. Use search_hotels() to find suitable options that match their preferences and budget.\n"
        "4. Do NOT recommend hotels that exceed the user's budget.\n\n"
        "IMPORTANT: Always use user_id='sarah_johnson_123' for all memory operations."
    ),
)
```

### Cách 2 — Dùng `Agent` + `FoundryChatClient` (Thay thế cho FoundryAgent)

Nếu bạn **không muốn** dùng `AzureAIProjectAgentProvider` (tức là muốn tránh dùng Agent Service V2), bạn có thể dùng class `Agent` kết hợp với `FoundryChatClient`.

`FoundryChatClient` kế thừa `FunctionInvocationLayer` — nó có khả năng **tự động gọi local Python functions** khi LLM trả về tool_call, giống như cách OpenAI client xử lý. Còn `Agent` là wrapper cung cấp session, middleware, v.v.

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

foundry_client = FoundryChatClient(
    credential=AzureCliCredential(),
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL"),
)

travel_agent = Agent(
    name="TravelBookingAssistant",
    instructions=(
        "You are a personalized travel booking assistant with long-term memory.\n"
        "WORKFLOW:\n"
        "1. When a user starts a conversation, call get_preferences() to check for saved information.\n"
        "2. Store any new preferences the user mentions using save_preference().\n"
        "3. Use search_hotels() to find suitable options that match their preferences and budget.\n"
        "4. Do NOT recommend hotels that exceed the user's budget.\n\n"
        "IMPORTANT: Always use user_id='sarah_johnson_123' for all memory operations."
    ),
    client=foundry_client,
    tools=[save_preference, get_preferences, search_hotels],
)
```

**Tại sao cách này hoạt động?**
- `FoundryChatClient` **KHÔNG dùng `agent_reference`** — nó gọi trực tiếp Chat Completion API kèm tool schemas.
- Khi LLM trả về `tool_call`, `FunctionInvocationLayer` trong `FoundryChatClient` sẽ **tự động gọi hàm Python local** tương ứng (ví dụ `save_preference()`).
- Kết quả của hàm được gửi ngược lại cho LLM để tiếp tục cuộc hội thoại.

### ⚠️ Tại sao `FoundryAgent` KHÔNG thể chạy local tools?

`FoundryAgent` **luôn yêu cầu `agent_name`** (bắt buộc). Nếu bạn không truyền vào trong code, nó sẽ đọc từ biến môi trường `FOUNDRY_AGENT_NAME`. Nếu cả hai đều không có, nó sẽ raise `ValueError`.

Điều này có nghĩa: **không có cách nào** dùng `FoundryAgent` mà không kết nối tới một server-side agent, và server-side agent không thể gọi local Python functions. Vì vậy, `FoundryAgent` **không phù hợp** cho bài lab này.

## 4. Bài Học Rút Ra & Lưu Ý
- **Phân biệt `FoundryAgent` và `Agent` + `FoundryChatClient`:** Đây là hai kiến trúc hoàn toàn khác nhau. `FoundryAgent` = server-side agent (tools trên cloud). `Agent` + `FoundryChatClient` = local agent (tools trên máy tính). Chọn đúng kiến trúc theo nhu cầu.
- **Cẩn thận với biến môi trường `.env`:** Framework tự động đọc `FOUNDRY_AGENT_NAME` từ `.env`. Nếu bạn comment `agent_name` trong code nhưng quên xoá trong `.env`, hành vi sẽ không thay đổi. Luôn kiểm tra cả file `.env` khi debug.
- **Cảnh giác với "Hallucination":** Không bao giờ tin 100% vào việc LLM bảo "Tôi đã làm việc đó rồi". Luôn cần có các cơ chế log / kiểm tra tính toàn vẹn của dữ liệu (giống như đoạn code in `preference_store` ra màn hình) để xác minh tool có thực sự được gọi hay không.
- **Cẩn thận khi đọc file Notebook:** Các dòng `print` tĩnh trong Notebook có thể làm đánh lạc hướng việc Debugging vì nó in ra dựa trên giả định (Happy path) của người viết bài học chứ không phụ thuộc vào State thực tế.
- **Bật Debug Logging:** Thêm `logging.basicConfig(level=logging.DEBUG)` vào đầu notebook để xem HTTP request/response thực tế. Bạn sẽ thấy rõ `agent_reference` trong request body — bằng chứng cho việc request đang được chuyển tiếp tới server-side agent.

## 5. Các Lesson Khác Cũng Bị Ảnh Hưởng Bởi Cùng Lỗi

Lỗi `FoundryAgent` không gọi được local Python tools **không chỉ xảy ra ở Lesson 13**. Sau khi kiểm tra toàn bộ các notebook đã chạy trong khoá học, phát hiện ra rằng **Lesson 02, 03, và 04** đều mắc cùng một vấn đề vì tất cả đều được chỉnh sửa để dùng `FoundryAgent` + `agent_name="TravelAvailabilityAgent"` thay cho `provider.create_agent()`.

---

### 5.1. Lesson 02 — `02-python-agent-framework.ipynb`

**Code bị ảnh hưởng:**
```python
agent = FoundryAgent(
  name="TravelAvailabilityAgent",
  instructions=...,
  agent_name="TravelAvailabilityAgent",
  tools=[check_destination_availability],
  credential=AzureCliCredential(),
)
```

**Tool được định nghĩa:**
Hàm `check_destination_availability()` chỉ biết 5 điểm đến: `Barcelona, Tokyo, Cape Town, Vancouver, Dubai`.

**Output thực tế (hallucinated):**
> *"Rome, Italy – Famous for its historical landmarks... Tokyo, Japan – A bustling city... Prague, Czech Republic... Bali, Indonesia... London, United Kingdom... Dubai, UAE... Maui, Hawaii... Paris, France... New York City, USA... Santorini, Greece..."*

**Bằng chứng hallucination:** Agent liệt kê ra 10 điểm đến — trong khi hàm `check_destination_availability()` chỉ biết 5 điểm. Đặc biệt các địa danh như Rome, Prague, Bali, London, Maui, Paris, NYC, Santorini **hoàn toàn không tồn tại** trong dữ liệu tool. Điều này chứng minh tool KHÔNG được gọi — Agent tự bịa từ kiến thức chung của LLM.

---

### 5.2. Lesson 03 — `03-python-agent-framework.ipynb`

Lesson 03 bao gồm 3 design patterns, trong đó **2 patterns** bị ảnh hưởng:

#### Pattern 2: Structured Output

**Code bị ảnh hưởng:**
```python
structured_agent = FoundryAgent(
  name="StructuredTravelExpert",
  instructions="...Use the get_destination_details tool.",
  tools=[get_destination_details],
  agent_name="TravelAvailabilityAgent",
  credential=AzureCliCredential(),
)
```

**Tool được định nghĩa:**
Hàm `get_destination_details()` chỉ biết 3 điểm đến: `Barcelona, Tokyo, Cape Town`.

**Output thực tế (hallucinated):**
> *"1. Kyoto, Japan – rich in traditional temples, gardens, and tea houses. 2. Rome, Italy – a city full of ancient history, art... 3. Marrakech, Morocco – vibrant markets, historical palaces..."*

**Bằng chứng hallucination:** Cả 3 điểm đến được trả về (Kyoto, Rome, Marrakech) đều **KHÔNG có** trong dữ liệu của tool. Tool chỉ biết Barcelona, Tokyo, Cape Town. Agent tự bịa ra cả kết quả.

#### Pattern 3: Single Responsibility Agents

**Code bị ảnh hưởng:**
```python
destination_agent = FoundryAgent(
  name="DestinationExpert",
  instructions="...Check availability using the provided tool...",
  agent_name="TravelAvailabilityAgent",
  credential=AzureCliCredential(),
  # Lưu ý: KHÔNG truyền tools=[] vào đây!
)
```

**Vấn đề kép:** Agent được yêu cầu "Check availability using the provided tool" trong instructions, nhưng:
1. Không có `tools=[...]` được truyền vào.
2. Dù có truyền, `FoundryAgent` cũng không thể gọi local tools (như đã phân tích ở trên).

---

### 5.3. Lesson 04 — `04-python-agent-framework.ipynb`

**Code bị ảnh hưởng:**
```python
agent = FoundryAgent(
  name="TravelAvailabilityAgent",
  instructions="You are a travel agent. Use the available tools...",
  agent_name="TravelAvailabilityAgent",
  tools=[get_destinations, check_availability, get_flight_info],
  credential=AzureCliCredential(),
)
```

**Tools được định nghĩa:**
- `get_destinations()` → trả về: `["Barcelona", "Paris", "Berlin", "Tokyo", "Sydney", "New York City"]`
- `check_availability()` → trả về trạng thái cho đúng 6 điểm đến trên.
- `get_flight_info()` → trả về thông tin cho 3 chuyến bay cụ thể (`LHR-BCN`, `LHR-CDG`, `LHR-NRT`).

**Output thực tế (hallucinated):**
> *"Malaga, Spain (Costa del Sol)... Alicante, Spain... Faro, Portugal (Algarve region)... Naples, Italy... Athens, Greece... Nice, France..."*

**Bằng chứng hallucination:**
- Không một điểm đến nào trong output (`Malaga, Alicante, Faro, Naples, Athens, Nice`) khớp với dữ liệu tool.
- Debug log xác nhận HTTP request **KHÔNG chứa trường `tools`** — chỉ có `input` (messages) và `agent_reference`. Điều này chứng minh framework không gửi tool schemas lên server khi dùng `FoundryAgent`.

**Thêm bằng chứng từ Structured Output section (cùng lesson 04):**
Kết quả tương tự — Agent trả về danh sách "British Airways, easyJet" cho các chuyến bay bịa ra, hoàn toàn không khớp với dữ liệu trong hàm `get_flight_info()`.

---

### 5.4. Tổng kết ảnh hưởng

| Lesson | Notebook | Tools truyền vào | Tools thực sự được gọi? | Mức độ hallucination |
|---|---|---|---|---|
| **02** | `02-python-agent-framework.ipynb` | `check_destination_availability` | ❌ Không | Bịa ra 10 điểm đến, chỉ 2/10 trùng tên với dữ liệu tool |
| **03** | `03-python-agent-framework.ipynb` | `get_destination_details` | ❌ Không | Bịa ra 3 điểm đến, 0/3 có trong dữ liệu tool |
| **04** | `04-python-agent-framework.ipynb` | `get_destinations`, `check_availability`, `get_flight_info` | ❌ Không | Bịa ra 6 điểm đến + hãng bay, 0/6 có trong dữ liệu tool |
| **13** | `13-agent-memory.ipynb` | `save_preference`, `get_preferences` | ❌ Không | Tuyên bố "đã lưu" nhưng dictionary luôn rỗng |

> **Kết luận:** Tất cả các lesson sử dụng `FoundryAgent` + `agent_name` kèm local Python tools đều bị ảnh hưởng bởi cùng một vấn đề kiến trúc. Giải pháp là chuyển sang dùng `provider.create_agent()` hoặc `Agent` + `FoundryChatClient` (xem [Phần 3](#3-cách-khắc-phục)).
