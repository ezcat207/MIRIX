"""
测试 GrowthAnalysisAgent 功能
"""

import pytest
from datetime import datetime, timedelta
from mirix.agents.growth_analysis_agent import GrowthAnalysisAgent
from mirix.services.raw_memory_manager import RawMemoryManager
from mirix.orm.raw_memory import RawMemoryItem


class TestGrowthAnalysisAgent:
    """测试 GrowthAnalysisAgent 的各项功能"""

    @pytest.fixture
    def agent(self, db_context):
        """创建 agent 实例"""
        return GrowthAnalysisAgent(db_context)

    @pytest.fixture
    def sample_raw_memories(self, test_pydantic_user, test_organization):
        """创建示例 raw_memory 数据（模拟一天的工作）"""
        raw_manager = RawMemoryManager()
        base_time = datetime(2025, 1, 21, 9, 0, 0)  # 早上 9 点开始

        memories = []

        # Scenario 1: 早上 9:00-10:30 - 连续编码（VSCode + Terminal）
        for i in range(18):  # 每 5 分钟一次，共 90 分钟
            app = "VSCode" if i % 2 == 0 else "Terminal"
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/screenshot_{i}.png",
                source_app=app,
                captured_at=base_time + timedelta(minutes=i * 5),
                ocr_text=f"Coding work {i}",
                organization_id=test_organization.id,
            )
            memories.append(memory)

        # 10 分钟休息（间隔）
        base_time = datetime(2025, 1, 21, 10, 40, 0)

        # Scenario 2: 10:40-11:20 - 浏览器研究（Chrome）
        for i in range(8):  # 每 5 分钟一次，共 40 分钟
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/screenshot_chrome_{i}.png",
                source_app="Chrome",
                captured_at=base_time + timedelta(minutes=i * 5),
                ocr_text=f"Research on Chrome {i}",
                source_url=f"https://example.com/page{i}",
                organization_id=test_organization.id,
            )
            memories.append(memory)

        # Scenario 3: 13:00-14:00 - 会议（Zoom）
        base_time = datetime(2025, 1, 21, 13, 0, 0)
        for i in range(12):  # 每 5 分钟一次，共 60 分钟
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/screenshot_zoom_{i}.png",
                source_app="Zoom",
                captured_at=base_time + timedelta(minutes=i * 5),
                ocr_text=f"Meeting {i}",
                organization_id=test_organization.id,
            )
            memories.append(memory)

        # Scenario 4: 14:30-17:00 - 编码时频繁切换（低专注度）
        base_time = datetime(2025, 1, 21, 14, 30, 0)
        apps_cycle = ["VSCode", "Slack", "Chrome", "VSCode", "Slack", "VSCode"]
        for i in range(30):  # 每 5 分钟一次，共 150 分钟
            app = apps_cycle[i % len(apps_cycle)]
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/screenshot_afternoon_{i}.png",
                source_app=app,
                captured_at=base_time + timedelta(minutes=i * 5),
                ocr_text=f"Afternoon work {i}",
                organization_id=test_organization.id,
            )
            memories.append(memory)

        return memories

    def test_generate_work_sessions(self, agent, sample_raw_memories, test_user, test_organization):
        """测试 WorkSession 生成"""
        work_sessions = agent._generate_work_sessions(
            sample_raw_memories, test_user.id, test_organization.id
        )

        # 应该生成 4 个主要 session（早上编码 + 浏览器研究 + 会议 + 下午工作）
        assert len(work_sessions) >= 3, f"Expected at least 3 sessions, got {len(work_sessions)}"

        # 检查第一个 session（早上编码）
        first_session = work_sessions[0]
        assert first_session.activity_type == "coding"
        assert first_session.duration > 0
        assert first_session.focus_score > 5.0  # 应该是高专注度
        assert "VSCode" in first_session.app_breakdown or "Terminal" in first_session.app_breakdown

        print(f"\n✅ 生成了 {len(work_sessions)} 个工作会话")
        for i, ws in enumerate(work_sessions):
            print(f"  Session {i+1}: {ws.activity_type}, "
                  f"duration={ws.duration}s ({ws.duration/60:.1f}min), "
                  f"focus_score={ws.focus_score:.1f}")

    def test_daily_review(self, agent, sample_raw_memories, test_user, test_organization):
        """测试每日复盘报告生成"""
        review_date = datetime(2025, 1, 21)

        report = agent.daily_review(
            date=review_date,
            user_id=test_user.id,
            organization_id=test_organization.id
        )

        # 验证报告结构
        assert "work_sessions" in report
        assert "time_allocation" in report
        assert "efficiency_metrics" in report
        assert "patterns" in report
        assert "insights" in report
        assert "summary" in report

        # 验证工作会话数据
        assert len(report["work_sessions"]) > 0

        # 验证时间分配
        total_work_time = report["time_allocation"]["total_work_time"]
        assert total_work_time > 0

        print(f"\n✅ 每日复盘报告生成成功")
        print(f"  工作会话数: {len(report['work_sessions'])}")
        print(f"  总工作时间: {total_work_time/3600:.1f} 小时")
        print(f"  总结: {report['summary']}")

    def test_focus_score_calculation(self, agent, test_pydantic_user, test_user, test_organization):
        """测试专注度评分计算"""
        raw_manager = RawMemoryManager()
        base_time = datetime(2025, 1, 21, 9, 0, 0)

        # Scenario A: 高专注度（无切换，持续 1 小时）
        high_focus_memories = []
        for i in range(12):
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/focus_high_{i}.png",
                source_app="VSCode",
                captured_at=base_time + timedelta(minutes=i * 5),
                ocr_text=f"Coding {i}",
                organization_id=test_organization.id,
            )
            high_focus_memories.append(memory)

        high_focus_sessions = agent._generate_work_sessions(
            high_focus_memories, test_user.id, test_organization.id
        )

        # Scenario B: 低专注度（频繁切换）
        low_focus_memories = []
        apps = ["VSCode", "Slack", "Chrome", "Slack", "VSCode", "Slack"]
        for i in range(12):
            memory = raw_manager.insert_raw_memory(
                actor=test_pydantic_user,
                screenshot_path=f"/tmp/focus_low_{i}.png",
                source_app=apps[i % len(apps)],
                captured_at=base_time + timedelta(hours=2, minutes=i * 5),
                ocr_text=f"Work {i}",
                organization_id=test_organization.id,
            )
            low_focus_memories.append(memory)

        low_focus_sessions = agent._generate_work_sessions(
            low_focus_memories, test_user.id, test_organization.id
        )

        # 验证：高专注度会话的 focus_score 应该明显高于低专注度会话
        high_score = high_focus_sessions[0].focus_score if high_focus_sessions else 0
        low_score = low_focus_sessions[0].focus_score if low_focus_sessions else 0

        print(f"\n✅ 专注度评分测试")
        print(f"  高专注度会话: {high_score:.1f}/10")
        print(f"  低专注度会话: {low_score:.1f}/10")

        assert high_score > low_score, f"High focus ({high_score}) should be > low focus ({low_score})"
        assert high_score >= 7.0, f"High focus should be >= 7.0, got {high_score}"

    def test_activity_type_inference(self, agent):
        """测试活动类型推断"""
        test_cases = [
            ({"VSCode": 3000, "Terminal": 600}, "coding"),
            ({"Chrome": 2400, "Safari": 1200}, "research"),
            ({"Zoom": 3600}, "meeting"),
            ({"Notion": 2400, "Pages": 1200}, "writing"),
            ({"Figma": 3600}, "design"),
            ({"Slack": 1800, "WeChat": 1800}, "communication"),
        ]

        print(f"\n✅ 活动类型推断测试")
        for app_times, expected_type in test_cases:
            inferred_type = agent._infer_activity_type(app_times)
            print(f"  {list(app_times.keys())} -> {inferred_type}")
            assert inferred_type == expected_type, \
                f"Expected {expected_type}, got {inferred_type} for {app_times}"

    def test_related_activity_detection(self, agent):
        """测试相关活动检测"""
        test_cases = [
            ("VSCode", "Terminal", True),  # Coding 相关
            ("VSCode", "Chrome", True),     # Coding + 查文档
            ("Chrome", "Safari", True),     # 都是浏览器
            ("Slack", "Zoom", True),        # 都是沟通工具
            ("VSCode", "Slack", False),     # Coding vs 沟通（可能被打断）
            ("Figma", "VSCode", False),     # Design vs Coding
        ]

        print(f"\n✅ 相关活动检测测试")
        for app1, app2, expected in test_cases:
            result = agent._is_related_activity(app1, app2)
            status = "✓" if result == expected else "✗"
            print(f"  {status} {app1} + {app2} -> {result} (expected {expected})")
            assert result == expected, f"Expected {expected} for {app1} + {app2}, got {result}"


# 运行示例
if __name__ == "__main__":
    """
    运行测试示例：
    pytest tests/test_growth_analysis_agent.py -v -s
    """
    print("请使用 pytest 运行此测试文件")
    print("命令: pytest tests/test_growth_analysis_agent.py -v -s")
