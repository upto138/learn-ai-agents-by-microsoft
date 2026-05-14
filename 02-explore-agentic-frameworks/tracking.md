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


# (14/05 - ) New plan for Building the Planner Agent base on the current progress

As the **MAS Architect**, I have outlined your sequential roadmap to integrate the **Planner Agent** into the **Student Admission Agents** pipeline. This plan prioritizes infrastructure stability first, followed by interface synchronization with your teammates, and finally local code implementation.

---

### **Phase 1: Infrastructure & Environment (The Foundation)**

1. **Finalize Azure AI Foundry Hub and Project**: Ensure your Hub and Project are created in the Azure Portal to provide the central management workspace for all agents.
2. **Model Deployment**: Deploy the `gpt-4o-mini` model within your project, as it supports the native tool-calling capabilities required for a functional agentic loop.
3. **Update `.env` Configuration**: Securely store your `AZURE_AI_PROJECT_ENDPOINT` and `AZURE_AI_MODEL_DEPLOYMENT_NAME` (without quotes or inline comments) to prevent the `UnsupportedProtocol` connection errors encountered previously.



### **Phase 2: Pipeline Interface Synchronization (Teammate Coordination)**

4. **Sync with the Researcher Agent Lead**:
* **Input Requirements**: Confirm that the Researcher will output **Structured Data** (JSON) containing university requirements, deadlines, and target scores.
* **Data Schema**: Agree on the exact keys the Researcher will provide so the Planner doesn't have to "guess" where information is located.


5. **Sync with the Advisor Agent Lead**:
* **Output Requirements**: Define the format of the "Admission Plan" or "Checklist" the Planner will generate.
* **Context Passing**: Ensure the Advisor understands how to read the Planner’s checklist to explain it to the student in natural language.


6. **Architectural Alignment**: Confirm with the **Orchestrator** lead that the Planner will be triggered sequentially after the Researcher finishes its task, following the **Information → Planning → Explanation** flow.
#### **Applying Agentic design patterns in phase 2**
Pattern: Workflow Graph / Orchestration: Instead of a loose "chat" between agents, use this phase to define the Graph-Based Routing.  

Application: Determine if the flow is Sequential (Researcher → Planner → Advisor) or if it requires Conditional Edges (e.g., if the Researcher finds no data, loop back to the user instead of going to the Planner).  

Pattern: Shared State: Define the "Single Source of Truth."  

Application: Decide what data persists in the IWorkflowContext so that every agent in the pipeline is looking at the same student profile.  

### **Phase 3: Portal-Side Persona Configuration** (Done in 14/05 - 18:00)

7. **Create the Planner Agent in the Portal**: Navigate to the **Agents** section in AI Foundry and create a new agent named `AdmissionPlannerAgent`.
8. **Define System Instructions**: Draft the persona instructions focusing on logical analysis and checklist generation:
* **Role**: Specialized Admission Strategist.
* **Input**: Student profile + Research data.
* **Output**: Structured registration plan.


9. **Playground Validation**: Test the agent in the portal playground by manually pasting sample data from the "Researcher" role to verify it generates a logical checklist.
#### **Applying Agentic design patterns in phase 3**

**Pattern: ReAct (Reasoning + Acting)**: This must be embedded in the System Instructions you write in the portal.  
- Application: For your Planner Agent, instruct it specifically to follow a "Thought -> Action -> Observation" loop. This ensures it doesn't just guess a plan but "thinks" about the requirements first.  

**Pattern**: Tool-Use: Even if you haven't coded the tools yet, you must define the Tool Metadata in the portal now.  
- Application: Define the description of the tools your agents will eventually use so the LLM knows they exist. 
### **Phase 4: SDK Integration & Local Development**

10. **Initialize FoundryChatClient**: Use the `agent-framework-foundry` SDK to connect your local Python environment to the portal-side agent you just created.


11. **Implement the Agent Wrapper**: Use `chat_client.as_agent()` to bring the `AdmissionPlannerAgent` into your backend logic.


12. **Define Agent State**: Implement the shared state object (`state.py`) that will hold the student's admission data as it passes from the Researcher to your Planner.

### **Phase 5: Iteration & Pattern Upgrades (Future Lessons)**

13. **Refine with Design Patterns**: Once you reach **Lesson 07 (Planning Design Pattern)**, update the agent's instructions to use advanced reasoning techniques for more complex university selection logic.


14. **Add Function Tools**: Once you reach **Lesson 04 (Tool Use)**, give the Planner tools to query the **PostgreSQL** database to save the generated plans for the student's future sessions.


#### **Applying Agentic design patterns in phase 5**
**Pattern**: Human-in-the-Loop (HITL): This is the most complex pattern to implement.  
- Application: Apply this specifically to the Application Agent. Use the ApprovalRequiredAIFunction pattern to ensure the agent pauses for a human "OK" before submitting any real university forms.  
**Pattern**: CodeAct / Code Interpreter: If your Planner needs to perform complex score calculations.  
- Application: Enable sandboxed code execution so the agent can write Python to calculate GPA conversions accurately rather than relying on LLM arithmetic

---

**Critical Architect’s Note**: By syncing with your teammates in **Step 4 and 5**, you prevent the most common failure in Multi-Agent Systems: **Interface Mismatch**. If the Researcher sends a raw PDF text but the Planner expects a clean JSON list, the entire pipeline will break.

**One relevant follow-up question:**
Since you are ready to coordinate with your teammates, would you like me to provide a **sample JSON schema** that the Researcher could use to pass data to your Planner Agent?
