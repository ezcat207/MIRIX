"""
测试 ReminderAgent
Phase 2 Week 3 Task 3.3 测试
"""

import pytest
from datetime import datetime, timedelta
from mirix.agents.reminder_agent import ReminderAgent
from mirix.orm.work_session import WorkSession


class TestReminderAgent:
    """测试 ReminderAgent 的各项功能"""

    @pytest.fixture
    def reminder_agent(self, db_context):
        """创建 ReminderAgent 实例"""
        return ReminderAgent(db_context)

    @pytest.fixture
    def clean_reminder_sessions(self, db_context):
        """测试后清理工作会话"""
        yield
        with db_context() as session:
            session.query(WorkSession).filter(
                WorkSession.id.like("reminder-test-%")
            ).delete()
            session.commit()

    def test_no_distraction(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试无分心情况"""
        # 创建正常工作会话（编码）
        with db_context() as session:
            work_session = WorkSession(
                id="reminder-test-ws-1",
                user_id=test_user.id,
                organization_id=test_organization.id,
                activity_type="coding",
                start_time=datetime.now() - timedelta(minutes=20),
                duration=1200,  # 20分钟
                focus_score=8.0,
                app_breakdown={"VSCode": 1000, "Terminal": 200},
            )
            session.add(work_session)
            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 不应该有专注提醒
        focus_reminders = [r for r in reminders if r["type"] == "focus_reminder"]
        assert len(focus_reminders) == 0

    def test_distraction_detected(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试检测到分心行为"""
        # 创建娱乐应用会话（YouTube）
        with db_context() as session:
            work_session = WorkSession(
                id="reminder-test-ws-2",
                user_id=test_user.id,
                organization_id=test_organization.id,
                activity_type="entertainment",
                start_time=datetime.now() - timedelta(minutes=12),
                duration=720,  # 12分钟
                focus_score=3.0,
                app_breakdown={"YouTube": 600, "Chrome": 120},
            )
            session.add(work_session)
            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 应该有专注提醒
        focus_reminders = [r for r in reminders if r["type"] == "focus_reminder"]
        assert len(focus_reminders) == 1

        # 验证提醒内容
        reminder = focus_reminders[0]
        assert reminder["title"] == "专注提醒"
        assert "YouTube" in reminder["content"]
        assert reminder["priority"] == 7

        # 验证元数据
        assert "metadata" in reminder
        metadata = reminder["metadata"]
        assert "entertainment_time_minutes" in metadata
        assert metadata["entertainment_time_minutes"] >= 10

    def test_multiple_entertainment_apps(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试多个娱乐应用的情况"""
        # 创建多个娱乐应用会话
        with db_context() as session:
            work_session = WorkSession(
                id="reminder-test-ws-3",
                user_id=test_user.id,
                organization_id=test_organization.id,
                activity_type="entertainment",
                start_time=datetime.now() - timedelta(minutes=15),
                duration=900,  # 15分钟
                focus_score=2.5,
                app_breakdown={
                    "YouTube": 400,
                    "Twitter": 300,
                    "Instagram": 200,
                },
            )
            session.add(work_session)
            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        focus_reminders = [r for r in reminders if r["type"] == "focus_reminder"]
        assert len(focus_reminders) == 1

        reminder = focus_reminders[0]
        # 应该提到至少一个娱乐应用
        assert any(
            app in reminder["content"]
            for app in ["YouTube", "Twitter", "Instagram"]
        )

    def test_entertainment_app_detection(self, reminder_agent):
        """测试娱乐应用检测"""
        # 测试已知娱乐应用
        assert reminder_agent._is_entertainment_app("YouTube") is True
        assert reminder_agent._is_entertainment_app("Netflix") is True
        assert reminder_agent._is_entertainment_app("Twitter") is True
        assert reminder_agent._is_entertainment_app("Instagram") is True
        assert reminder_agent._is_entertainment_app("TikTok") is True
        assert reminder_agent._is_entertainment_app("Bilibili") is True

        # 测试非娱乐应用
        assert reminder_agent._is_entertainment_app("VSCode") is False
        assert reminder_agent._is_entertainment_app("Terminal") is False
        assert reminder_agent._is_entertainment_app("Chrome") is False
        assert reminder_agent._is_entertainment_app("Notion") is False

        # 测试大小写不敏感
        assert reminder_agent._is_entertainment_app("youtube") is True
        assert reminder_agent._is_entertainment_app("NETFLIX") is True

        # 测试部分匹配
        assert reminder_agent._is_entertainment_app("YouTube.app") is True
        assert reminder_agent._is_entertainment_app("com.netflix.app") is True

    def test_break_reminder_needed(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试休息提醒（连续工作超过90分钟）"""
        # 创建连续工作会话（超过90分钟）
        with db_context() as session:
            # 第一个会话：60分钟
            session.add(
                WorkSession(
                    id="reminder-test-ws-4",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=100),
                    duration=3600,  # 60分钟
                    focus_score=8.0,
                )
            )

            # 第二个会话：40分钟（间隔10分钟）
            session.add(
                WorkSession(
                    id="reminder-test-ws-5",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=50),
                    duration=2400,  # 40分钟
                    focus_score=7.5,
                )
            )

            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 应该有休息提醒
        break_reminders = [r for r in reminders if r["type"] == "break_reminder"]
        assert len(break_reminders) == 1

        # 验证提醒内容
        reminder = break_reminders[0]
        assert reminder["title"] == "休息提醒"
        assert "连续工作" in reminder["content"]
        assert reminder["priority"] == 5

    def test_no_break_reminder_with_gaps(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试有间隔的工作不触发休息提醒"""
        # 创建有较大间隔的工作会话
        with db_context() as session:
            # 第一个会话：60分钟
            session.add(
                WorkSession(
                    id="reminder-test-ws-6",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=100),
                    duration=3600,  # 60分钟
                    focus_score=8.0,
                )
            )

            # 第二个会话：40分钟（间隔 20 分钟，超过阈值）
            session.add(
                WorkSession(
                    id="reminder-test-ws-7",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=40),
                    duration=2400,  # 40分钟
                    focus_score=7.5,
                )
            )

            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 不应该有休息提醒（因为间隔超过15分钟）
        break_reminders = [r for r in reminders if r["type"] == "break_reminder"]
        assert len(break_reminders) == 0

    def test_continuous_work_time_calculation(self, reminder_agent, db_context, test_user, test_organization):
        """测试连续工作时间计算"""
        # 创建测试会话
        with db_context() as session:
            sessions = [
                WorkSession(
                    id="reminder-test-ws-8",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=100),
                    duration=1800,  # 30分钟
                    focus_score=8.0,
                ),
                WorkSession(
                    id="reminder-test-ws-9",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=60),
                    duration=1800,  # 30分钟
                    focus_score=7.5,
                ),
            ]
            for s in sessions:
                session.add(s)
            session.commit()

            # 计算连续工作时间
            continuous_time = reminder_agent._calculate_continuous_work_time(sessions)

            # 应该是 60 分钟（两个30分钟会话，间隔小于15分钟）
            assert continuous_time == 3600  # 秒

    def test_no_recent_activity(
        self, reminder_agent, test_user, test_organization
    ):
        """测试无最近活动的情况"""
        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 不应该有任何提醒
        assert len(reminders) == 0

    def test_mixed_activity(
        self, reminder_agent, db_context, test_user, test_organization, clean_reminder_sessions
    ):
        """测试混合活动（工作+娱乐）"""
        # 创建混合会话
        with db_context() as session:
            # 工作会话
            session.add(
                WorkSession(
                    id="reminder-test-ws-10",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="coding",
                    start_time=datetime.now() - timedelta(minutes=20),
                    duration=600,  # 10分钟
                    focus_score=7.0,
                    app_breakdown={"VSCode": 600},
                )
            )

            # 娱乐会话（短，不应触发提醒）
            session.add(
                WorkSession(
                    id="reminder-test-ws-11",
                    user_id=test_user.id,
                    organization_id=test_organization.id,
                    activity_type="entertainment",
                    start_time=datetime.now() - timedelta(minutes=5),
                    duration=300,  # 5分钟
                    focus_score=4.0,
                    app_breakdown={"YouTube": 300},
                )
            )

            session.commit()

        reminders = reminder_agent.check_and_remind(test_user.id, test_organization.id)

        # 娱乐时间不足10分钟，不应该有专注提醒
        focus_reminders = [r for r in reminders if r["type"] == "focus_reminder"]
        assert len(focus_reminders) == 0

    def test_reminder_content_generation(self, reminder_agent):
        """测试提醒内容生成"""
        content = reminder_agent._generate_focus_reminder_content(
            15.0, ["YouTube", "Twitter"]
        )

        # 验证内容包含关键信息
        assert "15" in content
        assert "YouTube" in content or "Twitter" in content
        assert "建议" in content
