# Introduction
- This is the content I need to digest before starting this module 5 - Agentic RAG.
- All of the information here is summarized and briefly listed out in order to help me easily understand and remember the key concepts before diving into the module. Consequently, if any hard-to-understand definition here is not clear, please ask Gemini or any LLM model for more details.
--- 
Before you step into **Lesson 5 (Agentic RAG)**, you need to bridge the gap between traditional software systems (deterministic databases, exact matches) and AI systems (probabilistic reasoning, semantic matches).

Here is the essential, brief list of definitions mapped to software engineering concepts to give you the perfect mental model before starting Lesson 5:

---

### **Tier 1: The "Retrieval" Foundations (How AI Finds Data)**

#### **1. Knowledge Cutoff & Hallucination**

* **What it is:** LLMs are static artifacts. Once trained, their "knowledge database" is frozen (e.g., a model trained in 2024 knows nothing about 2026 university guidelines). If forced to answer something it doesn't know, it will predict words that *sound* correct but are entirely fabricated. This is called a **hallucination**.
* **Software Analogy:** Imagine an application that only relies on hardcoded static data bundled during its last compilation, without ever making an external API fetch.

#### **2. Embedding (Vectorization)**

* **What it is:** The process of converting natural language text (words, sentences, documents) into a long array of floating-point numbers (a vector). This vector mathematically represents the *meaning* or *semantic concept* of the text.
* **Software Analogy:** Think of it like a complex hashing function. However, instead of checking if two hashes are exactly equal (`hashA == hashB`), a vector check measures how "close" the numbers are in mathematical space to see if they mean similar things.

#### **3. Vector Database (e.g., ChromaDB / Azure AI Search)**

* **What it is:** A specialized database optimized for storing these arrays of numbers (vectors) and performing rapid "similarity searches." Instead of looking for exact keywords, it finds documents that match the *intent* or *context* of a query.
* **Software Analogy:** A database that replaces standard SQL `WHERE title LIKE '%ITP%'` with an algorithm that says: "Give me the top 5 text segments most conceptually related to the string input."

#### **4. Traditional (Static) RAG**

* **What it is:** A simple data injection design pattern. When a user asks a question, a script automatically queries a Vector DB, grabs relevant text blocks, pastes them blindly into the prompt as "context," and hands it to the LLM to write an answer.
* **Software Analogy:** Think of it as a rigid, linear ETL (Extract, Transform, Load) pipeline. It runs exactly once per user request and cannot change its query if the database returns irrelevant data.

---

### **Tier 2: The "Agentic" Foundations (How AI Controls Flow)**

#### **5. Token & Context Window**

* **What it is:** A **Token** is the fundamental unit of data an LLM reads (roughly 4 characters of English text). The **Context Window** is the maximum memory buffer (measured in tokens) an LLM can process in a single API call.
* **Software Analogy:** Think of the Context Window as the RAM allocated to a single runtime process. If you try to pass an entire 500-page university catalog into the prompt, you will cause a "Buffer Overflow" (running out of tokens) or heavily degrade performance.

#### **6. Tool / Function Calling**

* **What it is:** The mechanism where an LLM reads a user's prompt, decides it needs external data, and outputs a structured **JSON object** specifying a function name and arguments instead of natural language text.
* **Software Analogy:** The LLM does not execute code. It behaves like a routing controller that generates an exact web hook payload or API call structure, which *your* backend application (FastAPI) intercepts and executes locally.

#### **7. Iterative Control Loop (The State Machine)**

* **What it is:** The shift from a single execution script to a system that executes an event loop (`Thought → Action → Observation`). The model reviews its own output, assesses if the target criteria were met, and decides whether to loop again or terminate.
* **Software Analogy:** A standard `while` loop or an asynchronous worker poll (like a **Celery job**) that evaluates a conditional state before breaking out of the cycle.

---

### **How this ties into your Student Admission MAS**

In traditional RAG, if a student asks your system: *"What are the entry scores for New Zealand ITPs?"*, a static script would search ChromaDB for "entry scores New Zealand". If the database returns generic immigration articles instead of specific grade requirements, the system outputs a generic, useless answer.

In **Agentic RAG (Lesson 5)**, your **Researcher Agent** will use an *Iterative Control Loop*. It will call a tool to search the database. It will look at the results. If it notices the results only mention "visa information" and lack "GPA scores," the LLM will recognize the failure, rewrite its own search query to "minimum high school GPA Te Pūkenga", call the tool *again*, and only return the data once its verification criteria are satisfied.

Now that you have this mental model established, you are fully prepared to understand the architectural loops of Lesson 5. Would you like to review how the `FoundryChatClient` coordinates this JSON payload handshake when a tool is called?