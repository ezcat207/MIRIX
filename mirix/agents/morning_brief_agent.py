"""
MorningBriefAgent - Phase 2 Week 3 Task 3.1
生成每日早晨工作简报，帮助用户规划一天的工作
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from mirix.agents.growth_analysis_agent import GrowthAnalysisAgent
from mirix.orm.project import Project
from mirix.orm.task import Task
from mirix.orm.pattern import Pattern
from mirix.orm.insight import Insight


class MorningBriefAgent:
    """
    早晨简报 Agent

    职责：
    1. 获取昨天的复盘数据
    2. 获取项目状态和任务
    3. 基于用户模式建议今日优先级
    4. 生成提醒事项
    5. 建议最优时间安排
    """

    def __init__(self, db_context):
        """
        初始化 MorningBriefAgent

        Args:
            db_context: 数据库上下文管理器
        """
        self.db_context = db_context
        self.growth_agent = GrowthAnalysisAgent(db_context)

    def generate_brief(
        self, date: datetime, user_id: str, organization_id: str
    ) -> Dict[str, Any]:
        """
        生成早晨简报

        Args:
            date: 简报日期（今天）
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            Dict: 完整简报数据
            {
                "date": "2025-11-21",
                "greeting": "早安！今天是...",
                "yesterday_summary": {...},  # 昨日复盘摘要
                "today_priorities": [...],   # 今日优先级建议（top 5）
                "reminders": [...],          # 提醒事项
                "optimal_schedule": {...},   # 最优时间安排
                "motivational_message": str  # 激励信息
            }
        """
        # 1. 获取昨天的复盘数据
        yesterday = date - timedelta(days=1)
        yesterday_review = None
        try:
            yesterday_review = self.growth_agent.daily_review(
                date=yesterday, user_id=user_id, organization_id=organization_id
            )
        except Exception as e:
            print(f"Warning: Could not get yesterday's review: {e}")
            yesterday_review = None

        # 2. 获取用户的活跃项目
        active_projects = self._get_active_projects(user_id, organization_id)

        # 3. 获取用户的高效时段模式
        patterns = self._get_recent_patterns(user_id, organization_id, days=7)

        # 4. 基于昨日表现和项目状态建议今日优先级
        today_priorities = self._suggest_today_priorities(
            yesterday_review, active_projects, patterns, user_id, organization_id
        )

        # 5. 生成提醒事项
        reminders = self._generate_reminders(user_id, organization_id, date)

        # 6. 建议最优时间安排
        optimal_schedule = self._suggest_optimal_schedule(patterns, today_priorities)

        # 7. 生成激励信息
        motivational_message = self._generate_motivational_message(yesterday_review)

        # 8. 生成问候语
        greeting = self._generate_greeting(date)

        return {
            "date": date.strftime("%Y-%m-%d"),
            "greeting": greeting,
            "yesterday_summary": self._extract_yesterday_summary(yesterday_review),
            "today_priorities": today_priorities,
            "reminders": reminders,
            "optimal_schedule": optimal_schedule,
            "motivational_message": motivational_message,
        }

    def _get_active_projects(
        self, user_id: str, organization_id: str
    ) -> List[Project]:
        """获取用户的活跃项目"""
        with self.db_context() as session:
            projects = (
                session.query(Project)
                .filter(
                    Project.user_id == user_id,
                    Project.organization_id == organization_id,
                    Project.status == "active",
                )
                .order_by(Project.priority.desc())
                .limit(10)
                .all()
            )
            return projects

    def _get_recent_patterns(
        self, user_id: str, organization_id: str, days: int = 7
    ) -> List[Pattern]:
        """获取最近的模式（用于识别高效时段）"""
        cutoff_date = datetime.now() - timedelta(days=days)

        with self.db_context() as session:
            patterns = (
                session.query(Pattern)
                .filter(
                    Pattern.user_id == user_id,
                    Pattern.organization_id == organization_id,
                    Pattern.created_at >= cutoff_date,
                )
                .order_by(Pattern.confidence.desc())
                .all()
            )
            return patterns

    def _suggest_today_priorities(
        self,
        yesterday_review: Optional[Dict],
        active_projects: List[Project],
        patterns: List[Pattern],
        user_id: str,
        organization_id: str,
    ) -> List[Dict]:
        """
        基于昨日表现和项目状态建议今日优先级

        优先级计算逻辑：
        1. 高优先级项目的任务
        2. 昨日未完成的重要任务
        3. 今日截止的任务
        4. 阻塞其他任务的任务

        Returns:
            List[Dict]: 优先级任务列表（top 5）
        """
        priorities = []

        # 从所有活跃项目中获取任务
        with self.db_context() as session:
            for project in active_projects[:5]:  # 只看前5个项目
                # 获取项目的待办任务
                tasks = (
                    session.query(Task)
                    .filter(
                        Task.project_id == project.id,
                        Task.status.in_(["todo", "in_progress"]),
                    )
                    .order_by(Task.priority.desc(), Task.estimated_hours.asc())
                    .limit(3)  # 每个项目取前3个任务
                    .all()
                )

                for task in tasks:
                    # 计算任务的综合优先级分数
                    score = self._calculate_task_priority_score(task, project)

                    priorities.append(
                        {
                            "task_id": task.id,
                            "task_title": task.title,
                            "project_id": project.id,
                            "project_name": project.name,
                            "priority_score": score,
                            "estimated_hours": task.estimated_hours or 0,
                            "status": task.status,
                            "due_date": task.due_date.isoformat()
                            if task.due_date
                            else None,
                            "is_blocking": task.blocking,
                            "reason": self._generate_priority_reason(
                                task, project, yesterday_review
                            ),
                        }
                    )

        # 按优先级分数排序，取前5个
        priorities.sort(key=lambda x: x["priority_score"], reverse=True)
        return priorities[:5]

    def _calculate_task_priority_score(self, task: Task, project: Project) -> float:
        """
        计算任务的综合优先级分数（0-100）

        因素：
        - 任务优先级（1-10）: 权重 30%
        - 项目优先级（1-10）: 权重 20%
        - 是否阻塞其他任务: +20 分
        - 截止日期临近程度: 最多 +30 分
        """
        score = 0.0

        # 1. 任务优先级（0-30 分）
        score += task.priority * 3

        # 2. 项目优先级（0-20 分）
        score += project.priority * 2

        # 3. 阻塞其他任务（+20 分）
        if task.blocking:
            score += 20

        # 4. 截止日期临近程度（0-30 分）
        if task.due_date:
            days_until_due = (task.due_date - datetime.now()).days
            if days_until_due < 0:
                # 已逾期
                score += 30
            elif days_until_due == 0:
                # 今天截止
                score += 25
            elif days_until_due == 1:
                # 明天截止
                score += 20
            elif days_until_due <= 3:
                # 3 天内截止
                score += 15
            elif days_until_due <= 7:
                # 1 周内截止
                score += 10

        return min(score, 100)  # 最高 100 分

    def _generate_priority_reason(
        self, task: Task, project: Project, yesterday_review: Optional[Dict]
    ) -> str:
        """生成优先级推荐理由"""
        reasons = []

        if task.blocking:
            reasons.append("阻塞其他任务")

        if task.due_date:
            days_until_due = (task.due_date - datetime.now()).days
            if days_until_due < 0:
                reasons.append(f"已逾期 {abs(days_until_due)} 天")
            elif days_until_due == 0:
                reasons.append("今天截止")
            elif days_until_due <= 3:
                reasons.append(f"{days_until_due} 天后截止")

        if task.priority >= 8:
            reasons.append("高优先级任务")

        if project.priority >= 8:
            reasons.append("高优先级项目")

        if not reasons:
            reasons.append("待办任务")

        return "；".join(reasons)

    def _generate_reminders(
        self, user_id: str, organization_id: str, date: datetime
    ) -> List[Dict]:
        """
        生成提醒事项

        提醒类型：
        1. 今日截止的任务
        2. 即将到期的项目
        3. 基于 Insight 的提醒
        """
        reminders = []

        # 1. 今日截止的任务
        today_start = date.replace(hour=0, minute=0, second=0, microsecond=0)
        today_end = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        with self.db_context() as session:
            due_tasks = (
                session.query(Task)
                .filter(
                    Task.user_id == user_id,
                    Task.organization_id == organization_id,
                    Task.due_date >= today_start,
                    Task.due_date <= today_end,
                    Task.status.in_(["todo", "in_progress"]),
                )
                .all()
            )

            for task in due_tasks:
                reminders.append(
                    {
                        "type": "task_due",
                        "title": f"任务今日截止：{task.title}",
                        "content": f"任务「{task.title}」今天截止，请及时完成。",
                        "priority": 9,
                        "task_id": task.id,
                        "timestamp": datetime.now().isoformat(),
                    }
                )

            # 2. 基于最新 Insight 的提醒
            recent_insights = (
                session.query(Insight)
                .filter(
                    Insight.user_id == user_id,
                    Insight.organization_id == organization_id,
                    Insight.status == "active",
                )
                .order_by(Insight.priority.desc())
                .limit(2)
                .all()
            )

            for insight in recent_insights:
                if insight.category == "health" and insight.priority >= 8:
                    # 健康类高优先级洞察
                    reminders.append(
                        {
                            "type": "health_reminder",
                            "title": insight.title,
                            "content": insight.content,
                            "priority": insight.priority,
                            "insight_id": insight.id,
                            "timestamp": datetime.now().isoformat(),
                        }
                    )

        return reminders

    def _suggest_optimal_schedule(
        self, patterns: List[Pattern], priorities: List[Dict]
    ) -> Dict:
        """
        基于高效时段建议最优时间安排

        Args:
            patterns: 用户的时间模式（包含高效时段）
            priorities: 今日优先级任务

        Returns:
            {
                "high_productivity_hours": [9, 10, 11],  # 高效时段
                "suggested_schedule": [
                    {
                        "time_slot": "09:00-11:00",
                        "tasks": [...],  # 建议在这个时段完成的任务
                        "reason": "你的最高效时段"
                    },
                    ...
                ]
            }
        """
        # 1. 从 Temporal Pattern 中提取高效时段
        high_productivity_hours = []
        for pattern in patterns:
            if pattern.pattern_type == "temporal" and "高效时段" in pattern.title:
                # 尝试解析时间范围，例如 "09:00-11:00"
                if "：" in pattern.title:
                    time_range = pattern.title.split("：")[-1]
                    # 简单解析（假设格式为 "HH:00-HH:00"）
                    if "-" in time_range:
                        try:
                            start_str, end_str = time_range.split("-")
                            start_hour = int(start_str.split(":")[0])
                            end_hour = int(end_str.split(":")[0])
                            high_productivity_hours = list(range(start_hour, end_hour))
                            break
                        except (ValueError, IndexError):
                            pass

        # 如果没有找到模式，使用默认高效时段（9-11am）
        if not high_productivity_hours:
            high_productivity_hours = [9, 10]

        # 2. 生成时间安排建议
        suggested_schedule = []

        if high_productivity_hours:
            # 高效时段：安排最重要的任务
            important_tasks = priorities[:2]  # 前2个最重要的任务
            if important_tasks:
                time_slot = f"{high_productivity_hours[0]:02d}:00-{high_productivity_hours[-1]+1:02d}:00"
                suggested_schedule.append(
                    {
                        "time_slot": time_slot,
                        "tasks": [
                            {
                                "title": task["task_title"],
                                "project": task["project_name"],
                                "estimated_hours": task["estimated_hours"],
                            }
                            for task in important_tasks
                        ],
                        "reason": "你的最高效时段，适合处理复杂任务",
                    }
                )

            # 下午时段：安排其他任务
            remaining_tasks = priorities[2:]
            if remaining_tasks:
                suggested_schedule.append(
                    {
                        "time_slot": "14:00-17:00",
                        "tasks": [
                            {
                                "title": task["task_title"],
                                "project": task["project_name"],
                                "estimated_hours": task["estimated_hours"],
                            }
                            for task in remaining_tasks
                        ],
                        "reason": "适合处理轻量任务和沟通工作",
                    }
                )

        return {
            "high_productivity_hours": high_productivity_hours,
            "suggested_schedule": suggested_schedule,
        }

    def _generate_motivational_message(
        self, yesterday_review: Optional[Dict]
    ) -> str:
        """生成激励信息"""
        if not yesterday_review:
            return "新的一天，新的开始！保持专注，你一定能完成今天的目标。"

        # 根据昨日表现生成不同的激励信息
        efficiency = yesterday_review.get("efficiency_metrics", {})
        rating = efficiency.get("efficiency_rating", "C")
        deep_work_hours = efficiency.get("deep_work_hours", 0)

        if rating in ["S", "A"]:
            return f"昨天表现出色（{rating} 级）！今天继续保持这个节奏！"
        elif rating == "B":
            return "昨天表现不错，今天再努力一点，争取达到 A 级！"
        elif deep_work_hours >= 4:
            return f"昨天的深度工作时间达到了 {deep_work_hours:.1f} 小时，继续保持专注！"
        else:
            return "今天是个新的开始，专注于重要的事情，你可以做得更好！"

    def _generate_greeting(self, date: datetime) -> str:
        """生成问候语"""
        hour = date.hour
        weekday = date.strftime("%A")
        date_str = date.strftime("%Y年%m月%d日")

        if hour < 12:
            greeting = "早安"
        elif hour < 18:
            greeting = "午安"
        else:
            greeting = "晚上好"

        weekday_cn = {
            "Monday": "星期一",
            "Tuesday": "星期二",
            "Wednesday": "星期三",
            "Thursday": "星期四",
            "Friday": "星期五",
            "Saturday": "星期六",
            "Sunday": "星期日",
        }

        return f"{greeting}！今天是 {date_str} {weekday_cn.get(weekday, weekday)}"

    def _extract_yesterday_summary(self, yesterday_review: Optional[Dict]) -> Dict:
        """提取昨日复盘摘要（简化版）"""
        if not yesterday_review:
            return {
                "available": False,
                "message": "昨日数据暂无",
            }

        time_allocation = yesterday_review.get("time_allocation", {})
        efficiency = yesterday_review.get("efficiency_metrics", {})

        return {
            "available": True,
            "total_work_hours": time_allocation.get("total_work_hours", 0),
            "efficiency_rating": efficiency.get("efficiency_rating", "N/A"),
            "deep_work_hours": efficiency.get("deep_work_hours", 0),
            "deep_work_percentage": efficiency.get("deep_work_percentage", 0),
            "summary_text": yesterday_review.get("summary", "").split("\n\n")[0],  # 只取第一段
        }
