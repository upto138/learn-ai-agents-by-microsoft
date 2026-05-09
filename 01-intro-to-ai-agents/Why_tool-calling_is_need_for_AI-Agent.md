Để hiểu một cách bản chất và sòng phẳng nhất, **Tool-Calling** (gọi công cụ) không phải là việc AI "biết chạy code". Thực chất, đó là khả năng model **thừa nhận sự thiếu hụt của bản thân** và ra lệnh cho hệ thống bên ngoài hỗ trợ thông qua một cấu trúc dữ liệu chuẩn.

Dưới đây là cơ chế chính xác của Tool-Calling trong một hệ thống Agent:

### 1. Bản chất: Khả năng "Xuất lệnh" thay vì "Nói chuyện"

Trong chế độ bình thường, model cố gắng dự đoán từ tiếp theo để tạo ra một câu trả lời văn bản. Nhưng khi có Tool-Calling:

* Model sẽ so sánh yêu cầu của người dùng với **Mô tả của công cụ** (Tool Description) mà bạn đã định nghĩa trong `@tool`.


* Thay vì trả về văn bản như "Để tôi tìm điểm chuẩn cho bạn...", model sẽ trả về một khối dữ liệu cấu trúc (thường là JSON).


* 
**Ví dụ:** `{"function": "get_destinations", "arguments": {}}`.



### 2. Quy trình "Agentic Loop" (Vòng lặp tác tử)

Tool-calling thực thi qua 4 bước mà người dùng không nhìn thấy:

1. 
**Reasoning (Suy luận):** Model nhận đề bài và nhận ra nó không có dữ liệu thực tế (ví dụ: danh sách điểm đến năm 2026).


2. 
**Selection & Parameterization (Lựa chọn & Tham số hóa):** Model chọn công cụ phù hợp nhất và tự điền các tham số cần thiết vào lệnh JSON.


3. **Execution (Thực thi - Bởi Framework):** Bản thân model **không chạy hàm Python**. Framework (như `FoundryChatClient`) sẽ đọc lệnh JSON đó, tìm hàm Python tương ứng trên máy tính của bạn, thực thi nó và lấy kết quả.


4. 
**Observation (Quan sát & Tổng hợp):** Kết quả từ hàm Python (ví dụ: `['Paris', 'Tokyo']`) được gửi ngược lại cho model. Model đọc kết quả này như một luồng thông tin mới và cuối cùng mới đưa ra câu trả lời văn bản cho bạn.



### 3. Tại sao Agent "cần" Tool-Calling?

Nếu không có khả năng này, Agent chỉ là một "nhà thông thái bị nhốt trong phòng kín" (chỉ có kiến thức cũ được học từ lúc training). Tool-calling mang lại 3 vai trò sống còn:

* **Tương tác với thế giới thực:** Đây là cách duy nhất để **Application Agent** có thể thực hiện hành động nộp hồ sơ thực tế thông qua các công cụ như Playwright.
* 
**Truy cập dữ liệu thời gian thực:** Giúp **Researcher Agent** vượt qua giới hạn kiến thức cũ để lấy dữ liệu tuyển sinh mới nhất từ web hoặc database thông qua RAG.


* **Độ chính xác tuyệt đối:** Thay vì để AI "đoán" điểm chuẩn đại học (dễ hallucination), nó sẽ gọi hàm truy vấn trực tiếp từ SQL/PostgreSQL để lấy con số chính xác.

---

**Tổng kết:** Tool-Calling là sự chuyển đổi từ **Generative AI** (AI tạo sinh văn bản) sang **Agentic AI** (AI có khả năng hành động). Nếu model của bạn không hỗ trợ tham số này, nó sẽ mất đi khả năng "ra lệnh", và bạn buộc phải "mớm" sẵn dữ liệu cho nó (fallback mode), khiến tính linh hoạt và tự chủ của hệ thống MAS bị triệt tiêu hoàn toàn.