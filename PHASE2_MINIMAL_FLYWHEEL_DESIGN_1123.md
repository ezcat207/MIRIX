# Phase 2 Design: The Mirror of Reflection (复盘之镜)
## —— A Personal Palantir for Entrepreneurs & Students

> "We do not learn from experience... we learn from reflecting on experience." — John Dewey

### 1. Core Philosophy: The Success Flywheel
To achieve success for an **Independent Entrepreneur** (Product/Market Fit) or a **Student** (Knowledge Mastery), mere execution is not enough. One must iterate.

The Phase 2 system implements the **"Review & Evolve"** loop:
1.  **Record (记录)**: Capture reality (Done in Phase 1 via Screen/OCR).
2.  **Reflect (反思)**: Compare reality vs. expectation. Identify "What went well" vs. "What went wrong".
3.  **Principle (原则)**: Distill lessons into algorithms for future decision-making.

---

### 2. The "Personal Palantir" Dashboard
Unlike a simple To-Do list, this dashboard is a **Strategic Command Center**. It connects the *Micro* (what you did 5 minutes ago) with the *Macro* (your 3-year vision).

#### A. The Input: Strategic Definition (`goals.md`)
The user manually defines the "North Star" in a local file. The AI monitors this file for changes.

```markdown
# My Strategic Goals (Q4 2024)
## Objective: Launch MVP & Get 100 Users
- Why: To validate market demand for [Idea X].
- Key Results:
  1. Complete core coding by Nov 30.
  2. Launch on Product Hunt by Dec 15.
- Principles:
  - "Ship fast, fix later."
  - "Talk to users every day."
```

#### B. The Reasoning Engine: "Why & What"
The AI acts as a **Strategic Consultant**, not just a secretary. It runs a nightly/weekly analysis:
*   **Strategic Alignment**: "You spent 6 hours debugging CSS today, but your goal is 'Validate Market Demand'. Is this the highest leverage activity?"
*   **Drift Detection**: "You haven't worked on 'Key Result 2' for 5 days. Are we pivoting?"
*   **Resource Reality Check**: "Based on your current velocity (recorded via screen), the Dec 15 deadline is at risk."

#### C. The Dashboard UI (The Kanban of Truth)
A visual interface showing the health of your goals, not just their status.
*   **The Strategy Map**: Visual nodes connecting Goals -> Projects -> Recent Time Spent.
*   **The "Red/Green" Insight**:
    *   🟢 **Green**: "Deep Work" session detected on Core Feature.
    *   🔴 **Red**: 3 hours spent on "Distraction" (social media/irrelevant research) during "Focus Time".

---

### 3. The Core Feature: The Reflection Loop (复盘)

#### Step 1: Automated Reconstruction (The "What Happened")
*   **Context**: "Yesterday, you worked from 10:00 to 19:00."
*   **Evidence**: "You spent 4 hours in VS Code (Project A) and 2 hours in Chrome (Researching Competitor B)."
*   *Value*: Removes the bias of memory. Shows raw truth.

#### Step 2: Guided Reflection (The "Why It Happened")
The system prompts the user (or auto-generates a draft) to answer:
*   **Gap Analysis**: "You planned to finish the API, but only finished the Database. Why?"
*   **Conflict Check**: "You violated your principle 'Ship fast' by spending 3 hours optimizing a button animation."

#### Step 3: Principle Construction (The "Codex")
This is the ultimate output. The system helps you build a **Personal Codex**.
*   **New Principle Proposal**: "Based on this week's failure, should we add a rule: 'No UI polish before logic is 100% done'?"
*   **Principle Reinforcement**: When you start a similar task next time, the system pops up: *"Remember: No UI polish yet. Focus on logic."*

---

### 4. User Journeys

#### Scenario A: The Independent Entrepreneur
*   **Goal**: Launch a SaaS.
*   **Pain Point**: Getting lost in details, losing motivation, fake productivity.
*   **Phase 2 Solution**:
    *   **Dashboard**: Shows that 80% of time is going into "Low Impact" tasks.
    *   **Reasoning**: "You are avoiding the hard sales emails. Why?"
    *   **Reflection**: "I realized I'm afraid of rejection. Principle: Do the scariest thing first."

#### Scenario B: The Student
*   **Goal**: Pass the Bar Exam / Learn Python.
*   **Pain Point**: Inefficient study methods, forgetting curve, distraction.
*   **Phase 2 Solution**:
    *   **Dashboard**: Shows "Study Density" (Time spent reading vs. Time spent practicing).
    *   **Reasoning**: "You are reading tutorials but not writing code. This is passive learning."
    *   **Reflection**: "I learned better when I built a project. Principle: Project-Based Learning only."

---

### 5. Technical Implementation (Phase 2 Scope)

*   **Data Source**: Purely **Screen Recording & OCR** (Passive). No API integrations yet.
*   **Logic**:
    *   **Goal Parser**: Reads `goals.md`.
    *   **Activity Classifier**: Maps "VS Code + File X" -> "Project A".
    *   **Reasoning Agent**: LLM (Claude/GPT-4) comparing *Activity* vs. *Goal*.
*   **Storage**:
    *   `goals.md` (User Input)
    *   `daily_reflections.json` (System Output)
    *   `principles_codex.md` (The evolving rulebook)

### 6. Roadmap to Success
1.  **Phase 1 (Done)**: The "Camera" (Recording Reality).
2.  **Phase 2 (This Design)**: The "Mirror" (Reflecting Reality & Aligning with Strategy).
3.  **Phase 3 (Future)**: The "Coach" (Proactive Intervention & Active Data Integrations).
