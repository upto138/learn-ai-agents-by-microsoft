Dưới góc độ kiến trúc hệ thống, **Agentic Loop** (Vòng lặp tác tử) chính là "hệ điều hành" bên trong của một AI Agent. Thay vì chỉ nhận input và trả ra output một lần duy nhất như chatbot thông thường, Agentic Loop cho phép Agent tự vận hành thông qua các chu kỳ suy luận và hành động liên tục cho đến khi đạt được mục tiêu.

---

### 1. Cấu tạo của một Agentic Loop

Theo Microsoft Agent Framework, một Agent được định nghĩa là một đơn vị tự trị vận hành qua một vòng lặp lặp đi lặp lại để xử lý đầu vào, đưa ra quyết định và gọi công cụ. Quy trình này thường diễn ra theo các bước sau:

* 
**Nhận thức (Perception/Input):** Agent tiếp nhận yêu cầu từ người dùng hoặc dữ liệu từ bước trước đó.


* 
**Suy luận (Reasoning):** Agent sử dụng LLM làm "engine suy luận" để phân tích tình huống. Ở bước này, Agent tự hỏi: *"Tôi cần làm gì tiếp theo để đạt được mục tiêu?"*.


* 
**Hành động (Action):** Agent quyết định thực hiện một hành động cụ thể, chẳng hạn như gọi API, truy vấn cơ sở dữ liệu hoặc chạy code Python thông qua các công cụ (tools) được cung cấp.


* 
**Quan sát (Observation):** Agent nhận kết quả từ hành động đó (ví dụ: dữ liệu từ web hoặc kết quả từ hàm `get_destinations`).


* **Đánh giá (Evaluation):** Agent xem xét kết quả vừa nhận được đã đủ để trả lời chưa. Nếu chưa, nó sẽ quay lại bước Suy luận để bắt đầu một vòng lặp mới.



---

### 2. Kiến trúc Pipeline của Vòng lặp

Trong các hệ thống phức tạp như **Student Admission Agents**, Agentic Loop không chạy một cách hỗn loạn mà tuân theo một Pipeline nghiêm ngặt:

| Tầng (Layer) | Vai trò trong Vòng lặp |
| --- | --- |
| **Agent Middleware** | Điểm chặn đầu tiên để xử lý hoặc can thiệp vào dữ liệu đầu vào.

 |
| **Context Layer** | Cung cấp thông tin bổ sung (như hồ sơ sinh viên hoặc dữ liệu RAG) vào cửa sổ ngữ cảnh.

 |
| **Chat Client Layer** | Giao tiếp với LLM để gửi yêu cầu suy luận.

 |
| **LLM Engine** | "Bộ não" thực hiện việc tính toán và đưa ra quyết định hành động tiếp theo.

 |

---

### 3. Tại sao Agentic Loop lại quan trọng trong hệ thống MAS?

Trong dự án của bạn, mỗi Agent con đều sở hữu một Agentic Loop riêng biệt để giải quyết các bài toán chuyên biệt:

* **Orchestrator Agent (ReAct Pattern):** Sử dụng vòng lặp để duy trì kế hoạch tổng thể, điều phối nhiệm vụ giữa Researcher, Planner và Advisor.
* **Researcher Agent:** Vòng lặp sẽ tiếp tục chạy (ví dụ: tìm kiếm thêm các nguồn tin khác) nếu dữ liệu thu thập được từ một trang web như VnExpress chưa đủ để trích xuất các yêu cầu nhập học.
* 
**Application Agent:** Vòng lặp này có thêm bước **Human-in-the-Loop (HITL)**, trong đó Agent sẽ tạm dừng (pause) ở bước Hành động để chờ sự phê duyệt của con người trước khi thực hiện các thao tác quan trọng như nộp đơn.



> **Góc nhìn của Architect:** Một Agentic Loop tốt phải có "điểm dừng" (Termination condition). Nếu không được thiết kế kỹ với các ràng buộc về số lần lặp hoặc logic kiểm tra kết quả, Agent có thể rơi vào vòng lặp vô tận (infinite loop), gây tiêu tốn tài nguyên và chi phí API cực lớn.
> 
> 

Bạn có muốn tìm hiểu sâu hơn về cách thiết lập **điểm dừng (Termination)** cho vòng lặp để tránh việc Agent "chạy loạn" và đốt tiền API không?