"""
ReminderAgent - Phase 2 Week 3 Task 3.3
检测用户分心行为并发送专注提醒（简化版）
"""

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional

from mirix.orm.work_session import WorkSession


class ReminderAgent:
    """
    提醒 Agent（简化版）

    职责：
    1. 检测用户分心（连续使用娱乐应用）
    2. 发送专注提醒
    3. （可选）休息提醒
    """

    # 娱乐应用列表
    ENTERTAINMENT_APPS = [
        "YouTube",
        "Netflix",
        "Hulu",
        "Disney+",
        "Prime Video",
        "Twitter",
        "X",
        "Instagram",
        "TikTok",
        "Reddit",
        "Facebook",
        "Snapchat",
        "Twitch",
        "Steam",
        "Epic Games",
        "PlayStation",
        "Xbox",
        "Nintendo",
        "Spotify",
        "Apple Music",
        "Weibo",
        "Bilibili",
        "Douyin",
        "抖音",
        "快手",
        "小红书",
    ]

    # 休息提醒间隔（分钟）
    BREAK_REMINDER_INTERVAL_MINUTES = 90

    # 分心检测阈值（分钟）
    DISTRACTION_THRESHOLD_MINUTES = 15

    def __init__(self, db_context):
        """
        初始化 ReminderAgent

        Args:
            db_context: 数据库上下文管理器
        """
        self.db_context = db_context

    def check_and_remind(
        self, user_id: str, organization_id: str
    ) -> List[Dict[str, Any]]:
        """
        检查并生成提醒

        Args:
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            提醒列表:
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
        reminders = []

        # 1. 检测分心行为
        distraction_reminder = self._check_distraction(user_id, organization_id)
        if distraction_reminder:
            reminders.append(distraction_reminder)

        # 2. 检测是否需要休息（可选）
        break_reminder = self._check_break_needed(user_id, organization_id)
        if break_reminder:
            reminders.append(break_reminder)

        return reminders

    def _check_distraction(
        self, user_id: str, organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        检测分心行为

        检查最近 15 分钟的应用使用情况，如果连续使用娱乐应用，
        则生成专注提醒

        Args:
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            专注提醒（如果检测到分心），否则 None
        """
        time_window_minutes = self.DISTRACTION_THRESHOLD_MINUTES
        cutoff_time = datetime.now() - timedelta(minutes=time_window_minutes)

        with self.db_context() as session:
            recent_sessions = (
                session.query(WorkSession)
                .filter(
                    WorkSession.user_id == user_id,
                    WorkSession.organization_id == organization_id,
                    WorkSession.start_time >= cutoff_time,
                )
                .order_by(WorkSession.start_time.desc())
                .all()
            )

            if not recent_sessions:
                return None

            # 计算娱乐应用使用时间
            entertainment_time = 0
            total_time = 0
            entertainment_apps_used = set()

            for session in recent_sessions:
                total_time += session.duration

                # 检查会话中的应用
                if session.app_breakdown:
                    for app_name, duration in session.app_breakdown.items():
                        if self._is_entertainment_app(app_name):
                            entertainment_time += duration
                            entertainment_apps_used.add(app_name)

            # 如果娱乐应用使用时间超过阈值（10 分钟）
            entertainment_minutes = entertainment_time / 60
            if entertainment_minutes >= 10:
                return {
                    "type": "focus_reminder",
                    "title": "专注提醒",
                    "content": self._generate_focus_reminder_content(
                        entertainment_minutes, list(entertainment_apps_used)
                    ),
                    "priority": 7,
                    "timestamp": datetime.now(),
                    "metadata": {
                        "entertainment_time_minutes": round(entertainment_minutes, 1),
                        "total_time_minutes": round(total_time / 60, 1),
                        "entertainment_apps": list(entertainment_apps_used),
                    },
                }

            return None

    def _check_break_needed(
        self, user_id: str, organization_id: str
    ) -> Optional[Dict[str, Any]]:
        """
        检测是否需要休息

        如果用户连续工作超过 90 分钟，建议休息

        Args:
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            休息提醒（如果需要），否则 None
        """
        # 检查最近 2 小时的工作会话
        cutoff_time = datetime.now() - timedelta(hours=2)

        with self.db_context() as session:
            recent_sessions = (
                session.query(WorkSession)
                .filter(
                    WorkSession.user_id == user_id,
                    WorkSession.organization_id == organization_id,
                    WorkSession.start_time >= cutoff_time,
                    WorkSession.activity_type.in_(
                        ["coding", "writing", "meeting", "research"]
                    ),
                )
                .order_by(WorkSession.start_time.asc())
                .all()
            )

            if not recent_sessions:
                return None

            # 计算连续工作时间
            continuous_work_time = self._calculate_continuous_work_time(
                recent_sessions
            )

            # 如果连续工作时间超过 90 分钟，建议休息
            continuous_minutes = continuous_work_time / 60
            if continuous_minutes >= self.BREAK_REMINDER_INTERVAL_MINUTES:
                return {
                    "type": "break_reminder",
                    "title": "休息提醒",
                    "content": f"你已经连续工作 {int(continuous_minutes)} 分钟了，建议休息 10-15 分钟，活动一下身体，眺望远方，让眼睛和大脑放松。",
                    "priority": 5,
                    "timestamp": datetime.now(),
                    "metadata": {
                        "continuous_work_minutes": round(continuous_minutes, 1),
                    },
                }

            return None

    def _calculate_continuous_work_time(
        self, sessions: List[WorkSession]
    ) -> float:
        """
        计算连续工作时间（秒）

        连续工作定义：相邻会话间隔小于 15 分钟

        Args:
            sessions: 工作会话列表（按时间升序）

        Returns:
            连续工作时间（秒）
        """
        if not sessions:
            return 0

        continuous_time = 0
        last_end_time = None

        for session in sessions:
            session_end_time = session.start_time + timedelta(seconds=session.duration)

            if last_end_time is None:
                # 第一个会话
                continuous_time = session.duration
            else:
                # 计算与上一个会话的间隔
                gap = (session.start_time - last_end_time).total_seconds()

                if gap <= 15 * 60:  # 间隔小于 15 分钟，算作连续
                    continuous_time += session.duration
                else:
                    # 间隔过大，重新开始计算
                    continuous_time = session.duration

            last_end_time = session_end_time

        return continuous_time

    def _is_entertainment_app(self, app_name: str) -> bool:
        """
        判断是否为娱乐应用

        Args:
            app_name: 应用名称

        Returns:
            True if 是娱乐应用, False otherwise
        """
        # 不区分大小写匹配
        app_name_lower = app_name.lower()

        for entertainment_app in self.ENTERTAINMENT_APPS:
            if entertainment_app.lower() in app_name_lower:
                return True

        return False

    def _generate_focus_reminder_content(
        self, entertainment_minutes: float, apps_used: List[str]
    ) -> str:
        """
        生成专注提醒内容

        Args:
            entertainment_minutes: 娱乐应用使用时间（分钟）
            apps_used: 使用的娱乐应用列表

        Returns:
            提醒内容
        """
        apps_str = "、".join(apps_used[:3])  # 最多显示 3 个应用
        if len(apps_used) > 3:
            apps_str += " 等"

        return (
            f"检测到你在过去 {int(entertainment_minutes)} 分钟内使用了 {apps_str} 等娱乐应用。\n\n"
            f"建议：\n"
            f"• 关闭娱乐应用，回到工作任务\n"
            f"• 使用番茄工作法，专注 25 分钟后再休息\n"
            f"• 开启勿扰模式，减少干扰"
        )
