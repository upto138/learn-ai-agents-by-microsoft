### 1. Những điều chắc chắn về Planner Agent - cần xác nhận 1 lần nữa với Hòa

Dựa trên tài liệu thiết kế hệ thống, đây là những thông tin "xương sống" về Planner Agent:

* **Đầu vào (Input):** Planner Agent **bắt buộc** phải lấy dữ liệu từ Researcher Agent. Cụ thể, đầu vào của nó là sự kết hợp giữa **Hồ sơ sinh viên (Student Profile)** và **Dữ liệu nghiên cứu (Research Data)** do Researcher thu thập.
* **Chức năng cốt lõi:** Planner đóng vai trò là "engine" phân tích. Nó so khớp năng lực của sinh viên với các tiêu chí tuyển sinh để tạo ra một lộ trình cụ thể.
* **Đầu ra (Output):** Planner sẽ trả về một **Kế hoạch nhập học (Admission Plan)** dưới dạng một **Checklist có cấu trúc** bao gồm các bước thực hiện và các yêu cầu chi tiết.
* **Luồng hoạt động (Workflow):** Trong pipeline, Planner nằm giữa Researcher và Advisor. Nó tiếp nhận dữ liệu thô đã được Researcher cấu trúc hóa, sau đó chuyển kết quả là bản kế hoạch cho Advisor để Advisor "dịch" lại cho sinh viên.

---

### 2. Các câu hỏi cần làm rõ với Teammate (Người thiết kế Planner)

Để Advisor Agent của bạn có thể hoạt động hoàn hảo, bạn cần "ép" Teammate cung cấp các chi tiết kỹ thuật sau:

**Về định dạng dữ liệu (Data Schema):**

1. "Dữ liệu JSON mà Planner trả về có cấu trúc như thế nào? (Bạn cần biết các Key cụ thể như `deadlines`, `required_documents`, `reason_for_recommendation` để Advisor có thể đọc và giải thích)."
2. "Planner sẽ trả về danh sách các trường đại học theo thứ tự ưu tiên hay chỉ trả về một lựa chọn tốt nhất?"

**Về logic xử lý (Reasoning logic):**  
3.  "Nếu Researcher không tìm thấy dữ liệu phù hợp với sinh viên, Planner sẽ trả về lỗi hay sẽ đưa ra một kế hoạch dự phòng (back-up plan)?"  
4.  "Planner có lưu lại 'lý do' (Reasoning) tại sao nó lại chọn bước này hay bước kia không? (Advisor rất cần thông tin này để giải thích cho sinh viên một cách thuyết phục)."  

**Về tích hợp hệ thống (Integration):**  
5.  "Planner đang sử dụng công cụ (Tool) nào để lưu trữ kế hoạch? (Ví dụ: Lưu vào `PostgreSQL` hay chỉ truyền qua `State` của workflow?)"  
6.  "Bạn có định nghĩa các 'điểm dừng' (Termination conditions) cho Planner không, hay nó sẽ luôn phải tạo ra một kế hoạch bằng mọi giá?"  

**Lời khuyên từ Architect:** Khi gặp Teammate, hãy nhấn mạnh rằng: *"Nếu tôi không biết cấu trúc JSON chính xác mà bạn trả về, Advisor của tôi sẽ không biết phải nói gì với sinh viên hoặc sẽ nói sai hoàn toàn lộ trình mà bạn đã lập ra."* Điều này sẽ giúp teammate của bạn hiểu tầm quan trọng của việc thống nhất Interface giữa hai bên.

Bạn có muốn tôi dự thảo một **mẫu cấu trúc JSON (Schema)** để bạn gửi cho Teammate làm ví dụ đối chiếu không?