# Implementation Plan — Advisor Agent

> **Ngày tạo:** 2026-05-17  
> **Mục tiêu:** Tổng hợp toàn bộ thông tin cần thiết từ project hiện tại để triển khai **Advisor Agent** — agent thứ 3 trong pipeline `Researcher → Planner → [Advisor] → Application`.

---

## 1. Tổng quan kiến trúc (từ `architecture.md`)

### 1.1 Vị trí của Advisor trong Pipeline

```
Researcher Agent → Planner Agent → ★ Advisor Agent ★ → Application Agent
```

- **Input nhận được:** Kết quả từ **Researcher** (`ResearchResult`) và **Planner** (`PlanResult`), cùng với `StudentProfile`.
- **Output trả ra:** Ghi vào `state.advisor_response` (hiện tại là `str`).
- **Tool sử dụng:** `LLM Reasoning` (theo architecture diagram). Advisor **không cần** Web Scraper hay Browser Automation.
- **Service tương tác:** `LLM Service` + `Memory Service` (theo execution flow diagram).

### 1.2 Vai trò của Advisor

Theo architecture, Advisor Agent có nhiệm vụ: **"Explains plan, gives guidance"** — tức là:
- Giải thích kế hoạch tuyển sinh (từ Planner) bằng ngôn ngữ dễ hiểu cho học sinh.
- Đưa ra lời khuyên / hướng dẫn cá nhân hóa dựa trên hồ sơ học sinh.
- Tổng hợp rủi ro và đưa ra khuyến nghị hành động.

---

## 2. Dữ liệu Input — Output format của Researcher & Planner

### 2.1 Output của Researcher Agent → `ResearchResult`

> **File:** `backend/app/schemas/agent_state.py` (dòng 48-57)

```python
class ResearchResult(BaseModel):
    query: str = ""
    universities: List[UniversityInfo] = []      # Danh sách trường/ngành
    general_requirements: List[str] = []          # Yêu cầu chung
    important_deadlines: Dict[str, str] = {}      # Mốc thời gian quan trọng
    admission_methods: List[str] = []             # Phương thức xét tuyển
    raw_summary: str = ""                         # Tóm tắt ngắn gọn
    sources: List[str] = []                       # Danh sách URL nguồn
    researched_at: Optional[datetime] = None
```

**Chi tiết `UniversityInfo`** (dòng 34-45):

```python
class UniversityInfo(BaseModel):
    university_name: str
    major: str
    benchmark_score: Optional[float] = None       # Điểm chuẩn
    admission_method: str = ""                     # Phương thức tuyển (THPTQG, ĐGNL...)
    required_documents: List[str] = []             # Giấy tờ yêu cầu
    deadline: Optional[str] = None                 # Hạn nộp (YYYY-MM-DD hoặc None)
    tuition_fee: Optional[str] = None              # Học phí
    website: Optional[str] = None                  # Website trường
    source_url: Optional[str] = None               # URL nguồn dữ liệu
    notes: str = ""                                # Ghi chú bổ sung
```

### 2.2 Output của Planner Agent → `PlanResult`

> **File:** `backend/app/schemas/agent_state.py` (dòng 92-106)

```python
class PlanResult(BaseModel):
    missing_questions: List[str] = []             # Câu hỏi cần hỏi thêm học sinh
    checklist: List[ChecklistItem] = []           # Danh sách hồ sơ cần chuẩn bị
    timeline: List[TimelineTask] = []             # Timeline hành động
    risks: List[str] = []                         # Rủi ro được phát hiện
    needs_human_confirmation: bool = False        # Cần xác nhận từ người dùng?
```

**Chi tiết `ChecklistItem`** (dòng 64-78):

```python
class ChecklistItem(BaseModel):
    title: str                                     # Tên giấy tờ / hành động
    status: str = "pending"                        # ready | pending | need_review
    required: bool = True                          # Bắt buộc?
    reason: str = ""                               # Lý do cần
    source: str = ""                               # admission_news | rag | student_profile | inferred
```

**Chi tiết `TimelineTask`** (dòng 81-89):

```python
class TimelineTask(BaseModel):
    date: Optional[str] = None                     # ISO date hoặc None
    task: str                                      # Mô tả việc cần làm
    priority: str = "medium"                       # high | medium | low
    reason: str = ""                               # Lý do ưu tiên
```

### 2.3 Student Profile (Input chung cho tất cả agents)

> **File:** `backend/app/schemas/agent_state.py` (dòng 23-31)

```python
class StudentProfile(BaseModel):
    name: str = ""
    gpa: Optional[float] = None
    target_scores: Dict[str, float] = {}          # {"Toán": 9.0, "Lý": 8.5}
    preferred_majors: List[str] = []
    preferred_universities: List[str] = []
    extra_activities: List[str] = []
    notes: str = ""
```

### 2.4 Advisor Output Slot trong AgentState

> **File:** `backend/app/schemas/agent_state.py` (dòng 129-165)

```python
class AgentState(BaseModel):
    # ...
    # Agent outputs (filled in gradually along the pipeline)
    research_result: Optional[ResearchResult] = None
    plan_result: Optional[PlanResult] = None
    admission_plan: Optional[AdmissionPlan] = None   # legacy
    advisor_response: str = ""                        # ← ADVISOR GHI VÀO ĐÂY
    application_status: str = ""

    # HITL (Human-in-the-Loop)
    requires_confirmation: bool = False
    confirmation_payload: Optional[Dict[str, Any]] = None

    # Metadata
    errors: List[str] = []
    current_agent: str = ""
    completed_agents: List[str] = []
```

> **⚠️ LƯU Ý QUAN TRỌNG:**  
> Hiện tại `advisor_response` là `str`. Có thể cần nâng cấp thành một Pydantic model riêng (`AdvisorResult`) nếu muốn output có cấu trúc (structured JSON) giống Researcher/Planner.

---

## 3. Các pattern hiện có cần tuân theo

### 3.1 Base Agent Interface

> **File:** `backend/app/agents/base.py`

Mọi agent phải kế thừa `BaseAgent` và implement:

```python
class BaseAgent(ABC):
    name: str = "base_agent"
    description: str = "Base agent"

    def __init__(self, verbose: bool = False): ...

    @abstractmethod
    async def run(self, state: AgentState) -> AgentState: ...

    def log(self, message: str, level: str = "info") -> None: ...
```

### 3.2 Pattern chung của Researcher & Planner (cần follow)

Cả hai agent hiện tại đều tuân theo pattern giống nhau:

| Bước | Mô tả | Hàm / Method |
|------|--------|---------------|
| 1 | Load system prompt từ file `.txt` | `_load_prompt()` → đọc `prompts/<agent_name>.txt` |
| 2 | Build user message từ AgentState | `_build_user_message(state)` → format context cho LLM |
| 3 | Lazy-init FoundryChatClient agent | `_get_agent()` → dùng `FoundryChatClient.as_agent()` |
| 4 | Gọi `agent.run(message)` | Framework tự xử lý tool calls |
| 5 | Parse response text → Pydantic model | `_parse_<result>(raw_text)` |
| 6 | Ghi kết quả vào `state` | `state.<field> = result` |
| 7 | Mark agent done | `state.mark_agent_done(self.name)` |
| 8 | Hỗ trợ streaming | `run_stream()` method |

### 3.3 Tech Stack & Dependencies

| Component | Thư viện | Cách dùng |
|-----------|----------|-----------|
| Agent Framework | `agent_framework` (Microsoft) | `FoundryChatClient`, `@tool`, `Agent` |
| LLM Backend | Azure AI Foundry | `FOUNDRY_PROJECT_ENDPOINT`, model `gpt-4o-admission` |
| Credential | `azure.identity` | `DefaultAzureCredential` / `AzureCliCredential` |
| Schema | `pydantic.BaseModel` | Tất cả schemas trong `agent_state.py` |
| RAG | `rag_tool.py` | `query_knowledge_base()` — có thể dùng cho Advisor |

### 3.4 Cách đăng ký Tools

```python
# Researcher
ALL_RESEARCHER_TOOLS = ALL_SEARCH_TOOLS + ALL_RAG_TOOLS

# Planner
ALL_PLANNER_TOOLS = PlannerToolset.tools  # = ALL_RAG_TOOLS
```

Advisor theo architecture chỉ dùng **LLM Reasoning**, nhưng có thể cần `query_knowledge_base` để truy vấn thêm ngữ cảnh cho lời khuyên. Quyết định này cần cân nhắc.

---

## 4. Workflow Integration — Nơi cần chỉnh sửa

### 4.1 File `chat_workflow.py`

> **File:** `backend/app/workflows/chat_workflow.py`

Hiện tại đã có placeholder cho Advisor:

```python
# ── Bước 3: Advisor (TODO) ───────────────────────────────────
# from app.agents.advisor import AdvisorAgent
# state = await AdvisorAgent(verbose=self.verbose).run(state)
```

**Cần thực hiện:**
1. Import `AdvisorAgent` từ `app.agents.advisor`
2. Thêm `self.advisor = AdvisorAgent(verbose=verbose)` vào `__init__`
3. Uncomment và điều chỉnh logic chạy Advisor sau Planner
4. Xử lý guard condition: Advisor chỉ chạy khi `plan_result` tồn tại VÀ không có `missing_questions` chưa được trả lời (hoặc tùy logic HITL)

### 4.2 File `main.py` — API Response

> **File:** `backend/app/main.py`

Cần cập nhật `ResearchResponse` schema để bao gồm output của Advisor:
- Thêm field `advisor_response` (hoặc `advisor_result` nếu dùng structured output)
- Cập nhật logic trong route `/chat` để serialize advisor output

---

## 5. Các file cần tạo mới cho Advisor Agent

### 5.1 Danh sách file

| File | Vị trí | Mô tả |
|------|--------|--------|
| `advisor.py` | `backend/app/agents/advisor.py` | Logic chính của Advisor Agent |
| `advisor.txt` | `backend/app/prompts/advisor.txt` | System prompt cho LLM |

### 5.2 Schema mới (nếu cần structured output)

Nếu quyết định nâng cấp `advisor_response: str` thành structured output, cần thêm vào `agent_state.py`:

```python
class AdvisorResult(BaseModel):
    """Output đầy đủ của AdvisorAgent."""
    summary: str = ""                              # Tóm tắt tình hình tuyển sinh
    personalized_advice: List[str] = []            # Lời khuyên cá nhân hóa
    risk_analysis: List[str] = []                  # Phân tích rủi ro
    action_recommendations: List[str] = []         # Khuyến nghị hành động cụ thể
    encouragement: str = ""                        # Lời động viên / khích lệ
    next_steps: List[str] = []                     # Bước tiếp theo
    confidence_level: str = "medium"               # high | medium | low
```

> **📝 GHI CHÚ:**  
> Đây là **đề xuất** schema. Có thể giữ `advisor_response: str` nếu muốn output dạng free-text (tự nhiên hơn cho tư vấn). Quyết định phụ thuộc vào cách frontend sẽ hiển thị kết quả.

---

## 6. Logic xử lý đặc biệt cần lưu ý

### 6.1 HITL Gate từ Planner

Planner có thể set:
- `state.requires_confirmation = True` → pipeline bị chặn
- `plan_result.missing_questions` không rỗng → cần hỏi thêm thông tin
- `plan_result.needs_human_confirmation = True` → cần xác nhận trước khi tiếp tục

**Advisor cần quyết định:**
- Nếu `missing_questions` không rỗng → Advisor vẫn chạy nhưng nêu rõ giới hạn? Hay skip hoàn toàn?
- Nếu `requires_confirmation = True` → Advisor tổng hợp lại và yêu cầu xác nhận?

### 6.2 Error Handling

Tham khảo pattern từ Researcher/Planner:
```python
except Exception as e:
    logger.exception(f"AdvisorAgent failed: {e}")
    state.add_error(f"AdvisorAgent error: {str(e)}")
    state.advisor_response = f"Advisor failed: {str(e)}"  # fallback
```

### 6.3 Streaming Support

Cả Researcher và Planner đều có `run_stream()`. Advisor nên implement tương tự để hỗ trợ WebSocket real-time UI:

```python
async def run_stream(self, state: AgentState):
    async for chunk in agent.run(user_message, stream=True):
        if chunk.text:
            yield chunk.text
```

---

## 7. Tóm tắt dữ liệu Advisor nhận được (Input context)

```
┌─────────────────────────────────────────────────────────────────┐
│                     ADVISOR INPUT CONTEXT                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│  FROM RESEARCHER (state.research_result):                       │
│  ├── universities[]                                             │
│  │   ├── university_name, major, benchmark_score                │
│  │   ├── admission_method, required_documents                   │
│  │   ├── deadline, tuition_fee, website                         │
│  │   └── source_url, notes                                     │
│  ├── general_requirements[]                                     │
│  ├── important_deadlines{}                                      │
│  ├── admission_methods[]                                        │
│  ├── raw_summary                                                │
│  └── sources[]                                                  │
│                                                                 │
│  FROM PLANNER (state.plan_result):                              │
│  ├── checklist[]                                                │
│  │   ├── title, status, required, reason, source                │
│  ├── timeline[]                                                 │
│  │   ├── date, task, priority, reason                           │
│  ├── risks[]                                                    │
│  ├── missing_questions[]                                        │
│  └── needs_human_confirmation                                   │
│                                                                 │
│  FROM USER (state.student_profile):                             │
│  ├── name, gpa, target_scores                                  │
│  ├── preferred_majors[], preferred_universities[]               │
│  ├── extra_activities[]                                         │
│  └── notes                                                     │
│                                                                 │
│  METADATA:                                                      │
│  ├── state.user_message (câu hỏi gốc)                          │
│  ├── state.session_id                                           │
│  └── state.errors[]                                             │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

---

## 8. Checklist triển khai

- [ ] **Tạo `backend/app/prompts/advisor.txt`** — System prompt cho Advisor
- [ ] **Tạo `backend/app/agents/advisor.py`** — Logic chính
  - [ ] Kế thừa `BaseAgent`
  - [ ] Implement `_load_prompt()`, `_build_user_message()`, `_parse_advisor_result()` (nếu structured)
  - [ ] Implement `_get_agent()` — lazy-init FoundryChatClient
  - [ ] Implement `run(state)` — logic chính
  - [ ] Implement `run_stream(state)` — streaming support
  - [ ] Guard: kiểm tra `plan_result` tồn tại trước khi chạy
- [ ] **(Tùy chọn) Cập nhật `backend/app/schemas/agent_state.py`** — Thêm `AdvisorResult` schema nếu cần structured output
- [ ] **Cập nhật `backend/app/workflows/chat_workflow.py`** — Tích hợp Advisor vào pipeline
- [ ] **Cập nhật `backend/app/main.py`** — Thêm advisor output vào API response
- [ ] **Viết tests** (nếu có test framework)


# Thêm 
Viewed Implement-plan-advisor.md:1-22

Đây là hai câu hỏi thiết kế rất hay. Tôi sẽ phân tích cả hai:

---

## 1. `AdvisorResult` model vs giữ `str` — Có cần thiết không?

### So sánh chi phí

| Tiêu chí | `advisor_response: str` | `AdvisorResult` (structured) |
|-----------|------------------------|------------------------------|
| **Code

Đây là hai câu hỏi thiết kế quan trọng. Tôi phân tích từng câu:

## 1. `AdvisorResult` model vs giữ `str`

**Khuyến nghị: Giữ `advisor_response: str` cho v1.**

**Lý do:**

- **Bản chất khác biệt:** Researcher/Planner cần structured output vì agent phía sau phải đọc dữ liệu lập trình (Planner đọc `universities[]`, Advisor đọc `checklist[]`). Nhưng Advisor là agent **cuối cùng hướng đến người dùng** — output của nó được **con người đọc trực tiếp**, không phải máy.

- **Chi phí không nhỏ:** Nhìn `_parse_research_result()` và `_parse_plan_result()` trong codebase — mỗi hàm ~100-150 dòng code xử lý JSON parsing, coercion, fallback. Viết thêm `_parse_advisor_result()` tương tự sẽ thêm ~150 dòng boilerplate mà **không ai consume programmatically**.

- **Rủi ro fragility:** LLM viết lời khuyên tự nhiên rất tốt, nhưng ép nó output JSON cho nội dung tư vấn sẽ tăng tỷ lệ parse fail. Lời khuyên kiểu *"Em nên chuẩn bị hồ sơ sớm vì deadline chỉ còn 2 tuần"* không phù hợp bị nhét vào `List[str]`.

- **Giải pháp thay thế nhẹ:** Dùng **markdown headings trong prompt** (`## Tóm tắt`, `## Lời khuyên`, `## Bước tiếp theo`). Frontend render markdown → vẫn có cấu trúc trực quan mà không cần parsing phức tạp.

> **Khi nào nên nâng cấp?** Chỉ khi frontend cần render từng section riêng biệt (ví dụ: tab "Rủi ro", tab "Lời khuyên"). Lúc đó mới tạo `AdvisorResult`.

---

## 2. Advisor có chạy khi `missing_questions` chưa trả lời?

**Khuyến nghị: KHÔNG chạy (skip) cho v1.**

**Lý do:**

- **Rủi ro hallucination:** Nếu Planner phát hiện thiếu GPA hoặc ngành mong muốn, Advisor buộc phải "đoán" để tư vấn → vi phạm nguyên tắc **ZERO HALLUCINATION** mà cả Researcher lẫn Planner đều tuân thủ. Lời khuyên dựa trên dữ liệu thiếu có thể **gây hại** (ví dụ: khuyên nộp hồ sơ vào ngành sai).

- **Trách nhiệm pháp lý:** Đây là hệ thống tư vấn tuyển sinh — lời khuyên sai có thể ảnh hưởng đến tương lai học sinh. Tốt hơn là **không tư vấn** hơn là **tư vấn sai**.

- **Workflow đã có cơ chế:** Planner set `requires_confirmation = True` + `application_status = "pending_info"` → Frontend hiển thị `missing_questions` để học sinh trả lời → Workflow chạy lại với dữ liệu đầy đủ → Advisor chạy bình thường.

**Guard condition đề xuất cho `chat_workflow.py`:**

```python
# ── Bước 3: Advisor ─────────────────────────────────────
if (state.plan_result 
    and not state.plan_result.missing_questions 
    and not state.errors):
    state = await self.advisor.run(state)
else:
    logger.warning("[Workflow] Bỏ qua AdvisorAgent — thiếu plan_result hoặc còn missing_questions")
```

---

## Tóm lại

| Quyết định | Khuyến nghị | Lý do chính |
|------------|-------------|-------------|
| Schema output | Giữ `str`, dùng markdown trong prompt | Advisor hướng đến người đọc, không cần parsing phức tạp |
| Chạy khi thiếu info | Skip, chờ user trả lời | Tránh hallucination, đảm bảo chất lượng tư vấn |
