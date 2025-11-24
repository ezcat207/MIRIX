# AI 在 Mech Pilot 系统中的角色 (Revised)

## 核心变更
- **模型统一**：Oracle 和 Navigator 均使用 **Gemini 2.5 Flash** (速度快，成本低)。
- **Navigator 简化**：移除屏幕监控 (OCR) 和主动干预。专注于**陪伴与坚持**。

---

## 1. The Oracle (战略大脑)
**触发时机**：Hangar (晨间/晚间)
**模型**：Gemini 2.5 Flash

**职责**：
- **每日简报**：在 Hangar 界面展示"今日已完成任务" (OKR 相关 vs 无关)。
- **战略建议**：基于当前 OKR 进度，建议下一个应该启动的 Mech。

**数据流 (Data Flow)**：
- **输入**：`projects.json` (项目结构), `daily_log` (今日完成的任务列表)。
- **输出**：Hangar 界面的 Dashboard 数据。

---

## 2. The Navigator (战术副驾)
**触发时机**：Cockpit (执行模式)
**模型**：Gemini 2.5 Flash

**职责**：
- **"定海神针" (Persistence Anchor)**：
    - 当您进入 Cockpit 时，Navigator 会加载任务专属的 `Prompt` 作为其**系统指令 (System Instruction)**。
    - **核心目标**：当您感到疲惫、分心或想放弃时，提供心理支持和方向指引，帮助您"坚持下去"。
    - 它**不会**主动写代码或读文章（除非您明确要求），它的主要作用是**防守**——防止注意力涣散。

**数据流 (Data Flow)**：
- **输入**：
    1. **System Prompt**：来自 `projects.json` 中当前任务的 `prompt` 字段。
    2. **User Input**：您在对话框中输入的文字（例如："我不想做了"、"好难"）。
- **输出**：基于 Prompt 设定的角色（如"严厉的教练"或"温柔的讲故事人"）生成的鼓励或引导话语。
- **注意**：它**不读取**屏幕内容，**不进行** OCR，**不知道**您是否打开了 Twitter（除非您告诉它）。

---

## 3. Hangar 新功能：今日战报 (Daily Log)
最外层 (Hangar) 将新增一个面板，显示：
- **OKR 相关**：今日在 Mech Pilot 中完成的任务 (从 `projects.json` 追踪)。
- **OKR 无关**：(未来功能) 允许手动记录或标记"杂事/摸鱼"时间。
