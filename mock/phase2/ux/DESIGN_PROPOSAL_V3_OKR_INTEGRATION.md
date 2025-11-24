# Phase 2 UX Design Proposal V3: The Integrated OKR Engine
## —— "Strategy in the Morning, Flow in the Day"

### 1. 核心理念：互补的双模态 (Complementary Dual-Mode)
您说得对，RPG 和 Cockpit 不是非此即彼，而是**时间维度**上的互补：
*   **RPG Mode (The Headquarters)**: **战略层**。用于晨间规划 (Quest Acceptance) 和晚间复盘 (Loot/XP)。关注 OKR 进度、能力成长。
*   **Cockpit Mode (The Field)**: **战术层**。用于日间执行 (Execution)。关注当前任务 (Focus)、实时状态 (Flow)。

---

### 2. Ontology 设计 (社会本体论)
为了支持您的 OKR "O2: 个人成长"，我们需要构建以下本体关系：

#### **Core Entities (核心实体)**
1.  **Objective (O)**: 宏观目标 (e.g., "个人成长 - 能力/收入/影响力增长")。
2.  **Key Result (KR)**: 关键结果 (e.g., "KR0: 主动复盘", "KR1: MIRIX MVP 发布")。
3.  **Project (P)**: 具体项目 (e.g., "MIRIX", "爸爸带女儿", "VeryLoving")。
4.  **Task (T)**: 最小执行单元 (e.g., "Fix Chat History Bug")。
5.  **Session (S)**: 时间切片 (e.g., "2025-11-23 09:00-11:00 Coding Session")。

#### **Relationships (关系)**
*   `Objective` --(has_many)--> `Key Result`
*   `Key Result` --(driven_by)--> `Project`
*   `Project` --(consists_of)--> `Task`
*   `Session` --(contributes_to)--> `Task` & `Project`

#### **Data from MIRIX SDK (数据获取)**
*   **From Screen Recording**:
    *   `AppUsage`: 验证是否在做与 Project 相关的 App (e.g., VS Code -> MIRIX)。
    *   `ContextSwitch`: 检测注意力分散。
*   **From Conversation**:
    *   `SocialInteraction`: 提取“影响力”指标（与谁聊，聊多深）。
*   **From User Input**:
    *   `Reflection`: 每日复盘的文本。

---

### 3. AI 分工 (The AI Agents)
为了实现这个系统，我们需要两个不同角色的 AI：

#### **A. The Oracle (战略家) —— 对应 RPG 界面**
*   **职责**：OKR 对齐、复盘分析、生成任务。
*   **输入**：昨天的 `Session` 数据、`Reflection` 日志。
*   **输出**：
    *   "你昨天在 MIRIX 上投入了 4 小时，KR0 进度 +2%。"
    *   "检测到你最近忽视了 'VeryLoving' 项目，建议今天分配 1 小时。"
    *   生成今日“每日任务 (Daily Quests)”。

#### **B. The Navigator (领航员) —— 对应 Cockpit 界面**
*   **职责**：实时监控、卡点解除、维持心流。
*   **输入**：实时屏幕画面、当前 `Task` 上下文。
*   **输出**：
    *   "偏航警报：你正在刷推特，而当前任务是 'Fix Bug'。"
    *   "检测到你在 StackOverflow 停留过久，是否需要搜索内部知识库？"

---

### 4. UX 交互设计 (The Dual UX)

#### **Scene 1: Morning Routine (RPG Mode)**
*   **界面**：英雄大厅。
*   **动作**：
    1.  查看 **OKR 树** (Tree of Life)：看到 O2 的进度条。
    2.  **领取任务**：AI 根据 OKR 生成 3 个主线任务 (e.g., "MIRIX: Fix Bug", "Family: Read Book")。
    3.  **装备技能**：选择今日 Focus 模式（"Deep Work" Buff）。

#### **Scene 2: Deep Work (Cockpit Mode)**
*   **界面**：战斗机座舱。
*   **动作**：
    1.  **锁定目标**：只显示当前进行的一个 Task。
    2.  **HUD 数据**：显示当前 Session 时长、效率值。
    3.  **屏蔽干扰**：其他 Project 的信息被折叠。

#### **Scene 3: Evening Review (RPG Mode)**
*   **界面**：结算画面。
*   **动作**：
    1.  **Loot Box**：结算今日 Session，转化为 XP 和 属性点（e.g., MIRIX 贡献 -> 编程能力 +5）。
    2.  **复盘填空**：AI 提问 "今天 MIRIX 进展如何？"，用户语音/文字输入。
    3.  **OKR 更新**：确认 KR 进度变化。

---

### 5. 扩展性 (Extensibility)
*   **添加新 OKR**：在 RPG 界面的 "Quest Board" 中新增 Objective 卡片。
*   **添加新 KR**：在 Objective 下挂载新的进度条。
*   **关联 Project**：将现有 Project 拖拽到新的 KR 下，建立 `driven_by` 关系。

---

### Next Steps for Prototype
我们将更新 `shared_data.js` 以包含 OKR 结构，并调整两个界面以反映这种“互补”关系。
