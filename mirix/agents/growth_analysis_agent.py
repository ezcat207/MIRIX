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
        average_session_duration = total_work_time / total_sessions if total_sessions > 0 else 0

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

    # ========================================================================
    # Task 2.4: 基础模式发现
    # ========================================================================

    def _discover_daily_patterns(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Pattern]:
        """
        发现每日行为模式

        模式类型：
        1. Temporal Pattern (时间规律)
           - 最高效时段
           - 工作时间偏好

        2. Causal Pattern (因果关系)
           - 会议多 → 编码时间少
           - 频繁切换 → 专注度低

        3. Anomaly Pattern (异常检测)
           - 工作时长异常（过长/过短）
           - 深度工作不足
           - 时间分配失衡

        Args:
            work_sessions: WorkSession 列表
            time_allocation: 时间分配统计
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            发现的模式列表
        """
        patterns = []

        if not work_sessions:
            return patterns

        # 1. Temporal Pattern: 识别最高效时段
        temporal_patterns = self._discover_temporal_patterns(
            work_sessions, user_id, organization_id
        )
        patterns.extend(temporal_patterns)

        # 2. Causal Pattern: 识别因果关系
        causal_patterns = self._discover_causal_patterns(
            work_sessions, time_allocation, user_id, organization_id
        )
        patterns.extend(causal_patterns)

        # 3. Anomaly Pattern: 检测异常情况
        anomaly_patterns = self._discover_anomaly_patterns(
            work_sessions, time_allocation, user_id, organization_id
        )
        patterns.extend(anomaly_patterns)

        return patterns

    def _discover_temporal_patterns(
        self, work_sessions: List[WorkSession], user_id: str, organization_id: str
    ) -> List[Pattern]:
        """发现时间规律模式"""
        patterns = []

        # 按小时分析专注度
        hourly_focus = {}
        for ws in work_sessions:
            hour = ws.start_time.hour
            if hour not in hourly_focus:
                hourly_focus[hour] = {"scores": [], "durations": []}

            hourly_focus[hour]["scores"].append(ws.focus_score)
            hourly_focus[hour]["durations"].append(ws.duration)

        # 计算每小时平均专注度
        hourly_avg = {}
        for hour, data in hourly_focus.items():
            # 加权平均（按时长加权）
            total_duration = sum(data["durations"])
            weighted_focus = sum(
                score * duration
                for score, duration in zip(data["scores"], data["durations"])
            )
            hourly_avg[hour] = weighted_focus / total_duration if total_duration > 0 else 0

        # 找出最高效时段（专注度 >= 7.5）
        productive_hours = [
            hour for hour, avg_focus in hourly_avg.items() if avg_focus >= 7.5
        ]

        if productive_hours:
            productive_hours.sort()
            # 找连续时段
            hour_ranges = self._group_continuous_hours(productive_hours)

            for start_hour, end_hour in hour_ranges:
                avg_focus_in_range = sum(
                    hourly_avg[h] for h in range(start_hour, end_hour + 1)
                ) / (end_hour - start_hour + 1)

                pattern = Pattern(
                    id=f"pattern-{uuid.uuid4()}",
                    pattern_type="temporal",
                    title=f"最高效时段：{start_hour:02d}:00-{end_hour+1:02d}:00",
                    description=f"今天在 {start_hour:02d}:00-{end_hour+1:02d}:00 时段的平均专注度为 {avg_focus_in_range:.1f}/10，是你的高效工作时段。建议将重要任务安排在这个时间。",
                    confidence=0.8,
                    frequency="daily",
                    evidence=[
                        f"时段专注度: {avg_focus_in_range:.1f}/10",
                        f"工作会话数: {sum(1 for ws in work_sessions if start_hour <= ws.start_time.hour <= end_hour)}",
                    ],
                    first_detected=datetime.utcnow(),
                    last_confirmed=datetime.utcnow(),
                    user_id=user_id,
                    organization_id=organization_id,
                    metadata_={
                        "hour_range": [start_hour, end_hour],
                        "avg_focus": avg_focus_in_range,
                    },
                )

                # 保存到数据库
                with self.db_context() as db_session:
                    db_session.add(pattern)
                    db_session.commit()
                    db_session.refresh(pattern)

                patterns.append(pattern)

        return patterns

    def _discover_causal_patterns(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Pattern]:
        """发现因果关系模式"""
        patterns = []

        activity_stats = time_allocation.get("by_activity_type", {})

        # Pattern: 会议多 → 编码时间少
        meeting_time = activity_stats.get("meeting", {}).get("total_time", 0)
        coding_time = activity_stats.get("coding", {}).get("total_time", 0)
        total_time = time_allocation.get("total_work_time", 1)

        meeting_percentage = (meeting_time / total_time * 100) if total_time > 0 else 0
        coding_percentage = (coding_time / total_time * 100) if total_time > 0 else 0

        # 如果会议时间 > 30% 且编码时间 < 30%
        if meeting_percentage > 30 and coding_percentage < 30:
            pattern = Pattern(
                id=f"pattern-{uuid.uuid4()}",
                pattern_type="causal",
                title="会议时间占比过高，影响深度工作",
                description=f"今天会议占用了 {meeting_percentage:.0f}% 的时间（{meeting_time/3600:.1f} 小时），导致编码时间仅有 {coding_percentage:.0f}%。频繁的会议会打断专注状态，建议合并或批量安排会议时间。",
                confidence=0.75,
                frequency="occasional",
                evidence=[
                    f"会议时间: {meeting_time/3600:.1f}h ({meeting_percentage:.0f}%)",
                    f"编码时间: {coding_time/3600:.1f}h ({coding_percentage:.0f}%)",
                    "建议: 将会议集中在下午或特定时段",
                ],
                first_detected=datetime.utcnow(),
                last_confirmed=datetime.utcnow(),
                user_id=user_id,
                organization_id=organization_id,
                metadata_={
                    "meeting_percentage": meeting_percentage,
                    "coding_percentage": coding_percentage,
                },
            )

            with self.db_context() as db_session:
                db_session.add(pattern)
                db_session.commit()
                db_session.refresh(pattern)

            patterns.append(pattern)

        # Pattern: 频繁切换 → 专注度低
        high_switch_sessions = [
            ws
            for ws in work_sessions
            if ws.duration and ws.duration > 0 and
               ws.metadata_.get("context_switches", 0) / (ws.duration / 60) > 2
        ]

        if len(high_switch_sessions) >= 3:
            avg_focus_high_switch = (
                sum(ws.focus_score for ws in high_switch_sessions)
                / len(high_switch_sessions)
            )

            pattern = Pattern(
                id=f"pattern-{uuid.uuid4()}",
                pattern_type="causal",
                title="频繁切换应用导致专注度下降",
                description=f"发现 {len(high_switch_sessions)} 个高切换频率的工作会话（平均每分钟切换超过2次），这些会话的平均专注度仅为 {avg_focus_high_switch:.1f}/10。建议：使用番茄工作法，设置专注时段（如25分钟）期间关闭通知。",
                confidence=0.85,
                frequency="frequent",
                evidence=[
                    f"高切换会话数: {len(high_switch_sessions)}",
                    f"平均专注度: {avg_focus_high_switch:.1f}/10",
                    "主要干扰源: Slack, 浏览器通知",
                ],
                first_detected=datetime.utcnow(),
                last_confirmed=datetime.utcnow(),
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"high_switch_session_count": len(high_switch_sessions)},
            )

            with self.db_context() as db_session:
                db_session.add(pattern)
                db_session.commit()
                db_session.refresh(pattern)

            patterns.append(pattern)

        return patterns

    def _discover_anomaly_patterns(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Pattern]:
        """发现异常模式"""
        patterns = []

        total_hours = time_allocation.get("total_work_hours", 0)

        # Anomaly 1: 工作时间过长（> 10 小时）
        if total_hours > 10:
            pattern = Pattern(
                id=f"pattern-{uuid.uuid4()}",
                pattern_type="anomaly",
                title=f"工作时间异常：今日工作 {total_hours:.1f} 小时",
                description=f"今天的工作时间达到 {total_hours:.1f} 小时，远超正常工作时长。长时间工作会降低效率和创造力，建议注意休息和工作生活平衡。",
                confidence=0.9,
                frequency="occasional",
                evidence=[
                    f"工作时长: {total_hours:.1f}h",
                    "建议: 合理安排休息时间",
                    "注意: 持续加班会导致效率下降",
                ],
                first_detected=datetime.utcnow(),
                last_confirmed=datetime.utcnow(),
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"total_hours": total_hours, "threshold": 10},
            )

            with self.db_context() as db_session:
                db_session.add(pattern)
                db_session.commit()
                db_session.refresh(pattern)

            patterns.append(pattern)

        # Anomaly 2: 工作时间过短（< 4 小时且不是休息日）
        elif total_hours > 0 and total_hours < 4:
            pattern = Pattern(
                id=f"pattern-{uuid.uuid4()}",
                pattern_type="anomaly",
                title=f"工作时间较少：今日仅工作 {total_hours:.1f} 小时",
                description=f"今天的工作时间仅 {total_hours:.1f} 小时，可能受到其他事务影响。如非休息日，建议检查是否有时间管理上的问题。",
                confidence=0.7,
                frequency="occasional",
                evidence=[
                    f"工作时长: {total_hours:.1f}h",
                    "可能原因: 外出、身体不适、或其他安排",
                ],
                first_detected=datetime.utcnow(),
                last_confirmed=datetime.utcnow(),
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"total_hours": total_hours, "threshold": 4},
            )

            with self.db_context() as db_session:
                db_session.add(pattern)
                db_session.commit()
                db_session.refresh(pattern)

            patterns.append(pattern)

        return patterns

    def _group_continuous_hours(self, hours: List[int]) -> List[tuple]:
        """将连续的小时分组"""
        if not hours:
            return []

        ranges = []
        start = hours[0]
        prev = hours[0]

        for hour in hours[1:]:
            if hour == prev + 1:
                prev = hour
            else:
                ranges.append((start, prev))
                start = hour
                prev = hour

        ranges.append((start, prev))
        return ranges

    def _generate_insights(
        self,
        patterns: List[Pattern],
        efficiency_metrics: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Insight]:
        """
        Task 2.5: 生成可执行洞察

        基于发现的模式和效率指标，生成三类洞察：
        1. efficiency: 效率优化建议
        2. time_management: 时间管理建议
        3. health: 健康提醒

        Args:
            patterns: 发现的模式列表
            efficiency_metrics: 效率指标字典
            user_id: 用户 ID
            organization_id: 组织 ID

        Returns:
            List[Insight]: 生成的洞察列表，已保存到数据库
        """
        insights = []

        # 1. 基于效率指标生成效率优化建议
        insights.extend(
            self._generate_efficiency_insights(
                patterns, efficiency_metrics, user_id, organization_id
            )
        )

        # 2. 基于时间分配生成时间管理建议
        insights.extend(
            self._generate_time_management_insights(
                patterns, efficiency_metrics, user_id, organization_id
            )
        )

        # 3. 基于工作时长和模式生成健康建议
        insights.extend(
            self._generate_health_insights(
                patterns, efficiency_metrics, user_id, organization_id
            )
        )

        return insights

    def _generate_efficiency_insights(
        self,
        patterns: List[Pattern],
        efficiency_metrics: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Insight]:
        """生成效率优化类洞察"""
        insights = []

        # Insight 1: 基于高效时段建议
        temporal_patterns = [p for p in patterns if p.pattern_type == "temporal"]
        if temporal_patterns:
            # 找到最高效的时段
            for pattern in temporal_patterns:
                if "高效时段" in pattern.title:
                    # 提取时间范围（简单解析）
                    time_range = pattern.title.split("：")[-1] if "：" in pattern.title else ""

                    insight = Insight(
                        id=f"insight-{uuid.uuid4()}",
                        category="efficiency",
                        title="优化深度工作时间安排",
                        content=f"根据今日数据分析，你在 {time_range} 的平均专注度最高（{pattern.confidence*10:.1f}/10）。"
                        f"建议将核心编码任务、复杂问题解决等需要深度思考的工作安排在这个时段。",
                        action_items=[
                            f"将核心编码任务安排在 {time_range}",
                            "减少该时段的会议和沟通",
                            "设置免打扰模式以保护专注时间",
                        ],
                        priority=9,  # 高优先级
                        impact_score=8.5,
                        related_patterns=[pattern.id],
                        status="active",
                        user_id=user_id,
                        organization_id=organization_id,
                        metadata_={"pattern_confidence": pattern.confidence},
                    )

                    with self.db_context() as session:
                        session.add(insight)
                        session.commit()
                        session.refresh(insight)

                    insights.append(insight)
                    break  # 只生成一个高效时段建议

        # Insight 2: Deep Work 时间不足建议
        deep_work_hours = efficiency_metrics.get("deep_work_hours", 0)
        deep_work_percentage = efficiency_metrics.get("deep_work_percentage", 0)

        if deep_work_hours < 4:  # 少于 4 小时 Deep Work
            insight = Insight(
                id=f"insight-{uuid.uuid4()}",
                category="efficiency",
                title="增加深度工作时间",
                content=f"今日深度工作时间为 {deep_work_hours:.1f} 小时（{deep_work_percentage:.1f}%），"
                f"低于推荐的 4 小时标准。深度工作是高价值产出的关键，建议增加深度工作时间比例。",
                action_items=[
                    "设定每天至少 4 小时的深度工作目标",
                    "使用番茄工作法（25 分钟专注 + 5 分钟休息）",
                    "关闭通知和即时通讯工具",
                    "选择安静的工作环境",
                ],
                priority=8,
                impact_score=9.0,  # 高影响
                related_patterns=[],
                status="active",
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"current_deep_work_hours": deep_work_hours},
            )

            with self.db_context() as session:
                session.add(insight)
                session.commit()
                session.refresh(insight)

            insights.append(insight)

        # Insight 3: 效率评级建议
        rating = efficiency_metrics.get("efficiency_rating", "D")
        avg_focus = efficiency_metrics.get("average_focus_score", 0)

        if rating in ["C", "D"]:  # 效率较低
            insight = Insight(
                id=f"insight-{uuid.uuid4()}",
                category="efficiency",
                title=f"提升整体工作效率（当前评级：{rating}）",
                content=f"今日效率评级为 {rating} 级（平均专注度 {avg_focus:.1f}/10），有较大提升空间。"
                f"建议从减少干扰、优化工作环境、改进任务规划等方面入手。",
                action_items=[
                    "识别并消除主要干扰源（检查频繁切换的应用）",
                    "使用任务清单明确当日优先级",
                    "尝试时间块管理法（Time Blocking）",
                    "定期回顾和调整工作方法",
                ],
                priority=7,
                impact_score=7.5,
                related_patterns=[],
                status="active",
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"current_rating": rating, "avg_focus": avg_focus},
            )

            with self.db_context() as session:
                session.add(insight)
                session.commit()
                session.refresh(insight)

            insights.append(insight)

        return insights

    def _generate_time_management_insights(
        self,
        patterns: List[Pattern],
        efficiency_metrics: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Insight]:
        """生成时间管理类洞察"""
        insights = []

        # Insight 1: 基于因果模式的时间分配建议
        causal_patterns = [p for p in patterns if p.pattern_type == "causal"]

        for pattern in causal_patterns:
            if "会议占比过高" in pattern.title:
                insight = Insight(
                    id=f"insight-{uuid.uuid4()}",
                    category="time_management",
                    title="优化会议时间安排",
                    content=pattern.description,
                    action_items=[
                        "评估每个会议的必要性，减少不必要的会议",
                        "尝试将多个会议集中在特定时段（如下午）",
                        "设置每天的\"无会议时段\"用于深度工作",
                        "对于简单议题，考虑用异步沟通代替会议",
                    ],
                    priority=8,
                    impact_score=8.0,
                    related_patterns=[pattern.id],
                    status="active",
                    user_id=user_id,
                    organization_id=organization_id,
                    metadata_={"pattern_confidence": pattern.confidence},
                )

                with self.db_context() as session:
                    session.add(insight)
                    session.commit()
                    session.refresh(insight)

                insights.append(insight)

            elif "频繁切换" in pattern.title:
                insight = Insight(
                    id=f"insight-{uuid.uuid4()}",
                    category="time_management",
                    title="减少上下文切换",
                    content=pattern.description,
                    action_items=[
                        "关闭即时通讯工具的桌面通知",
                        "设定固定的邮件和消息查看时间（如每 2 小时一次）",
                        "使用\"勿扰模式\"保护专注时间",
                        "将类似任务批量处理，减少切换",
                    ],
                    priority=7,
                    impact_score=7.5,
                    related_patterns=[pattern.id],
                    status="active",
                    user_id=user_id,
                    organization_id=organization_id,
                    metadata_={"pattern_confidence": pattern.confidence},
                )

                with self.db_context() as session:
                    session.add(insight)
                    session.commit()
                    session.refresh(insight)

                insights.append(insight)

        return insights

    def _generate_health_insights(
        self,
        patterns: List[Pattern],
        efficiency_metrics: Dict,
        user_id: str,
        organization_id: str,
    ) -> List[Insight]:
        """生成健康类洞察"""
        insights = []

        # Insight 1: 基于工作时长异常的健康提醒
        anomaly_patterns = [p for p in patterns if p.pattern_type == "anomaly"]

        for pattern in anomaly_patterns:
            if "工作时间异常" in pattern.title and "过长" in pattern.description:
                insight = Insight(
                    id=f"insight-{uuid.uuid4()}",
                    category="health",
                    title="注意工作生活平衡",
                    content=pattern.description + " 长期过度工作可能影响健康和长期生产力。",
                    action_items=[
                        "设定合理的每日工作时长上限（如 8-9 小时）",
                        "确保每天有足够的休息和睡眠时间",
                        "评估任务优先级，避免不必要的加班",
                        "如果经常加班，考虑优化工作方法或寻求团队支持",
                    ],
                    priority=9,  # 健康相关，高优先级
                    impact_score=8.5,
                    related_patterns=[pattern.id],
                    status="active",
                    user_id=user_id,
                    organization_id=organization_id,
                    metadata_={"pattern_confidence": pattern.confidence},
                )

                with self.db_context() as session:
                    session.add(insight)
                    session.commit()
                    session.refresh(insight)

                insights.append(insight)

            elif "工作时间较少" in pattern.title:
                insight = Insight(
                    id=f"insight-{uuid.uuid4()}",
                    category="health",
                    title="工作时间提醒",
                    content=pattern.description + " 如果这是计划内的休息，那很好；如果不是，建议检查是否有影响工作的因素。",
                    action_items=[
                        "检查是否有健康或个人原因影响工作",
                        "如果是拖延，尝试使用番茄工作法开始小任务",
                        "评估任务清单，确保有明确的工作目标",
                        "考虑调整工作环境或时间安排",
                    ],
                    priority=5,
                    impact_score=5.0,
                    related_patterns=[pattern.id],
                    status="active",
                    user_id=user_id,
                    organization_id=organization_id,
                    metadata_={"pattern_confidence": pattern.confidence},
                )

                with self.db_context() as session:
                    session.add(insight)
                    session.commit()
                    session.refresh(insight)

                insights.append(insight)

        # Insight 2: 基于低效时段的休息建议
        distracted_hours = efficiency_metrics.get("distracted_hours", [])

        if len(distracted_hours) >= 2:  # 有 2 个或以上低效时段
            hours_str = ", ".join([f"{h}:00" for h in distracted_hours])

            insight = Insight(
                id=f"insight-{uuid.uuid4()}",
                category="health",
                title="适时休息，提升专注度",
                content=f"今日在 {hours_str} 等时段专注度较低（< 5.0/10），这可能是疲劳或需要休息的信号。"
                f"适时休息可以帮助恢复专注力。",
                action_items=[
                    "每工作 90 分钟休息 10-15 分钟",
                    "休息时离开屏幕，进行简单运动或冥想",
                    "保持充足的水分摄入",
                    "午休 15-20 分钟可以有效恢复下午的专注度",
                ],
                priority=6,
                impact_score=6.5,
                related_patterns=[],
                status="active",
                user_id=user_id,
                organization_id=organization_id,
                metadata_={"distracted_hours": distracted_hours},
            )

            with self.db_context() as session:
                session.add(insight)
                session.commit()
                session.refresh(insight)

            insights.append(insight)

        return insights

    def _generate_summary(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        efficiency_metrics: Dict,
        patterns: List[Pattern],
        insights: List[Insight],
    ) -> str:
        """
        Task 2.6: 生成每日复盘文字总结

        基于所有数据生成自然语言总结，包括：
        1. 基本统计（工作时间、会话数）
        2. 时间分配概览
        3. 效率评估
        4. 亮点（highlights）
        5. 待改进（areas for improvement）
        6. 明日建议（tomorrow's recommendations）

        注：目前使用结构化模板生成，未来可接入 LLM 生成更自然的文字

        Args:
            work_sessions: 工作会话列表
            time_allocation: 时间分配统计
            efficiency_metrics: 效率指标
            patterns: 发现的模式
            insights: 生成的洞察

        Returns:
            str: 每日复盘文字总结
        """
        # 1. 基本统计
        total_sessions = len(work_sessions)
        total_hours = time_allocation.get("total_work_hours", 0)

        summary_lines = []
        summary_lines.append(f"📊 今日工作概览")
        summary_lines.append(f"今天共工作 {total_hours:.1f} 小时，完成 {total_sessions} 个工作会话。")
        summary_lines.append("")

        # 2. 时间分配
        by_activity = time_allocation.get("by_activity_type", {})
        if by_activity:
            summary_lines.append(f"⏱️ 时间分配：")
            # 按时间排序活动类型
            sorted_activities = sorted(
                by_activity.items(),
                key=lambda x: x[1]["total_time"],
                reverse=True
            )

            activity_type_names = {
                "coding": "编码",
                "meeting": "会议",
                "research": "研究/浏览",
                "writing": "文档写作",
                "design": "设计",
                "communication": "沟通",
                "other": "其他",
            }

            for activity_type, stats in sorted_activities[:3]:  # 只显示前3个
                name = activity_type_names.get(activity_type, activity_type)
                hours = stats["total_time"] / 3600
                percentage = stats["percentage"]
                summary_lines.append(f"  • {name}占用 {percentage:.1f}% 时间（{hours:.1f} 小时）")
            summary_lines.append("")

        # 3. 效率评估
        rating = efficiency_metrics.get("efficiency_rating", "N/A")
        avg_focus = efficiency_metrics.get("average_focus_score", 0)
        deep_work_hours = efficiency_metrics.get("deep_work_hours", 0)
        deep_work_percentage = efficiency_metrics.get("deep_work_percentage", 0)

        summary_lines.append(f"📈 效率评估：")
        summary_lines.append(
            f"整体效率评级为 {rating} 级，"
            f"平均专注度 {avg_focus:.1f}/10，"
            f"Deep Work 时间 {deep_work_hours:.1f} 小时（{deep_work_percentage:.1f}%）。"
        )
        summary_lines.append("")

        # 4. 亮点（highlights）
        summary_lines.append(f"✨ 今日亮点：")
        highlights = self._extract_highlights(
            work_sessions, time_allocation, efficiency_metrics, patterns
        )
        if highlights:
            for highlight in highlights:
                summary_lines.append(f"  • {highlight}")
        else:
            summary_lines.append(f"  • 今日工作数据收集完成，继续保持记录")
        summary_lines.append("")

        # 5. 待改进（areas for improvement）
        summary_lines.append(f"🎯 待改进：")
        improvements = self._extract_improvements(
            efficiency_metrics, patterns, insights
        )
        if improvements:
            for improvement in improvements:
                summary_lines.append(f"  • {improvement}")
        else:
            summary_lines.append(f"  • 今日整体表现良好，继续保持")
        summary_lines.append("")

        # 6. 明日建议（tomorrow's recommendations）
        summary_lines.append(f"💡 明日建议：")
        recommendations = self._extract_recommendations(insights, patterns)
        if recommendations:
            for rec in recommendations[:3]:  # 最多显示3条
                summary_lines.append(f"  • {rec}")
        else:
            summary_lines.append(f"  • 继续保持今日的良好工作状态")

        return "\n".join(summary_lines)

    def _extract_highlights(
        self,
        work_sessions: List[WorkSession],
        time_allocation: Dict,
        efficiency_metrics: Dict,
        patterns: List[Pattern],
    ) -> List[str]:
        """提取今日亮点"""
        highlights = []

        # 亮点 1: 高效时段
        productive_hours = efficiency_metrics.get("productive_hours", [])
        if productive_hours:
            if len(productive_hours) >= 3:
                hours_str = f"{productive_hours[0]}:00-{productive_hours[-1]+1}:00"
                highlights.append(
                    f"在 {hours_str} 保持了高专注度（≥ 7.0/10），建议继续保持"
                )

        # 亮点 2: Deep Work 达标
        deep_work_hours = efficiency_metrics.get("deep_work_hours", 0)
        if deep_work_hours >= 4:
            highlights.append(
                f"深度工作时间达 {deep_work_hours:.1f} 小时，符合高效工作标准"
            )

        # 亮点 3: 高评级
        rating = efficiency_metrics.get("efficiency_rating", "D")
        if rating in ["S", "A"]:
            highlights.append(
                f"整体效率评级达到 {rating} 级，工作表现优秀"
            )

        # 亮点 4: 最长专注会话
        longest = time_allocation.get("longest_session")
        if longest and longest["focus_score"] >= 8.0:
            duration_min = longest["duration"] / 60
            highlights.append(
                f"最长专注会话达 {duration_min:.0f} 分钟（专注度 {longest['focus_score']:.1f}/10）"
            )

        # 亮点 5: 基于模式的亮点
        temporal_patterns = [p for p in patterns if p.pattern_type == "temporal"]
        if temporal_patterns and not productive_hours:
            # 如果没有高效时段但有时间模式，说明找到了规律
            highlights.append("成功识别了工作时间规律，有助于优化未来安排")

        return highlights

    def _extract_improvements(
        self,
        efficiency_metrics: Dict,
        patterns: List[Pattern],
        insights: List[Insight],
    ) -> List[str]:
        """提取待改进项"""
        improvements = []

        # 改进 1: Deep Work 不足
        deep_work_hours = efficiency_metrics.get("deep_work_hours", 0)
        if deep_work_hours < 4:
            improvements.append(
                f"深度工作时间仅 {deep_work_hours:.1f} 小时，建议增加到 4 小时以上"
            )

        # 改进 2: 低效时段
        distracted_hours = efficiency_metrics.get("distracted_hours", [])
        if len(distracted_hours) >= 2:
            hours_str = ", ".join([f"{h}:00" for h in distracted_hours[:2]])
            improvements.append(
                f"在 {hours_str} 等时段专注度较低（< 5.0/10），建议调整任务安排或增加休息"
            )

        # 改进 3: 效率评级低
        rating = efficiency_metrics.get("efficiency_rating", "D")
        if rating in ["C", "D"]:
            improvements.append(
                f"整体效率评级为 {rating} 级，有较大提升空间"
            )

        # 改进 4: 基于因果模式的改进
        causal_patterns = [p for p in patterns if p.pattern_type == "causal"]
        for pattern in causal_patterns:
            if "会议占比过高" in pattern.title:
                improvements.append("会议时间占比过高，影响了深度工作时间")
                break
            elif "频繁切换" in pattern.title:
                improvements.append("频繁切换应用导致专注度下降，建议减少干扰")
                break

        # 改进 5: 基于异常模式的改进
        anomaly_patterns = [p for p in patterns if p.pattern_type == "anomaly"]
        for pattern in anomaly_patterns:
            if "工作时间异常" in pattern.title and "过长" in pattern.description:
                improvements.append("工作时间过长，注意工作生活平衡")
                break

        return improvements

    def _extract_recommendations(
        self,
        insights: List[Insight],
        patterns: List[Pattern],
    ) -> List[str]:
        """提取明日建议"""
        recommendations = []

        # 按优先级排序洞察
        sorted_insights = sorted(insights, key=lambda x: x.priority, reverse=True)

        # 提取前3个最重要洞察的首条行动项
        for insight in sorted_insights[:3]:
            if insight.action_items:
                # 取第一条行动项作为建议
                recommendations.append(insight.action_items[0])

        # 如果洞察不足，基于模式补充建议
        if len(recommendations) < 2:
            temporal_patterns = [p for p in patterns if p.pattern_type == "temporal"]
            if temporal_patterns:
                for pattern in temporal_patterns:
                    if "高效时段" in pattern.title:
                        time_range = pattern.title.split("：")[-1] if "：" in pattern.title else "早上"
                        recommendations.append(
                            f"将重要任务安排在 {time_range} 高效时段"
                        )
                        break

        # 通用建议（如果还不够）
        if len(recommendations) < 1:
            recommendations.append("设定明确的每日工作目标和优先级")
            recommendations.append("保持专注，减少不必要的干扰")
            recommendations.append("适时休息，保持良好的工作节奏")

        return recommendations

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
