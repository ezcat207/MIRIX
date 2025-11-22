# Phase 2 - Week 3 进度报告

## 📅 当前进度

**日期**: 2025-11-21
**状态**: 进行中（0% 完成）

| 任务 | 状态 | 预计耗时 | 完成情况 |
|------|------|----------|----------|
| Task 3.1: MorningBriefAgent | ⏳ 待开始 | 4h | 0% |
| Task 3.2: ProjectDashboardAgent | ⏳ 待开始 | 5h | 0% |
| Task 3.3: ReminderAgent (简化版) | ⏳ 待开始 | 3h | 0% |

**总进度**: 0h / 12h (0%)

---

## 📋 任务概览

### Week 3 目标

实现三个核心 Agent，为用户提供智能化的工作辅助：

1. **MorningBriefAgent**: 生成每日早晨工作简报
2. **ProjectDashboardAgent**: 提供项目进度和健康度分析
3. **ReminderAgent**: 基于模式的智能提醒（简化版）

---

## 🎯 任务详情

### Task 3.1: MorningBriefAgent (4h)

**功能需求**:
1. 获取昨天的复盘数据（来自 GrowthAnalysisAgent）
2. 获取当前项目状态
3. 基于用户工作模式建议今日优先级
4. 生成提醒事项（会议、截止日期等）

**核心方法**:
```python
class MorningBriefAgent:
    def generate_brief(date, user_id, organization_id) -> Dict:
        """
        生成早晨简报

        Returns:
            {
                "date": "2025-11-21",
                "yesterday_summary": {...},  # 昨日复盘摘要
                "today_priorities": [...],   # 今日优先级建议
                "reminders": [...],          # 提醒事项
                "optimal_schedule": {...},   # 最优时间安排
                "motivational_message": str  # 激励信息
            }
        """

    def _suggest_today_priorities(yesterday_review, projects, patterns) -> List:
        """基于昨日表现和项目状态建议优先级"""

    def _generate_reminders(user_id, date) -> List:
        """生成提醒事项"""

    def _suggest_optimal_schedule(patterns, priorities) -> Dict:
        """基于高效时段建议时间安排"""
```

**验收标准**:
- ✅ 简报内容完整（包含昨日总结、今日建议、提醒）
- ✅ 优先级建议合理（基于项目状态和用户模式）
- ✅ 格式清晰易读

---

### Task 3.2: ProjectDashboardAgent (5h)

**功能需求**:
1. 计算项目进度（完成度百分比）
2. 获取项目任务列表（包含状态、优先级）
3. 识别项目瓶颈（阻塞任务、延期风险）
4. 计算开发速度（velocity）

**核心方法**:
```python
class ProjectDashboardAgent:
    def get_dashboard_data(project_id, user_id, organization_id) -> Dict:
        """
        获取项目看板数据

        Returns:
            {
                "project_info": {...},
                "progress": {...},           # 进度统计
                "tasks": [...],             # 任务列表
                "bottlenecks": [...],       # 瓶颈分析
                "velocity": {...},          # 速度指标
                "health_score": float       # 健康度评分 (0-10)
            }
        """

    def _calculate_progress(project_id) -> Dict:
        """计算项目进度"""

    def _identify_bottlenecks(project_id) -> List:
        """识别瓶颈"""

    def _calculate_velocity(project_id, time_window_days=7) -> Dict:
        """计算开发速度"""

    def _calculate_health_score(progress, bottlenecks, velocity) -> float:
        """计算项目健康度"""
```

**验收标准**:
- ✅ 看板数据完整（进度、任务、瓶颈、速度）
- ✅ 进度计算准确
- ✅ 瓶颈识别有用
- ✅ 健康度评分合理

---

### Task 3.3: ReminderAgent (3h, 简化版)

**功能需求**:
1. 检测用户分心（连续使用娱乐应用）
2. 发送专注提醒
3. （可选）休息提醒

**核心方法**:
```python
class ReminderAgent:
    def check_and_remind(user_id, organization_id) -> List[Dict]:
        """
        检查并生成提醒

        Returns:
            [
                {
                    "type": "focus_reminder",
                    "title": "专注提醒",
                    "content": "检测到你已在娱乐应用上花费 20 分钟...",
                    "priority": 7,
                    "timestamp": datetime(...)
                },
                ...
            ]
        """

    def _should_send_focus_reminder(user_id) -> bool:
        """检测是否应发送专注提醒"""

    def _detect_distraction(user_id, time_window_minutes=15) -> bool:
        """检测分心行为"""
```

**验收标准**:
- ✅ 能检测到分心行为（连续 15 分钟娱乐应用）
- ✅ 提醒内容合适
- ✅ 不过度打扰用户

---

## 📊 Week 3 整体架构

```
MorningBriefAgent
    ↓ 调用
GrowthAnalysisAgent.daily_review()  → 获取昨日数据
    ↓
ProjectDashboardAgent.get_dashboard_data()  → 获取项目状态
    ↓
基于 Pattern + Insight → 生成优先级建议
    ↓
返回完整简报 JSON

---

ProjectDashboardAgent
    ↓ 查询
Project + Task ORM  → 项目和任务数据
    ↓
WorkSession 数据  → 时间投入分析
    ↓
计算进度、瓶颈、速度  → 健康度评分
    ↓
返回看板数据 JSON

---

ReminderAgent
    ↓ 查询
最近 15 分钟 WorkSession  → 检测应用使用
    ↓
判断是否分心  → 生成提醒
    ↓
返回提醒列表
```

---

## 🔧 技术实现要点

### 1. MorningBriefAgent

**依赖**:
- GrowthAnalysisAgent (Week 2 已完成)
- Pattern, Insight ORM 模型
- Project, Task ORM 模型

**关键算法**:
- 优先级推荐：基于昨日未完成任务 + 项目截止日期 + 用户高效时段
- 时间安排：将重要任务安排在高效时段（来自 Temporal Pattern）

### 2. ProjectDashboardAgent

**依赖**:
- Project, Task ORM 模型
- WorkSession ORM 模型

**关键算法**:
- 进度计算：`完成任务数 / 总任务数 * 100`
- 瓶颈识别：阻塞其他任务的未完成任务、超时任务
- 速度计算：`最近 7 天完成任务数 / 7`
- 健康度评分：综合进度、瓶颈数量、速度趋势

### 3. ReminderAgent

**依赖**:
- WorkSession ORM 模型
- RawMemoryItem ORM 模型

**关键算法**:
- 分心检测：检查最近 15 分钟的应用使用，判断是否为娱乐应用
- 娱乐应用列表：`["YouTube", "Netflix", "Twitter", "Instagram", "TikTok", "Reddit", ...]`

---

## 📁 文件结构

```
mirix/agents/
├── growth_analysis_agent.py      ✅ Week 2 完成
├── morning_brief_agent.py         ⏳ Task 3.1
├── project_dashboard_agent.py     ⏳ Task 3.2
└── reminder_agent.py              ⏳ Task 3.3

tests/
├── conftest.py                    ✅ Week 2 完成
├── test_growth_analysis_agent.py  ✅ Week 2 完成
├── test_morning_brief_agent.py    ⏳ Task 3.1
├── test_project_dashboard_agent.py ⏳ Task 3.2
└── test_reminder_agent.py         ⏳ Task 3.3
```

---

## 🚀 下一步行动

### 立即可做：
1. **Task 3.1**: 实现 MorningBriefAgent
   - 创建 `mirix/agents/morning_brief_agent.py`
   - 实现 `generate_brief()` 方法
   - 实现 `_suggest_today_priorities()` 方法
   - 创建测试文件

2. **Task 3.2**: 实现 ProjectDashboardAgent
   - 创建 `mirix/agents/project_dashboard_agent.py`
   - 实现看板数据计算方法
   - 创建测试文件

3. **Task 3.3**: 实现 ReminderAgent (简化版)
   - 创建 `mirix/agents/reminder_agent.py`
   - 实现分心检测逻辑
   - 创建测试文件

---

## 📝 相关文档

- **Week 2 完成总结**: `PHASE2_WEEK2_PROGRESS.md`
- **整体架构设计**: `PHASE2_AGENT_ARCHITECTURE_AND_TASKS.md`
- **项目指南**: `CLAUDE.md`

---

**生成时间**: 2025-11-21
**状态**: Week 3 准备中 ⏳
