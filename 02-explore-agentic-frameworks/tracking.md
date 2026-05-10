# Introduction
- This is the tracking file for course 02-explore-agentic-frameworks

# Done
- Reading theory about 02 course - explore agentic frameworks (README.md)
- Can answer below questions
    1. What are AI Agent Frameworks and what do they enable developers to achieve?
    2. How can teams use these to quickly prototype, iterate, and improve their agent’s capabilities?
    3. What are the differences between the frameworks and tools created by Microsoft (<a href="https://aka.ms/ai-agents-beginners/ai-agent-service" target="_blank">Azure AI Agent Service</a> and the <a href="https://learn.microsoft.com/azure/ai-services/openai/how-to/responses" target="_blank">Microsoft Agent Framework</a>)?
    4. Can I integrate my existing Azure ecosystem tools directly, or do I need standalone solutions?
    5. What is Azure AI Agents service and how is this helping me?


# Not Done
- Review the course - in myImages (5 mins)
- Should **read and understand the content of "azure-ai-foundry-agent-creation.md" first**.

### **Recommended Workflow**

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
