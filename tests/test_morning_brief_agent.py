"""
测试 MorningBriefAgent
Phase 2 Week 3 Task 3.1 测试
"""

import pytest
from datetime import datetime, timedelta
from mirix.agents.morning_brief_agent import MorningBriefAgent
from mirix.orm.project import Project
from mirix.orm.task import Task
from mirix.orm.pattern import Pattern
from mirix.orm.insight import Insight


class TestMorningBriefAgent:
    """测试 MorningBriefAgent 的各项功能"""

    @pytest.fixture
    def morning_brief_agent(self, db_context):
        """创建 MorningBriefAgent 实例"""
        return MorningBriefAgent(db_context)

    @pytest.fixture
    def test_project(self, db_context, test_user, test_organization):
        """创建测试项目"""
        with db_context() as session:
            # 先删除可能存在的旧数据
            session.query(Project).filter_by(id="test-project-morning-brief").delete()
            session.commit()

            project = Project(
                id="test-project-morning-brief",
                name="Test Project",
                description="A test project",
                user_id=test_user.id,
                organization_id=test_organization.id,
                status="active",
                priority=8,
                progress=60,
                start_date=datetime.now() - timedelta(days=30),
                target_end_date=datetime.now() + timedelta(days=30),
            )
            session.add(project)
            session.commit()
            session.refresh(project)
            return project

    @pytest.fixture
    def test_tasks(self, db_context, test_user, test_organization, test_project):
        """创建测试任务"""
        with db_context() as session:
            # 先删除可能存在的旧任务数据
            task_ids = ["task-mb-1", "task-mb-2", "task-mb-3", "task-mb-4", "task-mb-5"]
            for task_id in task_ids:
                session.query(Task).filter_by(id=task_id).delete()
            session.commit()

            tasks = [
                # 高优先级任务（阻塞其他任务）
                Task(
                    id="task-mb-1",
                    title="Fix critical bug",
                    description="Urgent bug fix",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="in_progress",
                    priority=10,
                    blocking=True,
                    estimated_hours=4,
                    actual_hours=2,
                    due_date=datetime.now() + timedelta(days=1),
                ),
                # 今日到期任务
                Task(
                    id="task-mb-2",
                    title="Write documentation",
                    description="API documentation",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=7,
                    blocking=False,
                    estimated_hours=3,
                    due_date=datetime.now(),
                ),
                # 普通任务
                Task(
                    id="task-mb-3",
                    title="Code review",
                    description="Review PR #123",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=5,
                    blocking=False,
                    estimated_hours=2,
                    due_date=datetime.now() + timedelta(days=3),
                ),
                # 已逾期任务
                Task(
                    id="task-mb-4",
                    title="Update dependencies",
                    description="Update npm packages",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="todo",
                    priority=6,
                    blocking=False,
                    estimated_hours=1,
                    due_date=datetime.now() - timedelta(days=1),
                ),
                # 已完成任务
                Task(
                    id="task-mb-5",
                    title="Setup CI/CD",
                    description="Configure GitHub Actions",
                    project_id=test_project.id,
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    status="completed",
                    priority=8,
                    blocking=False,
                    estimated_hours=5,
                    actual_hours=6,
                ),
            ]

            for task in tasks:
                session.add(task)
            session.commit()
            return tasks

    @pytest.fixture
    def test_patterns(self, db_context, test_user, test_organization):
        """创建测试模式"""
        with db_context() as session:
            # 先删除可能存在的旧数据
            session.query(Pattern).filter_by(id="pattern-morning-brief-1").delete()
            session.commit()

            # 创建时间模式（高效时段）
            detected_time = datetime.now() - timedelta(days=1)
            pattern = Pattern(
                id="pattern-morning-brief-1",
                user_id=test_user.id,
                organization_id=test_organization.id,
                pattern_type="temporal",
                title="最高效时段：09:00-11:00",
                description="过去7天数据显示，你在 9-11am 的平均专注度为 8.5/10",
                confidence=0.85,
                frequency="daily",
                evidence=[
                    {"hour": 9, "avg_focus": 8.3},
                    {"hour": 10, "avg_focus": 8.7},
                ],
                first_detected=detected_time,
                last_confirmed=detected_time,
            )
            session.add(pattern)
            session.commit()
            return [pattern]

    @pytest.fixture
    def test_insights(self, db_context, test_user, test_organization):
        """创建测试洞察"""
        with db_context() as session:
            # 先删除可能存在的旧数据
            session.query(Insight).filter_by(id="insight-morning-brief-1").delete()
            session.commit()

            insight = Insight(
                id="insight-morning-brief-1",
                user_id=test_user.id,
                organization_id=test_organization.id,
                category="efficiency",
                title="优化深度工作时间安排",
                content="将核心编码任务安排在 09:00-11:00 高效时段",
                action_items=[
                    "将核心编码任务安排在 09:00-11:00",
                    "减少该时段的会议和沟通",
                    "设置免打扰模式以保护专注时间",
                ],
                priority=9,
                impact_score=8.5,
                status="active",
                created_at=datetime.now() - timedelta(days=1),
            )
            session.add(insight)
            session.commit()
            return [insight]

    def test_generate_brief_structure(
        self,
        morning_brief_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
        test_patterns,
        test_insights,
    ):
        """测试 generate_brief 返回结构"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        # 验证返回结构
        assert "date" in brief
        assert "greeting" in brief
        assert "yesterday_summary" in brief
        assert "today_priorities" in brief
        assert "reminders" in brief
        assert "optimal_schedule" in brief
        assert "motivational_message" in brief

        # 验证日期
        assert brief["date"] == today.date().isoformat()

        # 验证问候语
        assert isinstance(brief["greeting"], str)
        assert len(brief["greeting"]) > 0

        # 验证优先级列表
        assert isinstance(brief["today_priorities"], list)
        assert len(brief["today_priorities"]) > 0

    def test_priority_scoring(
        self,
        morning_brief_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
    ):
        """测试优先级评分算法"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        priorities = brief["today_priorities"]

        # 应该返回最多 5 个任务
        assert len(priorities) <= 5

        # 验证优先级排序（分数应该递减）
        scores = [p["priority_score"] for p in priorities]
        assert scores == sorted(scores, reverse=True)

        # 验证阻塞任务应该有更高优先级
        blocking_tasks = [p for p in priorities if p.get("blocking")]
        if blocking_tasks:
            # 阻塞任务的分数应该 >= 最低分数 + 20
            min_score = min(scores)
            for task in blocking_tasks:
                assert task["priority_score"] >= min_score + 20

    def test_reminders_generation(
        self,
        morning_brief_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
        test_insights,
    ):
        """测试提醒生成"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        reminders = brief["reminders"]

        # 应该有提醒
        assert len(reminders) > 0

        # 检查提醒结构
        for reminder in reminders:
            assert "type" in reminder
            assert "title" in reminder
            assert "content" in reminder
            assert "priority" in reminder

        # 应该包含逾期任务提醒
        overdue_reminders = [r for r in reminders if r["type"] == "overdue_task"]
        assert len(overdue_reminders) > 0

        # 应该包含今日到期任务提醒
        due_today_reminders = [r for r in reminders if r["type"] == "due_today"]
        assert len(due_today_reminders) > 0

    def test_optimal_schedule_suggestion(
        self,
        morning_brief_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
        test_patterns,
    ):
        """测试最佳时间安排建议"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        optimal_schedule = brief["optimal_schedule"]

        # 验证结构
        assert "productive_hours" in optimal_schedule
        assert "morning_tasks" in optimal_schedule
        assert "afternoon_tasks" in optimal_schedule

        # 验证高效时段
        productive_hours = optimal_schedule["productive_hours"]
        assert isinstance(productive_hours, list)
        assert 9 in productive_hours  # 基于 test_patterns
        assert 10 in productive_hours

        # 验证任务分配
        morning_tasks = optimal_schedule["morning_tasks"]
        assert isinstance(morning_tasks, list)

        # 早晨任务应该是高优先级的
        if morning_tasks:
            for task in morning_tasks:
                assert task["priority_score"] >= 60  # 高分任务

    def test_motivational_message(
        self, morning_brief_agent, test_user, test_organization, test_project
    ):
        """测试激励信息生成"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        motivational_message = brief["motivational_message"]

        # 应该有激励信息
        assert isinstance(motivational_message, str)
        assert len(motivational_message) > 0

    def test_no_tasks(self, morning_brief_agent, db_context, test_user, test_organization):
        """测试无任务情况"""
        # 清理所有任务和项目
        with db_context() as session:
            session.query(Task).filter_by(user_id=test_user.id).delete()
            session.query(Project).filter_by(user_id=test_user.id).delete()
            session.commit()

        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        # 应该仍然能生成简报
        assert "date" in brief
        assert "greeting" in brief

        # 优先级列表应该为空
        assert brief["today_priorities"] == []

    def test_no_patterns(
        self,
        morning_brief_agent,
        test_user,
        test_organization,
        test_project,
        test_tasks,
    ):
        """测试无模式情况"""
        today = datetime.now()
        brief = morning_brief_agent.generate_brief(
            today, test_user.id, test_organization.id
        )

        optimal_schedule = brief["optimal_schedule"]

        # 应该有默认的高效时段建议
        assert "productive_hours" in optimal_schedule
        # 即使没有模式，也应该有任务分配
        assert "morning_tasks" in optimal_schedule
        assert "afternoon_tasks" in optimal_schedule
