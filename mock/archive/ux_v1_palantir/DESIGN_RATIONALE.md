# Phase 2 UX Design Rationale: The Personal Palantir
## "The Operating System for Your Life"

### 1. Design Philosophy: Palantir Style
We are adopting the **Palantir Foundry** aesthetic because it is designed for **High-Stakes Decision Making**, not just "browsing".
*   **Information Density**: We prioritize showing *more* data per pixel. No wasted whitespace.
*   **Dark Mode**: Essential for long-term usage and "hacker" aesthetic. Reduces eye strain during deep work.
*   **Ontology-First**: The UI is organized around *Objects* (People, Goals, Projects) and their *Relationships*, not just lists.
*   **Graph Visualization**: To see the hidden connections (e.g., "Person A introduced me to Concept B which solved Problem C").

### 2. User Journey 1: Learning & Networking (The "Social Graph")
**Goal**: Improve structured communication & meet capable people.
**UX Solution**:
*   **The "Network Velocity" Widget**: Tracks new nodes (people) added to your graph over time.
*   **The "Interaction Quality" Heatmap**: Analyzes your conversations (via MIRIX recording).
    *   *Metrics*: Structure Score (Did you use pyramid principle?), Listening Ratio, Insight Density.
*   **The "Connection Map"**: A force-directed graph showing how people are connected to your goals.
    *   *Visual*: `[You] -> [Goal: Learn AI] -> [Person: Dr. Smith] -> [Event: Conference]`

### 3. User Journey 2: Building Palantir (The "Builder's Dashboard")
**Goal**: Continuously advance the personal Palantir system.
**UX Solution**:
*   **The "Evolution Timeline"**: A Gantt-chart style view of your system's capabilities.
    *   *Visual*: `[Phase 1: Record] ===> [Phase 2: Reflect] ---> [Phase 3: Coach]`
*   **The "Flywheel Metric"**: Measuring the cycle time between "Experience" and "Principle".
    *   *Metric*: "Time to Insight" (How fast do you learn from a mistake?).

### 4. The "Mock" Implementation
We are building a **High-Fidelity Web Prototype** (`index.html`) to demonstrate this.
*   **Tech**: Pure HTML/CSS/JS (No heavy frameworks for this mock).
*   **Data**: Hardcoded JSON in `mock_data.js` to simulate the MIRIX SDK output.
*   **Visuals**: "Blueprint" style CSS (Monospace fonts, cyan/blue accents, dark backgrounds).
