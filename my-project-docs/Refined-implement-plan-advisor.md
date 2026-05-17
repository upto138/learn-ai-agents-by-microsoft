# Refined Implementation Plan — Advisor Agent

> **Ngày tạo:** 2026-05-17  
> **Cập nhật từ:** `Implement-plan-advisor.md` + Kinh nghiệm từ Lesson 02, 03, 04, 05, 12, 13  
> **Mục tiêu:** Kế hoạch chi tiết triển khai **Advisor Agent** — agent thứ 3 trong pipeline `Researcher → Planner → [Advisor] → Application`.

---

## 1. Quyết Định Kiến Trúc Quan Trọng Nhất

### 1.1 BẮT BUỘC dùng `Agent` + `FoundryChatClient` — KHÔNG dùng `FoundryAgent`

> [!CAUTION]
> **Đây là bài học quan trọng nhất rút ra từ Lesson 02, 03, 04, 13.**
> `FoundryAgent` gửi request kèm `agent_reference` lên server-side agent → local Python tools **KHÔNG BAO GIỜ được gọi** → LLM hallucinate kết quả.
> Chi tiết đầy đủ: xem `13-agent-memory/Problems.md`

**Pattern đúng cho Advisor Agent:**

```python
from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import AzureCliCredential

foundry_client = FoundryChatClient(
    credential=AzureCliCredential(),
    project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
    model=os.getenv("FOUNDRY_MODEL"),           # e.g. "gpt-4o-admission"
)

advisor_agent = Agent(
    name="AdvisorAgent",
    instructions=system_prompt,                  # Load từ prompts/advisor.txt
    client=foundry_client,
    tools=advisor_tools,                         # Nếu cần tools
)
```

**Tại sao pattern này hoạt động:**
1. `FoundryChatClient` gọi trực tiếp Chat Completion API — **KHÔNG** dùng `agent_reference`
2. `FunctionInvocationLayer` tự động gọi hàm Python local khi LLM trả về `tool_call`
3. Agent chạy hoàn toàn local, dùng model từ `.env` (`FOUNDRY_MODEL`)

### 1.2 Vị trí trong Pipeline

```
Researcher Agent → Planner Agent → ★ Advisor Agent ★ → Application Agent
     (tools:          (tools:           (tools:            (tools:
      WebSearch,       RAG)              LLM only +         BrowserAuto,
      RAG)                               optional RAG)      LLM)
```

---

## 2. Chiến Lược Output: Structured vs Free-text

### 2.1 Quyết định: Dùng **Hybrid** — Structured schema + free-text `narrative`

> [!IMPORTANT]
> Lesson 03 (Pattern 2: Structured Output) cho thấy Pydantic models đảm bảo output có cấu trúc, dễ parse cho downstream.
> Tuy nhiên, vai trò Advisor là **tư vấn và giải thích** — cần một phần free-text tự nhiên.

**Schema đề xuất cho `AdvisorResult`:**

```python
class RiskItem(BaseModel):
    """Một rủi ro cụ thể được phân tích."""
    description: str                              # Mô tả rủi ro
    severity: str = "medium"                      # high | medium | low
    mitigation: str = ""                          # Cách giảm thiểu

class ActionStep(BaseModel):
    """Một bước hành động cụ thể."""
    step: str                                     # Mô tả hành động
    priority: str = "medium"                      # high | medium | low
    deadline_hint: Optional[str] = None           # Gợi ý thời hạn

class AdvisorResult(BaseModel):
    """Output đầy đủ của AdvisorAgent."""
    narrative: str = ""                           # Tư vấn dạng free-text (phần chính)
    personalized_advice: List[str] = []           # Lời khuyên cá nhân hóa (bullet points)
    risk_analysis: List[RiskItem] = []            # Phân tích rủi ro có cấu trúc
    action_steps: List[ActionStep] = []           # Khuyến nghị hành động cụ thể
    confidence_level: str = "medium"              # high | medium | low
    caveats: List[str] = []                       # Giới hạn / lưu ý
    advised_at: Optional[datetime] = None         # Timestamp
```

### 2.2 Cập nhật `AgentState`

```python
# Trong agent_state.py
class AgentState(BaseModel):
    # ...
    advisor_result: Optional[AdvisorResult] = None   # Thay thế advisor_response: str
    advisor_response: str = ""                        # Giữ lại cho backward compat
```

> [!TIP]
> Sau khi parse `AdvisorResult`, gán `state.advisor_response = result.narrative` để backward-compatible với API hiện tại.

---

## 3. Chiến Lược Tools cho Advisor

### 3.1 Quyết định: Advisor chủ yếu dùng LLM Reasoning, tùy chọn RAG

Theo architecture diagram, Advisor chỉ kết nối tới `LLM Reasoning`. Tuy nhiên, dựa trên Lesson 05 (Agentic RAG), việc cho Advisor truy cập RAG tool có thể hữu ích khi cần tra cứu thêm thông tin để đưa lời khuyên chính xác hơn.

| Tùy chọn | Mô tả | Khuyến nghị |
|-----------|--------|-------------|
| **A. Không có tools** | Advisor chỉ nhận context từ state, dùng LLM reasoning thuần túy | ✅ Ưu tiên cho MVP |
| **B. Có RAG tool** | Advisor gọi `query_knowledge_base()` khi cần tra cứu thêm | 🔄 Phase 2 |

**MVP (Phase 1):** Không truyền tools → Advisor nhận toàn bộ context qua `_build_user_message()` và reasoning thuần.

```python
advisor_agent = Agent(
    name="AdvisorAgent",
    instructions=system_prompt,
    client=foundry_client,
    tools=[],                   # Không tools cho MVP
)
```

> [!NOTE]
> Lesson 12 (Context Engineering) cảnh báo về **Context Confusion** khi agent có quá nhiều tools.
> Advisor nên giữ tool loadout tối thiểu để tập trung vào reasoning.

---

## 4. Context Engineering cho Advisor

### 4.1 Bài học từ Lesson 12

Lesson 12 chỉ ra 4 loại context failure. Advisor đặc biệt dễ bị:

| Failure | Rủi ro cho Advisor | Giải pháp |
|---------|-------------------|-----------|
| **Context Distraction** | Advisor nhận quá nhiều data từ Researcher + Planner → mất focus | Summarize input trước khi đưa vào prompt |
| **Context Confusion** | Quá nhiều tools → LLM gọi sai tool | Giữ tools tối thiểu (0 cho MVP) |
| **Context Clash** | Thông tin từ Researcher mâu thuẫn với Planner | Advisor phải nhận diện và nêu rõ trong `caveats` |

### 4.2 Chiến lược xây dựng User Message

Thay vì dump toàn bộ JSON raw vào prompt, **tóm tắt có chọn lọc**:

```python
def _build_user_message(self, state: AgentState) -> str:
    sections = []

    # 1. Student Profile (luôn có)
    profile = state.student_profile
    sections.append(f"""
## HỒ SƠ HỌC SINH
- Họ tên: {profile.name}
- GPA: {profile.gpa}
- Điểm mục tiêu: {profile.target_scores}
- Ngành yêu thích: {', '.join(profile.preferred_majors)}
- Trường yêu thích: {', '.join(profile.preferred_universities)}
- Hoạt động ngoại khóa: {', '.join(profile.extra_activities)}
- Ghi chú: {profile.notes}
""")

    # 2. Research Summary (tóm tắt, không dump toàn bộ)
    if state.research_result:
        r = state.research_result
        uni_summary = "\n".join([
            f"  - {u.university_name} / {u.major} "
            f"(điểm chuẩn: {u.benchmark_score}, "
            f"phương thức: {u.admission_method})"
            for u in r.universities
        ])
        sections.append(f"""
## KẾT QUẢ NGHIÊN CỨU
Tóm tắt: {r.raw_summary}
Trường/Ngành tìm được:
{uni_summary}
Phương thức xét tuyển: {', '.join(r.admission_methods)}
Mốc quan trọng: {r.important_deadlines}
""")

    # 3. Plan Summary
    if state.plan_result:
        p = state.plan_result
        checklist_summary = "\n".join([
            f"  - [{item.status}] {item.title} "
            f"({'bắt buộc' if item.required else 'tùy chọn'})"
            for item in p.checklist
        ])
        timeline_summary = "\n".join([
            f"  - [{t.priority}] {t.date or 'TBD'}: {t.task}"
            for t in p.timeline
        ])
        sections.append(f"""
## KẾ HOẠCH TUYỂN SINH
Checklist hồ sơ:
{checklist_summary}
Timeline:
{timeline_summary}
Rủi ro: {'; '.join(p.risks) if p.risks else 'Không có'}
Câu hỏi chưa trả lời: {'; '.join(p.missing_questions) if p.missing_questions else 'Không có'}
""")

    # 4. Câu hỏi gốc của user
    sections.append(f"""
## CÂU HỎI GỐC CỦA HỌC SINH
{state.user_message}
""")

    return "\n".join(sections)
```

> [!TIP]
> Pattern này lấy cảm hứng từ Lesson 12 — **Agent Scratchpad**: chỉ đưa thông tin đã tóm tắt vào context, không dump raw data.

---

## 5. System Prompt Design

### 5.1 Áp dụng Lesson 03 — Pattern 1: Clear Agent Instructions

System prompt cho Advisor cần định nghĩa rõ: **WHO**, **WHAT**, **HOW**.

**File: `backend/app/prompts/advisor.txt`**

```
Bạn là một cố vấn tuyển sinh đại học tại Việt Nam, thân thiện và chuyên nghiệp.

## VAI TRÒ
Bạn nhận kết quả từ Researcher Agent (thông tin trường/ngành) và Planner Agent (kế hoạch hồ sơ), sau đó:
1. Giải thích kế hoạch tuyển sinh bằng ngôn ngữ dễ hiểu cho học sinh lớp 12
2. Đưa ra lời khuyên cá nhân hóa dựa trên hồ sơ cụ thể của học sinh
3. Phân tích rủi ro và đề xuất cách giảm thiểu
4. Gợi ý các bước hành động ưu tiên

## QUY TẮC
- LUÔN dựa trên dữ liệu từ Researcher và Planner. KHÔNG bịa thông tin về điểm chuẩn, deadline.
- Nếu có thông tin mâu thuẫn giữa các nguồn, hãy nêu rõ trong phần caveats.
- Nếu thiếu thông tin quan trọng (GPA, điểm thi), hãy nêu rõ giới hạn của lời khuyên.
- Giọng điệu: Động viên nhưng thực tế. Không hứa hẹn quá mức.
- Ưu tiên hành động có deadline gần nhất.

## ĐỊNH DẠNG OUTPUT
Trả về JSON với cấu trúc:
{
  "narrative": "Đoạn tư vấn tổng hợp dạng văn bản tự nhiên",
  "personalized_advice": ["Lời khuyên 1", "Lời khuyên 2"],
  "risk_analysis": [
    {"description": "...", "severity": "high|medium|low", "mitigation": "..."}
  ],
  "action_steps": [
    {"step": "...", "priority": "high|medium|low", "deadline_hint": "YYYY-MM-DD hoặc null"}
  ],
  "confidence_level": "high|medium|low",
  "caveats": ["Giới hạn 1", "Giới hạn 2"]
}
```

---

## 6. Advisor Agent — Code Blueprint

### 6.1 File: `backend/app/agents/advisor.py`

```python
"""Advisor Agent — giải thích kế hoạch và đưa lời khuyên cá nhân hóa."""

import json
import logging
import os
from datetime import datetime
from typing import Optional

from agent_framework import Agent
from agent_framework.foundry import FoundryChatClient
from azure.identity import DefaultAzureCredential

from app.agents.base import BaseAgent
from app.schemas.agent_state import AgentState, AdvisorResult, RiskItem, ActionStep

logger = logging.getLogger(__name__)


class AdvisorAgent(BaseAgent):
    name: str = "advisor"
    description: str = "Explains admission plan and gives personalized guidance"

    def __init__(self, verbose: bool = False):
        super().__init__(verbose=verbose)
        self._agent: Optional[Agent] = None
        self._system_prompt: Optional[str] = None

    def _load_prompt(self) -> str:
        if self._system_prompt is None:
            prompt_path = os.path.join(
                os.path.dirname(__file__), "..", "prompts", "advisor.txt"
            )
            with open(prompt_path, "r", encoding="utf-8") as f:
                self._system_prompt = f.read()
        return self._system_prompt

    def _get_agent(self) -> Agent:
        """Lazy-init Agent + FoundryChatClient (KHÔNG dùng FoundryAgent)."""
        if self._agent is None:
            client = FoundryChatClient(
                credential=DefaultAzureCredential(),
                project_endpoint=os.getenv("FOUNDRY_PROJECT_ENDPOINT"),
                model=os.getenv("FOUNDRY_MODEL", "gpt-4o-admission"),
            )
            self._agent = Agent(
                name="AdvisorAgent",
                instructions=self._load_prompt(),
                client=client,
                tools=[],  # MVP: No tools, pure LLM reasoning
            )
        return self._agent

    def _build_user_message(self, state: AgentState) -> str:
        """Build context message from state — summarized, not raw dump."""
        # ... (implementation theo Section 4.2)
        pass

    def _parse_advisor_result(self, raw_text: str) -> AdvisorResult:
        """Parse LLM response -> AdvisorResult."""
        try:
            data = json.loads(raw_text)
            return AdvisorResult(
                narrative=data.get("narrative", ""),
                personalized_advice=data.get("personalized_advice", []),
                risk_analysis=[RiskItem(**r) for r in data.get("risk_analysis", [])],
                action_steps=[ActionStep(**a) for a in data.get("action_steps", [])],
                confidence_level=data.get("confidence_level", "medium"),
                caveats=data.get("caveats", []),
                advised_at=datetime.now(),
            )
        except (json.JSONDecodeError, Exception) as e:
            logger.warning(f"Failed to parse structured output: {e}")
            return AdvisorResult(
                narrative=raw_text,
                confidence_level="low",
                caveats=["Output không thể parse structured — dùng raw text"],
                advised_at=datetime.now(),
            )

    async def run(self, state: AgentState) -> AgentState:
        self.log("Starting Advisor Agent...")

        # Guard: Planner phải chạy xong trước
        if state.plan_result is None:
            self.log("No plan_result found — skipping Advisor", level="warning")
            state.add_error("AdvisorAgent skipped: plan_result is None")
            return state

        try:
            agent = self._get_agent()
            user_message = self._build_user_message(state)
            response = await agent.run(user_message)
            raw_text = str(response)

            result = self._parse_advisor_result(raw_text)
            state.advisor_result = result
            state.advisor_response = result.narrative  # backward compat
            state.mark_agent_done(self.name)
            self.log("Advisor Agent completed successfully")

        except Exception as e:
            logger.exception(f"AdvisorAgent failed: {e}")
            state.add_error(f"AdvisorAgent error: {str(e)}")
            state.advisor_response = f"Advisor gặp lỗi: {str(e)}"

        return state

    async def run_stream(self, state: AgentState):
        """Streaming support for WebSocket real-time UI."""
        if state.plan_result is None:
            yield "⚠️ Không thể tư vấn: chưa có kế hoạch từ Planner."
            return
        try:
            agent = self._get_agent()
            user_message = self._build_user_message(state)
            async for chunk in agent.run(user_message, stream=True):
                if chunk.text:
                    yield chunk.text
        except Exception as e:
            logger.exception(f"AdvisorAgent streaming failed: {e}")
            yield f"\n⚠️ Lỗi: {str(e)}"
```

---

## 7. HITL Gate Logic — Khi nào Advisor chạy?

### 7.1 Quyết định

```python
# Trong chat_workflow.py
if state.plan_result is not None:
    # Case 1: Planner yêu cầu xác nhận → Advisor vẫn chạy
    # nhưng sẽ nêu rõ trong caveats rằng kế hoạch chưa được confirm
    if state.plan_result.needs_human_confirmation:
        state.advisor_result_is_preliminary = True  # Flag cho frontend

    # Case 2: Có missing_questions → Advisor vẫn chạy
    # nhưng nêu rõ giới hạn do thiếu thông tin

    state = await self.advisor.run(state)
```

> [!NOTE]
> **Quyết định thiết kế:** Advisor **luôn chạy** khi có `plan_result`, bất kể `missing_questions` hay `needs_human_confirmation`. Advisor sẽ tự điều chỉnh độ chi tiết và nêu caveats phù hợp.

---

## 8. Workflow Integration — Các file cần chỉnh sửa

### 8.1 `chat_workflow.py` — Tích hợp Advisor

```python
from app.agents.advisor import AdvisorAgent

class ChatWorkflow:
    def __init__(self, verbose: bool = False):
        self.verbose = verbose
        self.researcher = ResearcherAgent(verbose=verbose)
        self.planner = PlannerAgent(verbose=verbose)
        self.advisor = AdvisorAgent(verbose=verbose)       # ← MỚI

    async def run(self, state: AgentState) -> AgentState:
        state = await self.researcher.run(state)
        state = await self.planner.run(state)
        if state.plan_result is not None:                  # ← MỚI
            state = await self.advisor.run(state)
        return state
```

### 8.2 `agent_state.py` — Thêm schemas mới

Thêm `RiskItem`, `ActionStep`, `AdvisorResult` (xem Section 2.1).

### 8.3 `main.py` — Cập nhật API response

```python
class ChatResponse(BaseModel):
    research_result: Optional[ResearchResult] = None
    plan_result: Optional[PlanResult] = None
    advisor_result: Optional[AdvisorResult] = None     # ← MỚI
    advisor_response: str = ""                          # backward compat
    errors: List[str] = []
```

---

## 9. Bài Học Áp Dụng từ Các Lesson — Tóm Tắt

| Lesson | Bài học chính | Áp dụng cho Advisor |
|--------|--------------|---------------------|
| **02, 13** | `FoundryAgent` ≠ local tools | Dùng `Agent` + `FoundryChatClient` |
| **03** | Clear Instructions + Structured Output + Single Responsibility | System prompt WHO/WHAT/HOW, `AdvisorResult` Pydantic, chỉ tư vấn |
| **04** | `@tool` decorator, `approval_mode` | Nếu thêm RAG tool → `approval_mode="never_require"` |
| **05** | Agentic RAG, Maker-Checker | Phase 2: Advisor = "Checker" verify kế hoạch Planner |
| **12** | Context failures (Distraction, Confusion, Clash) | Summarize input, giữ tools tối thiểu, nêu mâu thuẫn trong caveats |
| **13** | Working/Short/Long-term Memory, tool execution verification | AgentState = working memory; Phase 2 tích hợp Memory Service |

---

## 10. Checklist Triển Khai Theo Phase

### Phase 1 — MVP

- [ ] Thêm `RiskItem`, `ActionStep`, `AdvisorResult` vào `agent_state.py`
- [ ] Cập nhật `AgentState` thêm field `advisor_result`
- [ ] Tạo `backend/app/prompts/advisor.txt`
- [ ] Tạo `backend/app/agents/advisor.py` (kế thừa `BaseAgent`)
  - [ ] `_load_prompt()`, `_build_user_message()`, `_get_agent()`, `_parse_advisor_result()`, `run()`
- [ ] Cập nhật `chat_workflow.py` — tích hợp Advisor
- [ ] Cập nhật `main.py` — thêm advisor output vào API response
- [ ] Test thủ công pipeline Researcher → Planner → Advisor

### Phase 2 — Nâng cao

- [ ] Thêm `run_stream()` cho streaming
- [ ] Thêm RAG tool (optional)
- [ ] Tích hợp Memory Service
- [ ] Xử lý HITL gate phức tạp
- [ ] Unit tests

---

## 11. Rủi Ro & Mitigation

| Rủi ro | Xác suất | Mitigation |
|--------|----------|------------|
| LLM không trả JSON hợp lệ | Trung bình | Fallback parser: raw text → `narrative` |
| Context quá dài → token overflow | Thấp | `_build_user_message()` đã summarize |
| Advisor hallucinate điểm chuẩn | Cao | Prompt: "CHỈ dựa trên data từ Researcher" |
| `FoundryAgent` bị dùng nhầm | Thấp | Code review + document rõ ràng |
