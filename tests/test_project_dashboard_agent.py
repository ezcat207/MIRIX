"""
测试 ProjectDashboardAgent
Phase 2 Week 3 Task 3.2 测试
"""

import pytest
from datetime import datetime, timedelta
from mirix.agents.project_dashboard_agent import ProjectDashboardAgent
from mirix.orm.project import Project
from mirix.orm.task import Task
from mirix.orm.work_session import WorkSession


class TestProjectDashboardAgent:
    """测试 ProjectDashboardAgent 的各项功能"""

    @pytest.fixture
    def dashboard_agent(self, db_context):
        """创建 ProjectDashboardAgent 实例"""
        return ProjectDashboardAgent(db_context)

    @pytest.fixture
    def test_project(self, db_context, test_user, test_organization):
        """创建测试项目"""
        with db_context() as session:
            # 先删除可能存在的旧数据
            session.query(Task).filter(Task.project_id == "test-project-dashboard").delete()
            session.query(WorkSession).filter(WorkSession.project_id == "test-project-dashboard").delete()
            session.query(Project).filter_by(id="test-project-dashboard").delete()
            session.commit()

            project = Project(
                id="test-project-dashboard",
                name="Dashboard Test Project",
                description="Testing project dashboard features",
                user_id=test_user.id,
                organization_id=test_organization.id,
                status="active",
                priority=8,
                progress=50,
                total_time_spent=36000,  # 10 hours
                start_date=datetime.now() - timedelta(days=30),
                target_end_date=datetime.now() + timedelta(days=30),
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return project

    @pytest.fixture
    def test_tasks(self, db_context, test_user, test_organization, test_project):
        """创建测试任务（包含各种场景）"""
        with db_context() as session:
            tasks = [
                # 已完成任务
                Task(
                    id="task-completed-1",
                    title="Completed Task 1",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="completed",
                    priority=8,
                    estimated_hours=5,
                    actual_hours=6,
                    updated_at=datetime.now() - timedelta(days=2),
                ),
                Task(
                    id="task-completed-2",
                    title="Completed Task 2",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="completed",
                    priority=7,
                    estimated_hours=3,
                    actual_hours=3,
                    updated_at=datetime.now() - timedelta(days=5),
                ),
                # 进行中任务（正常）
                Task(
                    id="task-in-progress-normal",
                    title="In Progress Normal",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="in_progress",
                    priority=9,
                    estimated_hours=4,
                    actual_hours=2,
                    updated_at=datetime.now() - timedelta(days=1),
                ),
                # 进行中任务（长期未更新 - 瓶颈）
                Task(
                    id="task-in-progress-stale",
                    title="In Progress Stale",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="in_progress",
                    priority=8,
                    estimated_hours=5,
                    actual_hours=3,
                    updated_at=datetime.now() - timedelta(days=10),  # 10天未更新
                ),
                # 待办任务（阻塞其他任务 - 瓶颈）
                Task(
                    id="task-todo-blocking",
                    title="Todo Blocking",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=10,
                    blocking=True,
                    estimated_hours=6,
                ),
                # 待办任务（已逾期 - 瓶颈）
                Task(
                    id="task-todo-overdue",
                    title="Todo Overdue",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=7,
                    estimated_hours=3,
                    due_date=datetime.now() - timedelta(days=3),  # 逾期3天
                ),
                # 待办任务（超时 - 瓶颈）
                Task(
                    id="task-overtime",
                    title="Overtime Task",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="in_progress",
                    priority=6,
                    estimated_hours=4,
                    actual_hours=8,  # 超时 100%
                ),
                # 普通待办任务
                Task(
                    id="task-todo-normal",
                    title="Todo Normal",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=5,
                    estimated_hours=2,
                ),
            ]

            for task in tasks:
                session.add(task)
            session.commit()
            return tasks

    @pytest.fixture
    def test_work_sessions(
        self, db_context, test_user, test_organization, test_project
    ):
        """创建测试工作会话"""
        with db_context() as session:
            sessions = []

            # 最近7天的工作会话
            for i in range(7):
                session_date = datetime.now() - timedelta(days=i)
                work_session = WorkSession(
                    id=f"ws-{i}",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    project_id=test_project.id,
                    activity_type="coding",
                    start_time=session_date,
                    duration=3600,  # 1小时
                    focus_score=7.5,
                )
                session.add(work_session)
                sessions.append(work_session)

            session.commit()
            return sessions

    def test_get_dashboard_data_structure(
        self,
        dashboard_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
        test_work_sessions,
    ):
        """测试 get_dashboard_data 返回结构"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        # 验证返回结构
        assert "project_info" in dashboard
        assert "progress" in dashboard
        assert "tasks" in dashboard
        assert "bottlenecks" in dashboard
        assert "velocity" in dashboard
        assert "time_investment" in dashboard
        assert "health_score" in dashboard

        # 验证项目信息
        project_info = dashboard["project_info"]
        assert project_info["exists"] is True
        assert project_info["id"] == test_project.id
        assert project_info["name"] == test_project.name

    def test_calculate_progress(
        self, dashboard_agent, test_user, test_organization, test_project, test_tasks
    ):
        """测试进度计算"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        progress = dashboard["progress"]

        # 验证结构
        assert "total_tasks" in progress
        assert "completed_tasks" in progress
        assert "in_progress_tasks" in progress
        assert "todo_tasks" in progress
        assert "completion_percentage" in progress
        assert "estimated_total_hours" in progress
        assert "actual_total_hours" in progress
        assert "hours_variance" in progress

        # 验证数值
        assert progress["total_tasks"] == 8
        assert progress["completed_tasks"] == 2
        assert progress["in_progress_tasks"] == 3
        assert progress["todo_tasks"] == 3

        # 验证完成百分比
        expected_percentage = (2 / 8) * 100
        assert progress["completion_percentage"] == round(expected_percentage, 1)

    def test_get_tasks_grouped(
        self, dashboard_agent, test_user, test_organization, test_project, test_tasks
    ):
        """测试任务分组"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        tasks = dashboard["tasks"]

        # 验证分组结构
        assert "todo" in tasks
        assert "in_progress" in tasks
        assert "completed" in tasks

        # 验证任务数量
        assert len(tasks["completed"]) == 2
        assert len(tasks["in_progress"]) == 3
        assert len(tasks["todo"]) == 3

        # 验证任务数据结构
        for task in tasks["todo"]:
            assert "id" in task
            assert "title" in task
            assert "status" in task
            assert "priority" in task

    def test_identify_bottlenecks(
        self, dashboard_agent, test_user, test_organization, test_project, test_tasks
    ):
        """测试瓶颈识别"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        bottlenecks = dashboard["bottlenecks"]

        # 应该识别出 4 个瓶颈
        # 1. task-todo-blocking (阻塞其他任务)
        # 2. task-todo-overdue (已逾期)
        # 3. task-in-progress-stale (长期未更新)
        # 4. task-overtime (超时)
        assert len(bottlenecks) >= 4

        # 验证瓶颈数据结构
        for bottleneck in bottlenecks:
            assert "task_id" in bottleneck
            assert "task_title" in bottleneck
            assert "reasons" in bottleneck
            assert "priority" in bottleneck
            assert "status" in bottleneck

        # 验证特定瓶颈
        blocking_bottleneck = next(
            (b for b in bottlenecks if b["task_id"] == "task-todo-blocking"), None
        )
        assert blocking_bottleneck is not None
        assert "阻塞其他任务" in blocking_bottleneck["reasons"]

        overdue_bottleneck = next(
            (b for b in bottlenecks if b["task_id"] == "task-todo-overdue"), None
        )
        assert overdue_bottleneck is not None
        assert any("逾期" in reason for reason in overdue_bottleneck["reasons"])

        stale_bottleneck = next(
            (b for b in bottlenecks if b["task_id"] == "task-in-progress-stale"), None
        )
        assert stale_bottleneck is not None
        assert any("进行中" in reason for reason in stale_bottleneck["reasons"])

    def test_calculate_velocity(
        self,
        dashboard_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
    ):
        """测试速度计算"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        velocity = dashboard["velocity"]

        # 验证结构
        assert "tasks_completed_this_week" in velocity
        assert "tasks_completed_last_week" in velocity
        assert "avg_tasks_per_day" in velocity
        assert "hours_spent_this_week" in velocity
        assert "trend" in velocity
        assert "time_window_days" in velocity

        # 验证趋势值
        assert velocity["trend"] in ["increasing", "stable", "decreasing"]

    def test_analyze_time_investment(
        self,
        dashboard_agent,
        test_user,
        test_organization,
        test_project,
        test_work_sessions,
    ):
        """测试时间投入分析"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        time_investment = dashboard["time_investment"]

        # 验证结构
        assert "total_hours" in time_investment
        assert "avg_hours_per_day" in time_investment
        assert "sessions_count" in time_investment
        assert "days_analyzed" in time_investment

        # 验证数值
        assert time_investment["sessions_count"] == 7  # 7天的会话
        assert time_investment["total_hours"] == 7.0  # 7小时（每天1小时）
        assert time_investment["avg_hours_per_day"] == 1.0

    def test_calculate_health_score(
        self,
        dashboard_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
    ):
        """测试健康度评分"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        health_score = dashboard["health_score"]

        # 验证评分范围
        assert 0 <= health_score <= 10

        # 验证是浮点数
        assert isinstance(health_score, float)

    def test_health_score_components(
        self,
        dashboard_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
    ):
        """测试健康度评分的各个组成部分"""
        dashboard = dashboard_agent.get_dashboard_data(
            test_project.id, test_user.id, test_organization.id
        )

        progress = dashboard["progress"]
        bottlenecks = dashboard["bottlenecks"]
        velocity = dashboard["velocity"]
        health_score = dashboard["health_score"]

        # 如果进度低，健康度应该低
        if progress["completion_percentage"] < 20:
            assert health_score < 5.0

        # 如果瓶颈多，健康度应该低
        if len(bottlenecks) > 5:
            assert health_score < 6.0

    def test_project_not_found(
        self, dashboard_agent, test_user, test_organization
    ):
        """测试项目不存在的情况"""
        dashboard = dashboard_agent.get_dashboard_data(
            "non-existent-project", test_user.id, test_organization.id
        )

        project_info = dashboard["project_info"]

        # 应该标记为不存在
        assert project_info["exists"] is False
        assert "error" in project_info

    def test_no_tasks_project(
        self, dashboard_agent, test_user, test_organization
    ):
        """测试无任务的项目"""
        # 创建一个没有任务的项目
        with dashboard_agent.db_context() as session:
            # 先删除可能存在的旧数据
            session.query(Project).filter_by(id="empty-project-dashboard").delete()
            session.commit()

            empty_project = Project(
                id="empty-project-dashboard",
                name="Empty Project",
                user_id=test_user.id,
                organization_id=test_organization.id,
                status="active",
                priority=5,
            )
            session.add(empty_project)
            session.commit()

        dashboard = dashboard_agent.get_dashboard_data(
            "empty-project-dashboard", test_user.id, test_organization.id
        )

        progress = dashboard["progress"]
        tasks = dashboard["tasks"]
        bottlenecks = dashboard["bottlenecks"]

        # 验证空项目的数据
        assert progress["total_tasks"] == 0
        assert progress["completion_percentage"] == 0
        assert len(tasks["todo"]) == 0
        assert len(tasks["in_progress"]) == 0
        assert len(tasks["completed"]) == 0
        assert len(bottlenecks) == 0
