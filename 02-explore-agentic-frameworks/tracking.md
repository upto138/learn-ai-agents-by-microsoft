# Introduction
- This is the tracking file for course 02-explore-agentic-frameworks

# Done - 10/05/2026
- Reading theory about 02 course - explore agentic frameworks (README.md)
- Can answer below questions
    1. What are AI Agent Frameworks and what do they enable developers to achieve?
    2. How can teams use these to quickly prototype, iterate, and improve their agent’s capabilities?
    3. What are the differences between the frameworks and tools created by Microsoft (<a href="https://aka.ms/ai-agents-beginners/ai-agent-service" target="_blank">Azure AI Agent Service</a> and the <a href="https://learn.microsoft.com/azure/ai-services/openai/how-to/responses" target="_blank">Microsoft Agent Framework</a>)?
    4. Can I integrate my existing Azure ecosystem tools directly, or do I need standalone solutions?
    5. What is Azure AI Agents service and how is this helping me?


# Not Done - Done in 14/05/2026
- Review the course - in myImages (5 mins)
- Should **read and understand the content of "azure-ai-foundry-agent-creation.md" first**.

### **Recommended Workflow**
0. Link Gemini to learn and study: [Here](https://gemini.google.com/gem/27e6134c9708/e68c7134f6c04ad6)
1. **Step 1: Setup (`azure-ai-foundry-agent-creation.md`)** – Create the Agent resource in Azure AI Foundry and verify your credentials. [Link here](https://github.com/upto138/learn-ai-agents-by-microsoft/blob/nphoang/02-explore-agentic-frameworks/azure-ai-foundry-agent-creation.md)
2. **Step 2: Practical Lab (`02-python-agent-framework.ipynb`)** – Run the code to build the "Travel Booking Agent" (the lesson's example) to see the concepts in action. [Link here](https://github.com/upto138/learn-ai-agents-by-microsoft/blob/nphoang/02-explore-agentic-frameworks/code_samples/02-python-agent-framework.ipynb?short_path=c74060d)
3. **Step 3: Project Alignment** – Apply the **Client/Agent/Tool/Session** pattern to your **Researcher Agent** for the Student Admission system.

**Next Step for our conversation:** Once you've reviewed the creation guide, would you like to walk through how to adapt the **AgentSession** concept from the notebook to maintain the "memory" of a student's university preferences?

### **Rationale for this Order**

**1. Infrastructure Before Implementation (The "Foundation" Rule)** In Lesson 01, you used the `FoundryChatClient` as a simple wrapper for a model deployment. However, Lesson 02 transitions into using the **Microsoft Agent Framework (MAF)** and **Azure AI Foundry Agent Service** more deeply.

* The `.md` file likely contains the step-by-step instructions for creating the **Agent Service resource** in the Azure Portal.
* Without this setup (creating the agent, configuring its identity, and obtaining the correct project IDs), the Python code in the notebook will fail to authenticate or find the required services.

**2. Understanding the "Agentic" Architecture** The curriculum for Lesson 02 aims to help you distinguish between standard AI frameworks (just calling an LLM) and **Agent Frameworks** (intelligent entities that interact with environments).

* Reading the documentation first helps you understand the **Client → Agent → Tools → Session** hierarchy used by Microsoft.
* This conceptual knowledge is critical for your project's **Researcher** and **Planner** agents, which rely on these specific layers to function autonomously.

**3. Preventing Connection Errors** Since you previously encountered a `ChatClientException` due to environment variable formatting, the `azure-ai-foundry-agent-creation.md` file will be your guide to ensuring your `.env` variables (like `AZURE_AI_PROJECT_ENDPOINT`) are mapped correctly to the *actual* resources you just created in the portal.

---


# (14/05 - ) New plan for Building the Advisor Agent base on the current progress

Kế hoạch này được thiết kế để tích hợp **Advisor Agent** vào pipeline, tập trung vào khả năng giải thích kế hoạch (Explanation) và hướng dẫn sinh viên (Guidance).

### **Phase 1: Infrastructure & Environment (The Foundation)**

1. **Verify Hub and Project**: Đảm bảo dự án `Student-Admission-Agents` đã sẵn sàng trên Azure AI Foundry Portal.
2. **Model Deployment**: Tiếp tục sử dụng `gpt-4o-mini` để hỗ trợ khả năng suy luận ngôn ngữ tự nhiên và tương tác thân thiện.
3. **Environment Check**: Đảm bảo các biến `.env` đã được cấu hình chính xác để tránh lỗi kết nối khi Agent thực hiện truy vấn ngữ cảnh.


## Next Plan:  
- Học Agentic Design Pattern, sau đó hỏi Hòa về một số câu hỏi cần thiết dựa vào file "Questions-for-Planner-teammate.md"  
- Tiếp tục Phase 2.
- Học thêm lesson 13: Managing Agentic Memory, 12: Context Engineering for AI Agents, 5: Agentic RAG (Retrieval-Augmented Generation)  
- Thứ tự: Lesson 13: Memory, Lesson 12: Context, Lesson 05: RAG
- Kỹ năng cần đạt được: Duy trì ngữ cảnh hội thoại dài hạn với sinh viên, Biến dữ liệu JSON của Planner thành lời khuyên có cấu trúc và dễ hiểu, Khả năng tự kiểm tra lại dữ liệu nguồn để giải thích lý do (Reasoning).


### **Phase 2: Pipeline Interface Synchronization (Teammate Coordination)**

4. **Sync with the Planner Agent Lead**:
* **Input Requirements**: Advisor cần nhận được **Admission Plan/Checklist** (JSON) từ Planner.


* **Reasoning Capture**: Thống nhất với Planner để truyền tải cả "lý do" tại sao chọn trường đó, giúp Advisor giải thích thuyết phục hơn.




5. **Sync with the Application Agent Lead**:
* **Confirmation Hand-off**: Định nghĩa cách Advisor thông báo cho Application Agent khi sinh viên đã sẵn sàng nộp hồ sơ (Human-in-the-Loop).




6. **Architectural Alignment**: Xác định vị trí của Advisor là chốt chặn cuối cùng trước khi thực thi, chuyển đổi từ ngôn ngữ máy (JSON) sang ngôn ngữ người (Chat).



#### **Applying Agentic design patterns in phase 2**

* **Pattern: Shared State**: Sử dụng `IWorkflowContext` để Advisor đọc được toàn bộ lịch sử từ Researcher và Planner, đảm bảo không hỏi lại những gì sinh viên đã cung cấp.
* **Pattern: Conditional Edges**: Nếu sinh viên không đồng ý với kế hoạch của Planner, Advisor phải có logic quay lại bước Planning để điều chỉnh.

### **Phase 3: Portal-Side Persona Configuration**  (Đã xong nhưng cần xem làm gì với Agentic patterns)

7. **Create the Advisor Agent**: Tạo agent mới với tên `AdmissionAdvisorAgent` trên portal.
8. **Define System Instructions**: Thiết lập Persona là một chuyên gia tư vấn giáo dục tận tâm:
* **Role**: Educational Advisor & Mentor.
* **Task**: Giải thích checklist, trả lời thắc mắc và hướng dẫn chuẩn bị hồ sơ (IELTS, học bạ).
* **Tone**: Thân thiện, hỗ trợ và chuyên nghiệp.


9. **Playground Validation**: Giả lập dữ liệu từ Planner để kiểm tra khả năng biến một JSON phức tạp thành một lời khuyên dễ hiểu.

#### **Applying Agentic design patterns in phase 3**

* **Pattern: ReAct (Reasoning + Acting)**: Yêu cầu Advisor luôn suy nghĩ về mục tiêu của sinh viên trước khi đưa ra lời khuyên, tránh việc chỉ lặp lại checklist một cách máy móc.

### **Phase 4: SDK Integration & Local Development**

10. **Initialize FoundryChatClient**: Kết nối code Python với `AdmissionAdvisorAgent` thông qua SDK.


11. **Implement Agent Session**: Đây là bước quan trọng nhất cho Advisor. Phải tích hợp quản lý **Memory** (Lesson 13) để Agent nhớ được các câu hỏi trước đó của sinh viên trong cùng một phiên tư vấn.
12. **Wrapper Development**: Hoàn thiện hàm `agent.run()` để Advisor có thể tương tác trực tiếp với Frontend của sinh viên.



### **Phase 5: Iteration & Pattern Upgrades (Future Lessons)**

13. **Context Engineering (Lesson 12)**: Tinh chỉnh cách Advisor tiếp nhận thông tin từ Researcher để đưa ra các lời khuyên thực tế về đời sống/văn hóa tại trường đại học mục tiêu.
14. **Human-in-the-Loop (HITL)**: Tích hợp nút xác nhận (Confirmation UI) trong luồng chat của Advisor. Khi sinh viên nói "I agree", Advisor sẽ kích hoạt Application Agent thực hiện nộp hồ sơ.

---

**Critical Architect’s Note**: Advisor là Agent duy nhất tương tác trực tiếp với cảm xúc của người dùng. Nếu Advisor không hiểu đúng kế hoạch từ Planner, sinh viên sẽ mất niềm tin vào toàn bộ hệ thống MAS. Hãy ưu tiên việc thử nghiệm các kịch bản "sinh viên thắc mắc" trong Playground trước khi tích hợp vào code.

---
