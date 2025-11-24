# Phase 2 UX Design Proposal V4: The Mech Pilot Protocol
## —— "Enter the Machine. Execute. Evolve."

### 1. 核心隐喻 (The Core Metaphor)
我们将整个系统视为一套**外骨骼装甲 (Exoskeleton/Mech)**。
*   **The Pilot (驾驶员)**: 您 (User)。负责决策、创造、体验。
*   **The Mech (机甲)**: 项目 (Project)。您通过“驾驶”项目来实现 OKR。
*   **The AI (机载电脑)**: 辅助系统。负责导航、监控、战术分析。

### 2. 统一的用户旅程 (The Unified Journey)
不再分割为两个独立页面，而是一个连续的**三阶段循环**：

#### **Stage 1: The Hangar (机库/整备室) —— 战略与选择**
*   **场景**：每天开始或任务切换时。
*   **核心动作**：**Select Mech (选择项目)**。
*   **UI 元素**：
    *   **Magic Metrics 面板**：显示三大核心指标（能力、收入、影响力）的当前读数。
    *   **Mech Bay (机位)**：
        *   `Mech-01 [MIRIX]`: 状态 "Active", 装备 "Code Editor", "Design Doc".
        *   `Mech-02 [Dad & Daughter]`: 状态 "Standby", 装备 "Storybook", "Park".
    *   **Mission Briefing**：AI 根据 KR0 (主动复盘) 生成的今日建议。
*   **User Action**: 点击 "Launch MIRIX" -> 进入驾驶舱动画。

#### **Stage 2: The Cockpit (驾驶舱/战斗) —— 执行与心流**
*   **场景**：深度工作 (Deep Work) 中。
*   **核心动作**：**Focus & Execute (专注执行)**。
*   **UI 元素 (HUD)**：
    *   **Reticle (准星)**：当前锁定的唯一任务 (Task)。
    *   **Shield Integrity (护盾)**：代表注意力/心流状态。检测到分心（刷推特）时护盾下降。
    *   **Fuel (精力)**：倒计时或番茄钟。
    *   **Tactical Map (战术地图)**：小窗显示当前 Task 在整个 Project 中的位置。
*   **User Action**: 完成任务 -> 点击 "Mission Complete" -> 自动记录数据。

#### **Stage 3: The Debrief (结算/复盘) —— 成长与进化**
*   **场景**：任务结束或一天结束。
*   **核心动作**：**Review & Upgrade (复盘升级)**。
*   **UI 元素**：
    *   **Mission Report**：本次行动的数据（时长、专注度、产出）。
    *   **Magic Metric Update**：
        *   "Coding 2h" -> **能力增长 +0.5%**
        *   "Posted Article" -> **影响力增长 +1.2%**
    *   **KR0 Check**：AI 提问 "本次行动有何卡点？"，用户输入后，KR0 进度条上涨。
*   **User Action**: 点击 "Return to Hangar" -> 回到 Stage 1。

---

### 3. 数据与 OKR 的深度绑定
*   **Magic Metrics (能力/收入/影响力)**：不是虚构的 XP，而是由后台根据 Task 类型和完成度计算出的加权分。
*   **KR0 (主动复盘)**：不仅是目标，更是**机制**。必须完成 Stage 3 的复盘，才能真正获得指标增长。

### 4. 可编辑性 (Editable UI)
*   **User & AI Co-Editing**: 界面中的“任务列表”、“项目配置”甚至“仪表盘布局”都应支持通过 Markdown/JSON 实时修改。AI 可以根据您的习惯自动调整配置（例如：发现您晚上效率低，自动调整晚间任务难度）。

---

### Next Steps
我们将构建一个单页应用 (SPA)，通过状态机 (State Machine) 在这三个视图之间切换。
