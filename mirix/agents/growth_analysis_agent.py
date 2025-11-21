"""
GrowthAnalysisAgent - Phase 2 核心 Agent
负责分析用户工作数据，生成复盘报告、洞察和模式发现
"""

import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any

from mirix.orm.work_session import WorkSession
from mirix.orm.pattern import Pattern
from mirix.orm.insight import Insight
from mirix.services.raw_memory_manager import RawMemoryManager


class GrowthAnalysisAgent:
    """
    成长分析 Agent - 核心业务逻辑

    职责：
    1. 从 raw_memory 生成 WorkSession
    2. 分析时间分配
    3. 计算效率指标
    4. 发现行为模式
    5. 生成可执行洞察
    6. 组装每日/周度复盘报告
    """

    def __init__(self, db_context):
        """
        初始化 GrowthAnalysisAgent

        Args:
            db_context: 数据库上下文管理器 (from mirix.server.server import db_context)
        """
        self.db_context = db_context
        self.raw_memory_manager = RawMemoryManager()

    def daily_review(
        self, date: datetime, user_id: str, organization_id: str
    ) -> Dict[str, Any]:
        """
        生成每日复盘报告

        Args:
            date: 复盘日期（只看日期部分，时间设为 00:00:00）
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            完整的每日复盘报告，包含：
            - work_sessions: 工作会话列表
            - time_allocation: 时间分配统计
            - efficiency_metrics: 效率指标
            - patterns: 发现的模式
            - insights: 可执行洞察
            - summary: 文字总结

        Example:
            report = agent.daily_review(
                date=datetime(2025, 1, 21),
                user_id="user-123",
                organization_id="org-456"
            )
        """
        # Step 1: 获取当天的 raw_memory 数据
        start_of_day = date.replace(hour=0, minute=0, second=0, microsecond=0)
        end_of_day = date.replace(hour=23, minute=59, second=59, microsecond=999999)

        raw_memories = self._get_memories_for_date(
            user_id, organization_id, start_of_day, end_of_day
        )

        # Step 2: 生成 WorkSession
        work_sessions = self._generate_work_sessions(
            raw_memories, user_id, organization_id
        )

        # Step 3: 分析时间分配
        time_allocation = self._analyze_time_allocation(work_sessions)

        # Step 4: 计算效率指标
        efficiency_metrics = self._calculate_efficiency(work_sessions)

        # Step 5: 发现每日模式
        patterns = self._discover_daily_patterns(
            work_sessions, time_allocation, user_id, organization_id
        )

        # Step 6: 生成洞察
        insights = self._generate_insights(
            patterns, efficiency_metrics, user_id, organization_id
        )

        # Step 7: 组装报告
        report = {
            "date": date.isoformat(),
            "user_id": user_id,
            "work_sessions": [self._serialize_work_session(ws) for ws in work_sessions],
            "time_allocation": time_allocation,
            "efficiency_metrics": efficiency_metrics,
            "patterns": [self._serialize_pattern(p) for p in patterns],
            "insights": [self._serialize_insight(i) for i in insights],
            "summary": self._generate_summary(
                work_sessions, time_allocation, efficiency_metrics, patterns, insights
            ),
        }

        return report

    # ========================================================================
    # Task 2.1: WorkSession 生成逻辑
    # ========================================================================

    def _get_memories_for_date(
        self,
        user_id: str,
        organization_id: str,
        start_time: datetime,
        end_time: datetime,
    ) -> List:
        """
        获取指定日期的所有 raw_memory 数据

        Args:
            user_id: 用户 ID
            organization_id: 组织 ID
            start_time: 开始时间
            end_time: 结束时间

        Returns:
            按时间排序的 RawMemoryItem 列表
        """
        return self.raw_memory_manager.get_memories_in_range(
            user_id=user_id,
            organization_id=organization_id,
            start_time=start_time,
            end_time=end_time,
            limit=2000,  # 一天最多 2000 条记录
        )

    def _generate_work_sessions(
        self, raw_memories: List, user_id: str, organization_id: str
    ) -> List[WorkSession]:
        """
        从 raw_memory 生成 WorkSession

        核心算法：
        1. 按时间顺序遍历 raw_memory
        2. 识别连续工作时段（同一 app 或相关 app，时间间隔 < 5 分钟）
        3. 合并成 WorkSession
        4. 计算 focus_score（基于 context switches 频率）
        5. 生成 app_breakdown 统计

        Args:
            raw_memories: RawMemoryItem 列表（已按时间排序）
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            生成的 WorkSession 列表
        """
        if not raw_memories:
            return []

        work_sessions = []
        current_session = None
        max_gap_seconds = 300  # 5 分钟间隔阈值

        # 按时间正序排列（从早到晚）
        sorted_memories = sorted(raw_memories, key=lambda m: m.captured_at)

        for memory in sorted_memories:
            if current_session is None:
                # 开始新的 session
                current_session = self._create_new_session(
                    memory, user_id, organization_id
                )
            else:
                # 检查是否应该合并到当前 session
                time_gap = (
                    memory.captured_at - current_session["last_activity_time"]
                ).total_seconds()

                if time_gap <= max_gap_seconds and self._is_related_activity(
                    current_session["current_app"], memory.source_app
                ):
                    # 合并到当前 session
                    self._merge_memory_to_session(current_session, memory)
                else:
                    # 保存当前 session，开始新的 session
                    work_sessions.append(
                        self._finalize_session(current_session, user_id, organization_id)
                    )
                    current_session = self._create_new_session(
                        memory, user_id, organization_id
                    )

        # 保存最后一个 session
        if current_session:
            work_sessions.append(
                self._finalize_session(current_session, user_id, organization_id)
            )

        return work_sessions

    def _create_new_session(
        self, memory, user_id: str, organization_id: str
    ) -> Dict:
        """创建新的工作会话（临时字典结构）"""
        return {
            "start_time": memory.captured_at,
            "last_activity_time": memory.captured_at,
            "current_app": memory.source_app,
            "app_times": {memory.source_app: 0},  # 实际时长稍后计算
            "raw_memory_ids": [memory.id],
            "context_switches": 0,
            "activities": [memory.source_app],
            "user_id": user_id,
            "organization_id": organization_id,
        }

    def _merge_memory_to_session(self, session: Dict, memory) -> None:
        """将 memory 合并到当前 session"""
        # 更新时间
        time_elapsed = (
            memory.captured_at - session["last_activity_time"]
        ).total_seconds()
        session["last_activity_time"] = memory.captured_at

        # 更新 app 时间统计（将间隔时间分配给上一个 app）
        if session["current_app"] in session["app_times"]:
            session["app_times"][session["current_app"]] += time_elapsed
        else:
            session["app_times"][session["current_app"]] = time_elapsed

        # 检测 context switch
        if memory.source_app != session["current_app"]:
            session["context_switches"] += 1
            session["current_app"] = memory.source_app

        # 添加到 activities 和 raw_memory_ids
        session["activities"].append(memory.source_app)
        session["raw_memory_ids"].append(memory.id)

    def _finalize_session(
        self, session_dict: Dict, user_id: str, organization_id: str
    ) -> WorkSession:
        """
        将临时 session 字典转换为 WorkSession ORM 对象

        计算：
        - duration: 总时长（秒）
        - focus_score: 专注度评分（0-10）
        - activity_type: 活动类型（coding, meeting, research, etc.）
        """
        duration = int(
            (session_dict["last_activity_time"] - session_dict["start_time"]).total_seconds()
        )

        # 计算 focus_score（基于 context switches 频率）
        # 公式：10 - (context_switches / duration_minutes * 2)
        # 含义：每分钟切换越少，专注度越高
        duration_minutes = max(duration / 60, 1)
        context_switch_rate = session_dict["context_switches"] / duration_minutes
        focus_score = max(0.0, min(10.0, 10.0 - (context_switch_rate * 2)))

        # 推断活动类型（基于主要使用的 app）
        activity_type = self._infer_activity_type(session_dict["app_times"])

        # 可能关联的项目（TODO: 在后续任务中实现智能匹配）
        project_id = None

        # 创建 WorkSession ORM 对象
        work_session = WorkSession(
            id=f"worksession-{uuid.uuid4()}",
            start_time=session_dict["start_time"],
            end_time=session_dict["last_activity_time"],
            duration=duration,
            project_id=project_id,
            activity_type=activity_type,
            focus_score=round(focus_score, 2),
            app_breakdown=session_dict["app_times"],
            metadata_={
                "context_switches": session_dict["context_switches"],
                "total_activities": len(session_dict["activities"]),
                "unique_apps": len(set(session_dict["activities"])),
            },
            raw_memory_references=session_dict["raw_memory_ids"],
            user_id=user_id,
            organization_id=organization_id,
        )

        # 保存到数据库
        with self.db_context() as db_session:
            db_session.add(work_session)
            db_session.commit()
            db_session.refresh(work_session)

        return work_session

    def _is_related_activity(self, app1: str, app2: str) -> bool:
        """
        判断两个应用是否属于相关活动

        例如：
        - VSCode + Terminal = 相关（coding）
        - Chrome + Notion = 相关（research/writing）
        - VSCode + Slack = 不太相关（可能是被打断）

        Args:
            app1: 第一个应用名称
            app2: 第二个应用名称

        Returns:
            是否相关
        """
        # 定义应用分组
        coding_apps = {"vscode", "code", "pycharm", "intellij", "vim", "terminal", "iterm"}
        browser_apps = {"chrome", "safari", "firefox", "edge"}
        communication_apps = {"slack", "teams", "zoom", "discord", "wechat", "telegram"}
        design_apps = {"figma", "sketch", "photoshop", "illustrator"}
        office_apps = {"word", "excel", "powerpoint", "notion", "obsidian", "pages"}

        app1_lower = app1.lower()
        app2_lower = app2.lower()

        # 检查是否在同一组
        for app_group in [
            coding_apps,
            browser_apps,
            communication_apps,
            design_apps,
            office_apps,
        ]:
            if any(app in app1_lower for app in app_group) and any(
                app in app2_lower for app in app_group
            ):
                return True

        # Coding + Browser 也认为相关（查文档）
        if (
            any(app in app1_lower for app in coding_apps)
            and any(app in app2_lower for app in browser_apps)
        ) or (
            any(app in app2_lower for app in coding_apps)
            and any(app in app1_lower for app in browser_apps)
        ):
            return True

        return False

    def _infer_activity_type(self, app_times: Dict[str, float]) -> str:
        """
        根据 app 使用时间推断活动类型

        Args:
            app_times: {app_name: seconds} 字典

        Returns:
            活动类型字符串：coding, meeting, research, writing, design, other
        """
        if not app_times:
            return "other"

        # 找出使用时间最长的 app
        dominant_app = max(app_times.items(), key=lambda x: x[1])[0].lower()

        # 根据 app 推断类型
        if any(
            app in dominant_app
            for app in ["vscode", "code", "pycharm", "intellij", "vim", "terminal"]
        ):
            return "coding"
        elif any(app in dominant_app for app in ["zoom", "teams", "meet", "skype"]):
            return "meeting"
        elif any(
            app in dominant_app for app in ["chrome", "safari", "firefox", "edge"]
        ):
            return "research"
        elif any(
            app in dominant_app
            for app in ["notion", "obsidian", "word", "pages", "docs"]
        ):
            return "writing"
        elif any(
            app in dominant_app
            for app in ["figma", "sketch", "photoshop", "illustrator"]
        ):
            return "design"
        elif any(
            app in dominant_app for app in ["slack", "wechat", "telegram", "discord"]
        ):
            return "communication"
        else:
            return "other"

    # ========================================================================
    # Task 2.2: 时间分配分析
    # ========================================================================

    def _analyze_time_allocation(self, work_sessions: List[WorkSession]) -> Dict:
        """
        分析时间分配

        统计：
        1. 总工作时间
        2. 按活动类型的时间分配
        3. 按项目的时间分配
        4. 按小时的时间分布
        5. 工作会话统计

        Args:
            work_sessions: WorkSession 列表

        Returns:
            时间分配统计字典
        """
        if not work_sessions:
            return {
                "total_work_time": 0,
                "total_sessions": 0,
                "by_activity_type": {},
                "by_project": {},
                "by_hour": {},
                "longest_session": None,
                "average_session_duration": 0,
            }

        # 1. 总工作时间和会话数
        total_work_time = sum(ws.duration for ws in work_sessions)
        total_sessions = len(work_sessions)

        # 2. 按活动类型统计
        by_activity_type = {}
        for ws in work_sessions:
            activity_type = ws.activity_type
            if activity_type not in by_activity_type:
                by_activity_type[activity_type] = {
                    "total_time": 0,
                    "session_count": 0,
                    "percentage": 0.0,
                }

            by_activity_type[activity_type]["total_time"] += ws.duration
            by_activity_type[activity_type]["session_count"] += 1

        # 计算百分比
        for activity_type in by_activity_type:
            time_spent = by_activity_type[activity_type]["total_time"]
            by_activity_type[activity_type]["percentage"] = (
                (time_spent / total_work_time * 100) if total_work_time > 0 else 0.0
            )

        # 3. 按项目统计
        by_project = {}
        for ws in work_sessions:
            project_id = ws.project_id or "unassigned"
            if project_id not in by_project:
                by_project[project_id] = {
                    "total_time": 0,
                    "session_count": 0,
                    "percentage": 0.0,
                }

            by_project[project_id]["total_time"] += ws.duration
            by_project[project_id]["session_count"] += 1

        # 计算百分比
        for project_id in by_project:
            time_spent = by_project[project_id]["total_time"]
            by_project[project_id]["percentage"] = (
                (time_spent / total_work_time * 100) if total_work_time > 0 else 0.0
            )

        # 4. 按小时统计（用于时段分析）
        by_hour = {}
        for ws in work_sessions:
            start_hour = ws.start_time.hour
            if start_hour not in by_hour:
                by_hour[start_hour] = {
                    "total_time": 0,
                    "session_count": 0,
                }

            by_hour[start_hour]["total_time"] += ws.duration
            by_hour[start_hour]["session_count"] += 1

        # 5. 找出最长的工作会话
        longest_session = max(work_sessions, key=lambda ws: ws.duration)
        longest_session_info = {
            "duration": longest_session.duration,
            "activity_type": longest_session.activity_type,
            "start_time": longest_session.start_time.isoformat(),
            "focus_score": longest_session.focus_score,
        }

        # 6. 平均会话时长
        average_session_duration = total_work_time / total_sessions

        # 7. 按应用的时间统计（聚合所有 session 的 app_breakdown）
        by_app = {}
        for ws in work_sessions:
            for app_name, app_time in ws.app_breakdown.items():
                if app_name not in by_app:
                    by_app[app_name] = 0
                by_app[app_name] += app_time

        # 排序（按时间降序）
        by_app_sorted = dict(sorted(by_app.items(), key=lambda x: x[1], reverse=True))

        return {
            "total_work_time": total_work_time,
            "total_work_hours": round(total_work_time / 3600, 2),
            "total_sessions": total_sessions,
            "by_activity_type": by_activity_type,
            "by_project": by_project,
            "by_hour": by_hour,
            "by_app": by_app_sorted,
            "longest_session": longest_session_info,
            "average_session_duration": round(average_session_duration, 2),
            "average_session_minutes": round(average_session_duration / 60, 1),
        }

    # ========================================================================
    # Task 2.3: 效率分析
    # ========================================================================

    def _calculate_efficiency(self, work_sessions: List[WorkSession]) -> Dict:
        """
        计算效率指标

        核心指标：
        1. 平均专注度
        2. Deep Work vs Shallow Work 时间
        3. 高效时段识别
        4. 效率评级

        参考理论：
        - Cal Newport《Deep Work》：专注度 >= 7.0 = Deep Work
        - 番茄工作法：25 分钟专注单元

        Args:
            work_sessions: WorkSession 列表

        Returns:
            效率指标字典
        """
        if not work_sessions:
            return {
                "average_focus_score": 0.0,
                "deep_work_time": 0,
                "shallow_work_time": 0,
                "deep_work_percentage": 0.0,
                "efficiency_rating": "N/A",
                "productive_hours": [],
                "distracted_hours": [],
            }

        # 1. 计算平均专注度
        total_focus_score = sum(ws.focus_score * ws.duration for ws in work_sessions)
        total_time = sum(ws.duration for ws in work_sessions)
        average_focus_score = (
            total_focus_score / total_time if total_time > 0 else 0.0
        )

        # 2. Deep Work vs Shallow Work 分类
        # Deep Work: focus_score >= 7.0 且 duration >= 1500s (25分钟)
        # Shallow Work: focus_score < 7.0 或 duration < 1500s
        deep_work_threshold = 7.0
        min_deep_work_duration = 1500  # 25 分钟

        deep_work_time = 0
        shallow_work_time = 0
        deep_work_sessions = []
        shallow_work_sessions = []

        for ws in work_sessions:
            if ws.focus_score >= deep_work_threshold and ws.duration >= min_deep_work_duration:
                deep_work_time += ws.duration
                deep_work_sessions.append(ws)
            else:
                shallow_work_time += ws.duration
                shallow_work_sessions.append(ws)

        # 计算 Deep Work 百分比
        deep_work_percentage = (
            (deep_work_time / total_time * 100) if total_time > 0 else 0.0
        )

        # 3. 按小时分析效率（找出高效和低效时段）
        hourly_efficiency = {}
        for ws in work_sessions:
            hour = ws.start_time.hour
            if hour not in hourly_efficiency:
                hourly_efficiency[hour] = {
                    "total_time": 0,
                    "weighted_focus": 0,
                    "session_count": 0,
                }

            hourly_efficiency[hour]["total_time"] += ws.duration
            hourly_efficiency[hour]["weighted_focus"] += ws.focus_score * ws.duration
            hourly_efficiency[hour]["session_count"] += 1

        # 计算每小时的平均专注度
        for hour in hourly_efficiency:
            total_time = hourly_efficiency[hour]["total_time"]
            weighted_focus = hourly_efficiency[hour]["weighted_focus"]
            hourly_efficiency[hour]["average_focus"] = (
                weighted_focus / total_time if total_time > 0 else 0.0
            )

        # 识别高效时段（average_focus >= 7.0）
        productive_hours = [
            hour
            for hour, data in hourly_efficiency.items()
            if data["average_focus"] >= 7.0
        ]
        productive_hours.sort()

        # 识别低效时段（average_focus < 5.0）
        distracted_hours = [
            hour
            for hour, data in hourly_efficiency.items()
            if data["average_focus"] < 5.0
        ]
        distracted_hours.sort()

        # 4. 效率评级（基于 Deep Work 百分比和平均专注度）
        # S 级：Deep Work >= 60% 且 avg_focus >= 8.0
        # A 级：Deep Work >= 40% 且 avg_focus >= 7.0
        # B 级：Deep Work >= 20% 且 avg_focus >= 6.0
        # C 级：Deep Work >= 10% 且 avg_focus >= 5.0
        # D 级：其他
        if deep_work_percentage >= 60 and average_focus_score >= 8.0:
            efficiency_rating = "S"
        elif deep_work_percentage >= 40 and average_focus_score >= 7.0:
            efficiency_rating = "A"
        elif deep_work_percentage >= 20 and average_focus_score >= 6.0:
            efficiency_rating = "B"
        elif deep_work_percentage >= 10 and average_focus_score >= 5.0:
            efficiency_rating = "C"
        else:
            efficiency_rating = "D"

        # 5. 按活动类型的效率分析
        efficiency_by_activity = {}
        for ws in work_sessions:
            activity = ws.activity_type
            if activity not in efficiency_by_activity:
                efficiency_by_activity[activity] = {
                    "average_focus": 0.0,
                    "total_time": 0,
                    "weighted_focus": 0,
                }

            efficiency_by_activity[activity]["total_time"] += ws.duration
            efficiency_by_activity[activity]["weighted_focus"] += (
                ws.focus_score * ws.duration
            )

        # 计算每种活动的平均专注度
        for activity in efficiency_by_activity:
            total_time = efficiency_by_activity[activity]["total_time"]
            weighted_focus = efficiency_by_activity[activity]["weighted_focus"]
            efficiency_by_activity[activity]["average_focus"] = (
                weighted_focus / total_time if total_time > 0 else 0.0
            )

        return {
            "average_focus_score": round(average_focus_score, 2),
            "deep_work_time": deep_work_time,
            "deep_work_hours": round(deep_work_time / 3600, 2),
            "shallow_work_time": shallow_work_time,
            "shallow_work_hours": round(shallow_work_time / 3600, 2),
            "deep_work_percentage": round(deep_work_percentage, 1),
            "efficiency_rating": efficiency_rating,
            "productive_hours": productive_hours,
            "distracted_hours": distracted_hours,
            "hourly_efficiency": hourly_efficiency,
            "efficiency_by_activity": efficiency_by_activity,
            "deep_work_session_count": len(deep_work_sessions),
            "shallow_work_session_count": len(shallow_work_sessions),
        }

    def _discover_daily_patterns(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Pattern]:
        """TODO: Task 2.4 - 发现每日模式"""
        return []

    def _generate_insights(
        self,
        patterns: List[Pattern],
        efficiency_metrics: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Insight]:
        """TODO: Task 2.5 - 生成洞察"""
        return []

    def _generate_summary(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        efficiency_metrics: Dict,
        patterns: List[Pattern],
        insights: List[Insight],
    ) -> str:
        """TODO: Task 2.6 - 生成文字总结"""
        total_sessions = len(work_sessions)
        total_time = sum(ws.duration for ws in work_sessions)
        total_hours = total_time / 3600

        return f"今日共有 {total_sessions} 个工作会话，总计 {total_hours:.1f} 小时。"

    # ========================================================================
    # 辅助方法：序列化对象为字典
    # ========================================================================

    def _serialize_work_session(self, ws: WorkSession) -> Dict:
        """将 WorkSession 序列化为字典"""
        return {
            "id": ws.id,
            "start_time": ws.start_time.isoformat(),
            "end_time": ws.end_time.isoformat(),
            "duration": ws.duration,
            "activity_type": ws.activity_type,
            "focus_score": ws.focus_score,
            "app_breakdown": ws.app_breakdown,
            "project_id": ws.project_id,
        }

    def _serialize_pattern(self, pattern: Pattern) -> Dict:
        """将 Pattern 序列化为字典"""
        return {
            "id": pattern.id,
            "pattern_type": pattern.pattern_type,
            "title": pattern.title,
            "description": pattern.description,
            "confidence": pattern.confidence,
        }

    def _serialize_insight(self, insight: Insight) -> Dict:
        """将 Insight 序列化为字典"""
        return {
            "id": insight.id,
            "category": insight.category,
            "title": insight.title,
            "content": insight.content,
            "action_items": insight.action_items,
            "priority": insight.priority,
            "impact_score": insight.impact_score,
        }
