Since you are moving directly into the **Planner Agent** role, you need a high-quality "Mock Student Profile" to test the agent's logic. In our **Student Admission MAS**, the Planner Agent serves as the analytical core that bridges the gap between raw data (Research) and student guidance (Advisor).

Here is the sample CV and the corresponding prompt designed for your `AdmissionPlannerAgent` using `gpt-4o-mini`.

---

### **1. High School Student Sample Profile (Markdown Format)**

This structure is designed to be easily "parsed" by the LLM. In a production environment, this would be stored in your **PostgreSQL** database and passed to the agent as a JSON object.

```markdown
### STUDENT PROFILE: NGUYEN MINH ANH
**Personal Summary:** 12th-grade student at a specialized high school with a strong interest in Information Technology and a goal to study in New Zealand.

**Academic Standing:**
* **Overall GPA (Academic Transcript):** 8.2 / 10.0
* **Math/Physics Average:** 8.5
* **English Proficiency:** IELTS 6.5 (No band under 6.0)

**Extracurricular & Achievements:**
* **Leader:** School Robotics Club (2 years).
* **Volunteer:** Organized "Tech for Kids" summer camp.
* **Soft Skills:** Critical thinking, teamwork, basic Python programming.

**Target Institutions:** * Interested in New Zealand Institutes of Technology/Polytechnics (ITPs).
* **Desired Major:** Bachelor of Information Technology.
* **Financial Budget:** Moderate (Looking for path-to-residency or affordable options).

```

---

### **2. Planner Agent Prompt (System Instructions)**

Copy and paste this into the **Instructions** box of your `AdmissionPlannerAgent` in the **Azure AI Foundry Portal**. This prompt instructs the agent to act as the "Strategy Engine" of your pipeline.

> **Role:** You are the **Admission Planner Agent** for the Student Admission Multi-Agent System. Your goal is to analyze a Student's Profile against specific Institutional Requirements provided via research.
> **Task:**
> 1. **Compare Academic Fit**: Look at the student's GPA and IELTS against the requirements mentioned in the provided news/data.
> 2. **Check Eligibility**: Specifically for New Zealand ITPs, verify if the student's GPA (e.g., above 7.0) qualifies them for direct entry based on the transcript.
> 3. **Generate Actionable Plan**: Create a step-by-step checklist including:
> * Recommended Institutions (from the provided list).
> * Document preparation (Transcript, IELTS certificate, Statement of Purpose).
> * Application deadlines (estimated based on context).
> 
> 
> 
> 
> **Constraint**: Output must be a **Structured Checklist**. Do not give general advice; give a specific plan based *only* on the provided student profile and the institution data.

---

### **3. How to Run the "Test" in the Playground**

To simulate the **Researcher Agent** providing you with data, use the following message in the **Playground chat box**:

**User Message:**

> "I have researched this news: [https://vnexpress.net/8-hoc-vien-new-zealand-tuyen-thang-hoc-sinh-viet-voi-hoc-ba-tu-7-diem-5059135.html](https://vnexpress.net/8-hoc-vien-new-zealand-tuyen-thang-hoc-sinh-viet-voi-hoc-ba-tu-7-diem-5059135.html)
> Based on the article (which says 8 NZ institutes like Te Pūkenga admit students with a GPA from 7.0), please create a plan for this student:
> [PASTE THE STUDENT PROFILE FROM SECTION 1 HERE]"


**Actual result:**

Based on Nguyen Minh Anh's profile and the eligibility criteria from the provided news article regarding New Zealand institutes, here is a structured checklist to guide the admission process:

**Actionable Plan for Nguyen Minh Anh**

**Recommended Institutions:**
1. **Te Pūkenga (New Zealand Institute of Skills and Technology)**
   - Strong fit for IT programs.
2. **Auckland University of Technology (AUT)**
3. **Massey University**
4. **Waikato Institute of Technology (Wintec)**
5. **Nelson Marlborough Institute of Technology (NMIT)**
6. **Tai Poutini Polytechnic**
7. **Southern Institute of Technology (SIT)**
8. **Otago Polytechnic**

**Document Preparation:**
1. **Academic Transcript**
   - Ensure that it clearly shows a GPA of 8.2/10.0.
2. **IELTS Certificate**
   - Include the score of 6.5, verifying that no band is under 6.0.
3. **Statement of Purpose**
   - Draft a concise essay highlighting:
     - Interest in Information Technology.
     - Leadership in the Robotics Club.
     - Volunteer experience with "Tech for Kids".
     - Future career aspirations related to IT and how studying in New Zealand aligns with those goals.

**Application Process:**
1. **Research Institutions** (1 week)
   - Visit the websites of mentioned institutions to understand specific entry requirements for the Bachelor of Information Technology program.

2. **Prepare Documents** (2-3 weeks)
   - Gather the academic transcript, IELTS certificate, and write the Statement of Purpose.

3. **Check Application Deadlines** (Ongoing)
   - For most New Zealand ITPs, the typical application deadlines for semesters in February are around **November**; for the July semester, expect deadlines around **April**. Specific institutions may vary, so confirm each.

4. **Online Application Submission** (Begin in early October)
   - Fill out applications for selected institutions and submit documents before deadlines.

5. **Financial Planning** (1 month)
   - Research scholarships specific to international students in New Zealand.
   - Explore part-time work opportunities while studying and check the requirements for work permits.

6. **Prepare for Visa Application** (Post-acceptance)
   - Once offers are received, prepare necessary documents for the student visa application (confirmation of enrollment, financial capacity, health insurance, etc.).

By following this structured checklist, Nguyen Minh Anh will be well-prepared for a successful application to study Information Technology in New Zealand.

---

### **Architect's Warning on the News Link**

The link you provided contains critical data: **8 New Zealand Institutes (Te Pūkenga)** now admit Vietnamese students directly with a GPA from **7.0** and **IELTS 6.0**.

Since your student (Minh Anh) has a **GPA of 8.2** and **IELTS 6.5**, your Planner Agent should logically conclude that they are an **Excellent Fit** for all 8 institutions. If the agent fails to mention this "Direct Entry" (Tuyển thẳng) advantage, you need to refine your **Instructions** to place higher "weight" on GPA comparison logic.

**One relevant follow-up question:**
Now that you have the profile and prompt, are you ready to learn how to use **Agentic RAG** (from Lesson 05) to store this news article in **ChromaDB** so the Researcher doesn't have to send the link every time?