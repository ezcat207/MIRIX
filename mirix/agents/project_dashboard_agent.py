"""
ProjectDashboardAgent - Phase 2 Week 3 Task 3.2
提供项目进度、健康度和瓶颈分析
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from mirix.orm.project import Project
from mirix.orm.task import Task
from mirix.orm.work_session import WorkSession


class ProjectDashboardAgent:
    """
    项目看板 Agent

    职责：
    1. 计算项目进度（完成度百分比）
    2. 获取项目任务列表
    3. 识别项目瓶颈
    4. 计算开发速度（velocity）
    5. 计算项目健康度评分
    """

    def __init__(self, db_context):
        """
        初始化 ProjectDashboardAgent

        Args:
            db_context: 数据库上下文管理器
        """
        self.db_context = db_context

    def get_dashboard_data(
        self, project_id: str, user_id: str, organization_id: str
    ) -> Dict[str, Any]:
        """
        获取项目看板数据

        Args:
            project_id: 项目 ID
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            Dict: 完整看板数据
            {
                "project_info": {...},       # 项目基本信息
                "progress": {...},           # 进度统计
                "tasks": [...],              # 任务列表
                "bottlenecks": [...],        # 瓶颈分析
                "velocity": {...},           # 速度指标
                "time_investment": {...},    # 时间投入分析
                "health_score": float        # 健康度评分 (0-10)
            }
        """
        # 1. 获取项目信息
        project_info = self._get_project_info(project_id)

        # 2. 计算项目进度
        progress = self._calculate_progress(project_id)

        # 3. 获取任务列表（分组）
        tasks = self._get_tasks_grouped(project_id)

        # 4. 识别瓶颈
        bottlenecks = self._identify_bottlenecks(project_id)

        # 5. 计算开发速度
        velocity = self._calculate_velocity(project_id, time_window_days=7)

        # 6. 分析时间投入
        time_investment = self._analyze_time_investment(project_id, days=7)

        # 7. 计算项目健康度
        health_score = self._calculate_health_score(
            progress, bottlenecks, velocity, project_info
        )

        return {
            "project_info": project_info,
            "progress": progress,
            "tasks": tasks,
            "bottlenecks": bottlenecks,
            "velocity": velocity,
            "time_investment": time_investment,
            "health_score": health_score,
        }

    def _get_project_info(self, project_id: str) -> Dict:
        """获取项目基本信息"""
        with self.db_context() as session:
            project = session.query(Project).filter_by(id=project_id).first()

            if not project:
                return {
                    "exists": False,
                    "error": "Project not found",
                }

            return {
                "exists": True,
                "id": project.id,
                "name": project.name,
                "description": project.description,
                "status": project.status,
                "priority": project.priority,
                "progress": project.progress or 0,
                "total_time_spent": project.total_time_spent or 0,
                "start_date": project.start_date.isoformat()
                if project.start_date
                else None,
                "target_end_date": project.target_end_date.isoformat()
                if project.target_end_date
                else None,
                "created_at": project.created_at.isoformat(),
            }

    def _calculate_progress(self, project_id: str) -> Dict:
        """
        计算项目进度

        Returns:
            {
                "total_tasks": int,
                "completed_tasks": int,
                "in_progress_tasks": int,
                "todo_tasks": int,
                "completion_percentage": float,
                "estimated_total_hours": float,
                "actual_total_hours": float,
            }
        """
        with self.db_context() as session:
            all_tasks = (
                session.query(Task).filter_by(project_id=project_id).all()
            )

            total_tasks = len(all_tasks)
            completed_tasks = len([t for t in all_tasks if t.status == "completed"])
            in_progress_tasks = len([t for t in all_tasks if t.status == "in_progress"])
            todo_tasks = len([t for t in all_tasks if t.status == "todo"])

            # 计算完成百分比
            completion_percentage = (
                (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0
            )

            # 计算估计和实际总小时数
            estimated_total_hours = sum(
                [t.estimated_hours or 0 for t in all_tasks]
            )
            actual_total_hours = sum([t.actual_hours or 0 for t in all_tasks])

            return {
                "total_tasks": total_tasks,
                "completed_tasks": completed_tasks,
                "in_progress_tasks": in_progress_tasks,
                "todo_tasks": todo_tasks,
                "completion_percentage": round(completion_percentage, 1),
                "estimated_total_hours": estimated_total_hours,
                "actual_total_hours": actual_total_hours,
                "hours_variance": actual_total_hours - estimated_total_hours,
            }

    def _get_tasks_grouped(self, project_id: str) -> Dict:
        """
        获取任务列表（按状态分组）

        Returns:
            {
                "todo": [...],
                "in_progress": [...],
                "completed": [...]
            }
        """
        with self.db_context() as session:
            all_tasks = (
                session.query(Task)
                .filter_by(project_id=project_id)
                .order_by(Task.priority.desc(), Task.created_at.desc())
                .all()
            )

            tasks_grouped = {"todo": [], "in_progress": [], "completed": []}

            for task in all_tasks:
                task_data = {
                    "id": task.id,
                    "title": task.title,
                    "description": task.description,
                    "status": task.status,
                    "priority": task.priority,
                    "estimated_hours": task.estimated_hours or 0,
                    "actual_hours": task.actual_hours or 0,
                    "due_date": task.due_date.isoformat() if task.due_date else None,
                    "blocking": task.blocking,
                    "dependencies": task.dependencies or [],
                    "created_at": task.created_at.isoformat(),
                }

                if task.status in tasks_grouped:
                    tasks_grouped[task.status].append(task_data)

            return tasks_grouped

    def _identify_bottlenecks(self, project_id: str) -> List[Dict]:
        """
        识别项目瓶颈

        瓶颈定义：
        1. 阻塞其他任务的未完成任务
        2. 超时的任务（actual_hours > estimated_hours * 1.5）
        3. 已逾期的任务
        4. 长期处于 in_progress 状态的任务（> 7 天）

        Returns:
            List[Dict]: 瓶颈列表
        """
        bottlenecks = []

        with self.db_context() as session:
            all_tasks = (
                session.query(Task)
                .filter_by(project_id=project_id)
                .filter(Task.status.in_(["todo", "in_progress"]))
                .all()
            )

            for task in all_tasks:
                bottleneck_reasons = []

                # 1. 阻塞其他任务
                if task.blocking:
                    bottleneck_reasons.append("阻塞其他任务")

                # 2. 超时任务
                if task.estimated_hours and task.actual_hours:
                    if task.actual_hours > task.estimated_hours * 1.5:
                        bottleneck_reasons.append(
                            f"超时 {((task.actual_hours / task.estimated_hours - 1) * 100):.0f}%"
                        )

                # 3. 已逾期任务
                if task.due_date and task.due_date < datetime.now():
                    days_overdue = (datetime.now() - task.due_date).days
                    bottleneck_reasons.append(f"逾期 {days_overdue} 天")

                # 4. 长期 in_progress 任务
                if task.status == "in_progress":
                    days_in_progress = (datetime.now() - task.updated_at).days
                    if days_in_progress > 7:
                        bottleneck_reasons.append(
                            f"进行中 {days_in_progress} 天未更新"
                        )

                # 如果有瓶颈原因，添加到列表
                if bottleneck_reasons:
                    bottlenecks.append(
                        {
                            "task_id": task.id,
                            "task_title": task.title,
                            "reasons": bottleneck_reasons,
                            "priority": task.priority,
                            "status": task.status,
                            "estimated_hours": task.estimated_hours or 0,
                            "actual_hours": task.actual_hours or 0,
                        }
                    )

        # 按优先级排序
        bottlenecks.sort(
            key=lambda x: (len(x["reasons"]), x["priority"]), reverse=True
        )

        return bottlenecks

    def _calculate_velocity(self, project_id: str, time_window_days: int = 7) -> Dict:
        """
        计算开发速度（velocity）

        指标：
        1. 最近 N 天完成的任务数
        2. 平均每天完成任务数
        3. 趋势（与上一周期对比）

        Args:
            project_id: 项目 ID
            time_window_days: 时间窗口（天）

        Returns:
            {
                "tasks_completed_this_week": int,
                "avg_tasks_per_day": float,
                "hours_spent_this_week": float,
                "trend": "increasing" | "stable" | "decreasing"
            }
        """
        now = datetime.now()
        current_period_start = now - timedelta(days=time_window_days)
        previous_period_start = current_period_start - timedelta(days=time_window_days)

        with self.db_context() as session:
            # 当前周期完成的任务
            current_completed = (
                session.query(Task)
                .filter(
                    Task.project_id == project_id,
                    Task.status == "completed",
                    Task.updated_at >= current_period_start,
                )
                .all()
            )

            # 上一周期完成的任务
            previous_completed = (
                session.query(Task)
                .filter(
                    Task.project_id == project_id,
                    Task.status == "completed",
                    Task.updated_at >= previous_period_start,
                    Task.updated_at < current_period_start,
                )
                .all()
            )

            current_count = len(current_completed)
            previous_count = len(previous_completed)

            # 计算平均每天完成任务数
            avg_tasks_per_day = current_count / time_window_days

            # 计算当前周期花费的小时数
            hours_spent_this_week = sum(
                [t.actual_hours or 0 for t in current_completed]
            )

            # 判断趋势
            if current_count > previous_count * 1.1:
                trend = "increasing"
            elif current_count < previous_count * 0.9:
                trend = "decreasing"
            else:
                trend = "stable"

            return {
                "tasks_completed_this_week": current_count,
                "tasks_completed_last_week": previous_count,
                "avg_tasks_per_day": round(avg_tasks_per_day, 2),
                "hours_spent_this_week": hours_spent_this_week,
                "trend": trend,
                "time_window_days": time_window_days,
            }

    def _analyze_time_investment(self, project_id: str, days: int = 7) -> Dict:
        """
        分析项目的时间投入

        通过 WorkSession 数据分析用户在该项目上花费的时间

        Args:
            project_id: 项目 ID
            days: 分析天数

        Returns:
            {
                "total_hours": float,
                "avg_hours_per_day": float,
                "sessions_count": int
            }
        """
        cutoff_date = datetime.now() - timedelta(days=days)

        with self.db_context() as session:
            work_sessions = (
                session.query(WorkSession)
                .filter(
                    WorkSession.project_id == project_id,
                    WorkSession.start_time >= cutoff_date,
                )
                .all()
            )

            total_seconds = sum([ws.duration for ws in work_sessions])
            total_hours = total_seconds / 3600
            avg_hours_per_day = total_hours / days

            return {
                "total_hours": round(total_hours, 1),
                "avg_hours_per_day": round(avg_hours_per_day, 1),
                "sessions_count": len(work_sessions),
                "days_analyzed": days,
            }

    def _calculate_health_score(
        self,
        progress: Dict,
        bottlenecks: List[Dict],
        velocity: Dict,
        project_info: Dict,
    ) -> float:
        """
        计算项目健康度评分（0-10）

        综合考虑：
        1. 进度（40%）: 完成度 vs 时间进度
        2. 瓶颈（30%）: 瓶颈数量和严重程度
        3. 速度（20%）: 开发速度趋势
        4. 时间估算准确度（10%）: actual vs estimated

        Args:
            progress: 进度数据
            bottlenecks: 瓶颈列表
            velocity: 速度数据
            project_info: 项目信息

        Returns:
            float: 健康度评分 (0-10)
        """
        score = 0.0

        # 1. 进度评分（0-4 分）
        completion_percentage = progress.get("completion_percentage", 0)
        if completion_percentage >= 80:
            score += 4.0
        elif completion_percentage >= 60:
            score += 3.0
        elif completion_percentage >= 40:
            score += 2.0
        elif completion_percentage >= 20:
            score += 1.0

        # 2. 瓶颈评分（0-3 分）
        bottleneck_count = len(bottlenecks)
        if bottleneck_count == 0:
            score += 3.0
        elif bottleneck_count <= 2:
            score += 2.0
        elif bottleneck_count <= 5:
            score += 1.0
        # 否则 0 分

        # 3. 速度评分（0-2 分）
        trend = velocity.get("trend", "stable")
        if trend == "increasing":
            score += 2.0
        elif trend == "stable":
            score += 1.0
        # decreasing: 0 分

        # 4. 时间估算准确度评分（0-1 分）
        hours_variance = progress.get("hours_variance", 0)
        estimated_total = progress.get("estimated_total_hours", 1)
        if estimated_total > 0:
            variance_percentage = abs(hours_variance / estimated_total)
            if variance_percentage <= 0.1:  # 10% 以内
                score += 1.0
            elif variance_percentage <= 0.2:  # 20% 以内
                score += 0.5

        return round(min(score, 10.0), 1)
