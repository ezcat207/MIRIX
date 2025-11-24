# Product Requirements Document (PRD): Phase 2 - The Mech Pilot Protocol
**Version:** 1.0
**Date:** 2025-11-23
**Status:** Draft
**Author:** Antigravity (AI) & Power (User)

---

## 1. Executive Summary
**Product Name:** MIRIX Phase 2: The Mech Pilot
**Vision:** Build an "External Prefrontal Cortex" that gamifies the user's life into a "Mech Pilot" experience. The system unifies strategy (OKR), execution (Flow), and review (Growth) into a continuous loop, making success inevitable through data-driven feedback.
**Core Metaphor:**
*   **Pilot (User)**: The decision maker.
*   **Mech (Project)**: The vehicle for execution.
*   **AI (OS)**: The strategic advisor (Oracle) and tactical copilot (Navigator).

---

## 2. User Objectives & Success Metrics
### 2.1 User Objectives (OKR O2)
*   **Objective**: Personal Growth (Q4).
*   **Key Result 0 (KR0)**: Active Review (Highest Priority). Establish a daily "Review & Evolve" loop.
*   **Key Result 1**: Capability Growth.
*   **Key Result 2**: Wealth Flow.
*   **Key Result 3**: Influence Expansion.

### 2.2 System Success Metrics (The "Magic Metrics")
The system must quantify and visualize these three abstract values:
1.  **Capability (能力)**: Derived from *Deep Work Duration* x *Task Difficulty*.
2.  **Wealth (收入)**: Derived from *Business Project Milestones* + *Manual Entry*.
3.  **Influence (影响力)**: Derived from *Social Interaction Quality* + *Content Output*.

---

## 3. Functional Requirements: The 3-Stage Loop

### Stage 1: The Hangar (Strategy & Selection)
**Goal**: Align daily actions with long-term OKRs.
*   **FR-1.1 Magic Metrics Dashboard**: Display current levels and trends for Capability, Wealth, and Influence.
*   **FR-1.2 OKR Tree Visualization**: Show the hierarchy: `O2 -> KR0 -> Project (Mech)`.
*   **FR-1.3 Mech Selection**:
    *   User selects a Project (Mech) to "pilot".
    *   System displays "Mission Briefing" (Tasks) for that project.
    *   **AI Feature (Oracle)**: Suggest the most critical Mech based on KR status (e.g., "KR0 is at risk, launch Review Mech").
*   **FR-1.4 Loadout Configuration**: User can edit the "Loadout" (Tools/Context) for the session (e.g., "Block Twitter", "Open VS Code").

### Stage 2: The Cockpit (Execution & Flow)
**Goal**: Maximize focus and execution velocity.
*   **FR-2.1 Single-Task Focus**: The UI must hide all non-essential information. Only the current Task is visible in the Reticle.
*   **FR-2.2 Flow Shield**:
    *   Visual indicator of "Flow State".
    *   **AI Feature (Navigator)**: Monitor screen activity. If distraction (e.g., social media) is detected, the Shield integrity drops, and a "Proximity Alert" is triggered.
*   **FR-2.3 Tactical Map**: Small visualization of where the current task fits in the larger Project.
*   **FR-2.4 Quick Capture**: One-key shortcut to capture a fleeting thought/idea without leaving the Cockpit (stored for Debrief).

### Stage 3: The Debrief (Review & Growth)
**Goal**: Close the loop and crystallize learning.
*   **FR-3.1 Session Report**:
    *   Time spent, Focus Score (Shield Integrity), Tasks completed.
*   **FR-3.2 Magic Metric Calculation**:
    *   System calculates the "XP" gained in Capability/Wealth/Influence based on the session data.
    *   *Example*: "2h Coding Session completed -> +50 Capability XP".
*   **FR-3.3 Active Review (KR0 Trigger)**:
    *   **AI Feature (Oracle)**: Ask 1-3 dynamic questions based on the session (e.g., "You spent 30m on that bug. What was the root cause?").
    *   User input is saved to `daily_reflections.json`.
    *   **KR0 Progress Update**: Completing the review automatically increments KR0 progress.

---

## 4. Data Ontology & Schema
The system relies on a strict hierarchy to link micro-actions to macro-goals.

```mermaid
graph TD
    O[Objective (O2: Growth)] --> KR[Key Result (KR0: Review)]
    KR --> P[Project / Mech (MIRIX)]
    P --> S[Session (The Flight)]
    S --> T[Task (The Enemy)]
    S --> M[Metric Update (+XP)]
```

### 4.1 Data Structures (JSON)
*   **Objective**: `{ id, title, krs: [], why: "Strategic Rationale", what: "Outcome Description" }`
*   **KeyResult**: `{ id, title, status, linked_projects: [] }`
*   **Project (Mech)**: 
    *   `{ id, name, type, why, what, attributes: { cap_weight, wealth_weight, inf_weight } }`
*   **Task**: 
    *   `{ id, title, how: "Context/Background", prompt: "AI System Prompt", xp_reward }`
*   **Session**: `{ id, project_id, start_time, end_time, focus_score, tasks_completed: [], reflection_log: "" }`

### 4.2 AI Prompt Integration
*   **Task Prompt**: Each task carries a specific `prompt` field.
*   **Cockpit UI**: When a task is focused, the AI (Navigator) loads this prompt into its context window to assist the user immediately.
*   **User Edit**: User can modify the prompt in real-time if the task context changes.

---

## 5. AI System Design
### 5.1 The Oracle (Strategic AI)
*   **Role**: High-level strategist.
*   **Model**: Gemini Pro 1.5 (Large Context).
*   **Context**: Full `goals.md`, `daily_reflections.json`, last 7 days of `session_logs`.
*   **Trigger**: Morning (Hangar) and Evening (Debrief).
*   **Output**: Mission suggestions, Insight generation, KR status updates.

### 5.2 The Navigator (Tactical AI)
*   **Role**: Real-time copilot.
*   **Model**: Gemini Flash (Low Latency).
*   **Context**: Current Screen (OCR), Current Task.
*   **Trigger**: Continuous loop (every 5s) during Cockpit Mode.
*   **Output**: Distraction alerts, "Stuck" detection (e.g., no screen change for 5m).

---

## 6. Technical Architecture (Phase 2 SDK)
*   **Frontend**: React SPA (Single Page Application) hosted in Electron.
    *   *Views*: `HangarView`, `CockpitView`, `DebriefView`.
*   **Backend**: Python FastAPI (Existing MIRIX Core).
*   **Data Store**:
    *   `sqlite` for structured data (Projects, Tasks, Sessions).
    *   `chromadb` for semantic search (Reflections, Context).
    *   `markdown` for user-editable configs (`goals.md`).

---

### 7. Finalized Decisions (User Confirmed)
1.  **Metric Weighting (Influence)**: Defined as **"Effective Followers"** (potential buyers).
    *   *Implementation*: Manual input field in Debrief (e.g., "New Followers: +5", "High Quality Leads: +2").
2.  **Wealth Input**: **Manual Entry** in Debrief stage.
    *   *Implementation*: Input field "Value Generated ($)" or "Revenue ($)".
3.  **Project & Tool Management**: **Markdown-driven**.
    *   **Projects**: System watches `projects.md` (Obsidian vault) to sync Mechs.
    *   **Loadout/Tools**: System watches a `tools.md` file (or section in `projects.md`) to populate available equipment.
    *   *Example Tool Path*: `/Users/power/Documents/onemonthoneproject/001skill_reddit_research` (Claude Skill).
