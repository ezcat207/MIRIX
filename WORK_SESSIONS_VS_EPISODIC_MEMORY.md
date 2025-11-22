# Work Sessions vs Episodic Memory 对比分析

**创建时间**: 2025-11-22
**目的**: 分析两种记忆系统的优缺点，提出整合方案

---

## 📊 概述对比

| 维度 | Work Sessions | Episodic Memory |
|------|--------------|-----------------|
| **生成方式** | 基于规则的算法 | LLM 语义分析 |
| **代码位置** | `growth_analysis_agent.py` | `memory_tools.py` + Memory Agents |
| **数据来源** | Raw Memory (截图) | Raw Memory (截图) |
| **主要目的** | 量化工作时段、专注度分析 | 记录事件、经历、情景 |
| **处理速度** | ⚡ 快（毫秒级） | 🐌 慢（秒级，需调用 LLM）|
| **准确性** | 🎯 规则准确但僵化 | 🧠 语义准确但不稳定 |
| **成本** | 💰 免费（无 API 调用）| 💸 有成本（LLM API）|

---

## 🏗️ 架构对比

### Work Sessions 架构

```
Raw Memory (截图数据)
    ↓
Growth Analysis Agent
    ├─ 按时间排序
    ├─ 时间间隔判断（< 5 分钟？）
    ├─ 应用相关性判断（同组应用？）
    └─ 合并/分割决策
    ↓
Work Session 对象
    ├─ start_time / end_time
    ├─ duration（秒）
    ├─ focus_score（0-10）
    ├─ app_breakdown（各应用时间）
    ├─ activity_type（硬编码为 "other"）
    └─ raw_memory_references[]
```

**特点**:
- ✅ **确定性**: 相同输入 → 相同输出
- ✅ **可预测**: 规则透明，易于调试
- ❌ **缺乏语义理解**: 只看应用名和时间，不理解内容
- ❌ **分类僵化**: activity_type 目前写死为 "other"

### Episodic Memory 架构

```
Raw Memory (截图数据)
    ↓
Meta Memory Agent (或各 Memory Agents)
    ├─ 构建 prompt（包含截图、OCR 文本）
    ├─ 调用 LLM (Gemini-2.5-flash)
    └─ LLM 分析并决定是否创建事件
    ↓
调用 episodic_memory_insert 工具
    ↓
Episodic Event 对象
    ├─ occurred_at（事件发生时间）
    ├─ summary（简短摘要）
    ├─ details（详细描述）
    ├─ event_type（事件类型）
    ├─ tree_path（分类路径）
    ├─ actor（触发者）
    ├─ metadata_（额外元数据）
    └─ raw_memory_references[]
```

**特点**:
- ✅ **语义理解**: LLM 能理解截图内容、上下文
- ✅ **灵活分类**: 动态判断事件类型和重要性
- ✅ **自然语言**: 生成人类可读的摘要和描述
- ❌ **不确定性**: 相同输入可能产生不同输出
- ❌ **速度慢**: 需要 LLM 推理（每张截图几秒）
- ❌ **有成本**: API 调用费用

---

## ⚖️ 优缺点详细分析

### Work Sessions 优点 ✅

1. **性能优异**
   - 纯算法计算，无 API 调用
   - 处理 149 张截图仅需毫秒级
   - 适合实时/高频更新

2. **确定性和可靠性**
   - 规则明确，行为可预测
   - 易于单元测试
   - 不会出现 LLM 的幻觉问题

3. **量化指标完善**
   - 精确的时间统计（duration, start/end time）
   - 专注度评分（focus_score）
   - 应用使用分布（app_breakdown）
   - 上下文切换次数（context_switches）

4. **适合趋势分析**
   - 数据结构标准化
   - 易于聚合统计（日/周/月报表）
   - 可视化友好

### Work Sessions 缺点 ❌

1. **缺乏语义理解**
   - 只看应用名，不懂内容
   - 无法区分：
     - Chrome 看 YouTube vs Chrome 看文档
     - VSCode 写代码 vs VSCode 写日记
   - 无法关联项目（project_id 永远为 None）

2. **分类能力弱**
   - activity_type 硬编码为 "other"
   - 无法自动识别：coding / meeting / research / writing
   - 应用分组规则写死在代码中

3. **合并逻辑僵化**
   - 只基于时间 + 应用名
   - 无法识别：
     - 同一项目的多个应用（VSCode + Terminal + Chrome docs）
     - 相关任务（写代码 → 查文档 → 写测试）
   - 5 分钟阈值固定，无法动态调整

4. **当前实现问题**
   - source_app 都是 "Full Screen"（截图监控问题）
   - 合并逻辑刚修复（之前每个截图都是独立 session）
   - duration 估算不准确（单截图硬编码 180 秒）

### Episodic Memory 优点 ✅

1. **语义理解能力强**
   - LLM 能理解截图内容、OCR 文本
   - 能识别事件的本质：
     - "用户在 GitHub 上创建了 Pull Request"
     - "用户在阅读 React 官方文档"
   - 生成自然语言摘要（summary, details）

2. **灵活的分类系统**
   - 动态判断 event_type
   - 分层分类（tree_path: ["work", "coding", "debugging"]）
   - 可以创建多层语义关系

3. **上下文关联**
   - LLM 能关联多个截图之间的联系
   - 能识别长期任务/项目
   - 能理解用户意图

4. **人类可读性**
   - 自动生成的 summary/details 直接可用
   - 适合展示给用户（不需二次处理）
   - 便于搜索和回顾

### Episodic Memory 缺点 ❌

1. **性能问题**
   - 每个截图需要 LLM 推理（几秒）
   - 处理 157 张截图耗时 224 秒
   - 不适合实时更新

2. **成本高昂**
   - 每次调用 Gemini API 有成本
   - 大量截图 → 大量 API 调用
   - 长期使用成本难以接受

3. **不确定性**
   - 相同输入可能产生不同输出
   - LLM 可能出现幻觉
   - 难以保证数据一致性

4. **缺乏量化指标**
   - 没有 duration、focus_score 等量化数据
   - 不适合趋势分析和图表可视化
   - metadata_ 字段自由格式，难以标准化聚合

5. **当前架构问题**
   - 6 个 Memory Agents 并行可能产生冗余
   - 没有去重逻辑
   - 与 Work Sessions 数据孤立，无法关联

---

## 🎯 核心问题总结

### Work Sessions 的核心问题

**❌ 问题**: 只有"量"没有"质"
- 知道用户工作了多久、专注度如何
- **不知道**用户在做什么、为什么做、有什么意义

**示例**:
```json
{
  "duration": 3600,
  "focus_score": 9.5,
  "app_breakdown": {"Chrome": 3600},
  "activity_type": "other",  // ❌ 没有语义
  "project_id": null          // ❌ 无法关联项目
}
```

### Episodic Memory 的核心问题

**❌ 问题**: 只有"质"没有"量"
- 知道发生了什么事件、内容是什么
- **不知道**持续了多久、专注度如何、趋势如何

**示例**:
```json
{
  "summary": "User reviewed React documentation on hooks",
  "details": "The user was reading...",
  "event_type": "learning",
  // ❌ 没有 duration
  // ❌ 没有 focus_score
  // ❌ 难以聚合分析
}
```

---

## 💡 推荐的修复方案

### 方案 1: 混合模式（推荐）⭐⭐⭐⭐⭐

**核心思想**: Work Sessions 提供"骨架"，Episodic Memory 提供"血肉"

#### 1.1 工作流程

```
Raw Memory (截图)
    ↓
步骤 1: 快速生成 Work Sessions
    ├─ Growth Analysis Agent (基于规则)
    ├─ 生成时间段、专注度、应用分布
    └─ 存储到数据库
    ↓
步骤 2: 异步语义增强（批处理）
    ├─ 每 N 个 Work Sessions 为一批
    ├─ 调用 LLM 分析（传入 OCR 文本）
    └─ 增强 Work Session 的语义字段
    ↓
增强后的 Work Session
    ├─ duration, focus_score（量化数据）
    ├─ activity_type（LLM 分类）
    ├─ project_id（LLM 推理）
    ├─ summary（LLM 生成）
    └─ semantic_tags（LLM 提取）
```

#### 1.2 具体实现

**阶段 1: Work Session 生成（快速）**

```python
# mirix/agents/growth_analysis_agent.py

def _generate_work_sessions(raw_memories):
    """
    基于规则快速生成 Work Sessions
    - 时间合并
    - 专注度计算
    - 应用分布统计
    """
    sessions = []

    for memory in sorted(raw_memories, key=lambda m: m.captured_at):
        # ... 现有合并逻辑 ...

    # 保存到数据库（毫秒级完成）
    return sessions
```

**阶段 2: 语义增强（异步批处理）**

```python
# mirix/agents/work_session_enhancer.py (新文件)

class WorkSessionEnhancer:
    """
    异步增强 Work Sessions 的语义信息
    """

    async def enhance_sessions_batch(self, sessions: List[WorkSession]):
        """
        批量处理 Work Sessions，每批 10-20 个
        """
        for batch in chunk(sessions, size=20):
            # 构建批量 prompt
            prompt = self._build_batch_prompt(batch)

            # 调用 LLM（一次调用处理多个 sessions）
            enhancements = await llm.analyze(prompt)

            # 更新 Work Sessions
            for session, enhancement in zip(batch, enhancements):
                session.activity_type = enhancement['activity_type']
                session.project_id = enhancement['project_id']
                session.metadata_['summary'] = enhancement['summary']
                session.metadata_['tags'] = enhancement['tags']

    def _build_batch_prompt(self, sessions):
        """
        构建批量分析 prompt

        示例输出：
        [
          {
            "session_id": "worksession-1",
            "activity_type": "coding",
            "project_id": "project-mirix",
            "summary": "实现 Work Session 语义增强功能",
            "tags": ["python", "fastapi", "memory-system"]
          },
          ...
        ]
        """
        return f"""
        分析以下工作会话，为每个会话提供语义信息：

        {self._format_sessions_for_llm(sessions)}

        返回 JSON 数组，每个元素包含：
        - activity_type: coding/research/meeting/writing/design/other
        - project_id: 关联的项目 ID（如果能推断出）
        - summary: 20-50 字的工作内容摘要
        - tags: 3-5 个关键标签
        """
```

**阶段 3: Episodic Memory 作为补充**

```python
# 只为"重要"事件创建 Episodic Memory

def should_create_episodic_memory(work_session):
    """
    判断是否值得创建 Episodic Memory
    """
    # 1. 长时间专注工作（值得记录）
    if work_session.duration > 1800 and work_session.focus_score > 8:
        return True

    # 2. 重要事件（会议、演示等）
    if work_session.activity_type in ['meeting', 'presentation']:
        return True

    # 3. 新项目启动
    if 'project_start' in work_session.metadata_.get('tags', []):
        return True

    # 其他常规工作不需要 Episodic Memory
    return False
```

#### 1.3 优势

1. **性能最优**:
   - 用户无需等待 LLM（Work Sessions 秒级生成）
   - LLM 批量处理 + 异步执行（后台完成）

2. **成本可控**:
   - 批量调用减少 API 次数（20 个 sessions → 1 次调用）
   - 只为必要场景创建 Episodic Memory

3. **数据完整**:
   - 量化指标（duration, focus_score）
   - 语义信息（activity_type, summary, tags）
   - 两全其美

4. **易于扩展**:
   - 可以逐步优化 LLM prompt
   - 可以添加更多语义字段
   - 不影响现有 Work Sessions 逻辑

### 方案 2: Work Sessions 优先（简化版）⭐⭐⭐⭐

**核心思想**: 改进 Work Sessions，让它"够用"

#### 2.1 改进点

**改进 1: 改进应用名称提取**

```python
# 修复 screenshot monitor
# 从 "Full Screen" → 真实应用名 "Google Chrome", "VSCode"

def get_active_window_app():
    """
    macOS: 使用 AppKit / pyobjc
    - NSWorkspace.sharedWorkspace().activeApplication()

    返回: "Google Chrome", "Code", "Notion"
    """
```

**改进 2: 基于 OCR 的内容分类**

```python
def classify_activity_type(session):
    """
    基于 OCR 文本的简单关键词匹配
    """
    ocr_texts = [rm.ocr_text for rm in session.raw_memories]
    combined = " ".join(ocr_texts).lower()

    # 关键词匹配
    if any(kw in combined for kw in ['def ', 'class ', 'import ', 'function']):
        return 'coding'

    if any(kw in combined for kw in ['zoom', 'meeting', 'calendar']):
        return 'meeting'

    if any(kw in combined for kw in ['documentation', 'tutorial', 'guide']):
        return 'research'

    return 'other'
```

**改进 3: 基于 URL 的项目关联**

```python
def infer_project_from_urls(session):
    """
    从 URL 推断项目
    """
    urls = [rm.source_url for rm in session.raw_memories if rm.source_url]

    # GitHub 项目
    github_repos = extract_github_repos(urls)
    if 'MIRIX' in github_repos:
        return 'project-mirix'

    # 文件路径（如果有）
    file_paths = extract_file_paths(ocr_texts)
    if '/MIRIX/' in file_paths:
        return 'project-mirix'

    return None
```

#### 2.2 优势

- ✅ 简单直接，易于实现
- ✅ 无 LLM 成本
- ✅ 性能极佳

#### 2.3 劣势

- ❌ 关键词匹配不如 LLM 智能
- ❌ 无法处理复杂场景
- ❌ 需要维护关键词列表

### 方案 3: 统一为 Enhanced Work Sessions（激进）⭐⭐⭐

**核心思想**: 废弃 Episodic Memory，只用 Work Sessions

#### 3.1 扩展 Work Session Schema

```python
class WorkSession(Base):
    # ... 现有字段 ...

    # 新增语义字段
    summary: str  # LLM 生成的摘要
    details: str  # 详细描述
    semantic_tags: List[str]  # 语义标签
    event_type: str  # 事件类型（对应 Episodic 的 event_type）

    # 保留量化字段
    duration: int
    focus_score: float
    app_breakdown: dict
    context_switches: int
```

#### 3.2 优势

- ✅ 架构简化（只有一种工作记录）
- ✅ 数据一致性好
- ✅ 易于查询和分析

#### 3.3 劣势

- ❌ Work Session 和 Event 概念混淆
- ❌ 不符合原有设计理念
- ❌ 丢失了 Episodic Memory 的灵活性

---

## 🏆 最终推荐

### 推荐方案: **方案 1 - 混合模式** ⭐⭐⭐⭐⭐

**理由**:
1. **符合现有架构**: 不需要大改，增量优化
2. **性能 + 语义兼得**: Work Sessions 快速生成 + LLM 异步增强
3. **成本可控**: 批量处理 + 选择性创建 Episodic Memory
4. **用户体验最佳**: 前端立即看到数据，后台逐步完善

### 实施路线图

#### Phase 1: 修复基础问题（1-2 天）✅ 部分完成

- [x] 修复 Work Sessions 合并逻辑（已完成）
- [ ] 修复 screenshot monitor 获取真实应用名
- [ ] 改进 duration 计算逻辑

#### Phase 2: 增加简单语义（2-3 天）

- [ ] 实现基于 OCR 的 activity_type 分类
- [ ] 实现基于 URL 的 project_id 推断
- [ ] 添加简单的关键词提取（tags）

#### Phase 3: LLM 语义增强（3-5 天）

- [ ] 实现 WorkSessionEnhancer 类
- [ ] 批量 LLM 调用优化
- [ ] 异步任务队列（Celery / FastAPI BackgroundTasks）
- [ ] 前端显示增强进度

#### Phase 4: Episodic Memory 整合（2-3 天）

- [ ] 实现选择性创建逻辑
- [ ] Work Session ↔ Episodic Memory 关联
- [ ] 统一前端展示

---

## 📝 总结

### Work Sessions 的定位

**"量化的工作时段记录"**
- 快速、可靠、标准化
- 适合趋势分析、图表可视化
- 提供工作效率的客观指标

### Episodic Memory 的定位

**"有意义的事件记忆"**
- 智能、灵活、人类可读
- 适合回顾、搜索、理解上下文
- 记录重要时刻和里程碑

### 两者的关系

**不是"二选一"，而是"互补"**
- Work Sessions 是"骨架"（结构化、量化）
- Episodic Memory 是"血肉"（语义化、故事性）
- 混合使用能发挥各自优势

**最佳实践**:
```
日常工作 → Work Sessions（每 3 秒截图 → 实时合并）
重要事件 → Episodic Memory（会议、里程碑、重大决策）
语义增强 → LLM 批量处理（后台异步，增强 Work Sessions）
```

这样既能保证性能和成本，又能提供丰富的语义信息！🎯
