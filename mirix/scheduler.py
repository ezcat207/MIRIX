"""
Scheduler - Phase 2 Week 3 Task 3.5
定时任务调度（晨间简报 + 晚间复盘）
"""

import logging
from datetime import datetime
from typing import Optional

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

logger = logging.getLogger(__name__)


class MirixScheduler:
    """
    MIRIX 定时任务调度器

    职责：
    1. 每天 08:00 发送晨间简报
    2. 每天 21:00 发送晚间复盘
    3. 管理定时任务生命周期
    """

    def __init__(
        self,
        db_context,
        notification_service,
        user_email: Optional[str] = None,
        user_id: Optional[str] = None,
        organization_id: Optional[str] = None,
    ):
        """
        初始化调度器

        Args:
            db_context: 数据库上下文
            notification_service: 通知服务
            user_email: 用户邮箱（用于发送通知）
            user_id: 用户 ID
            organization_id: 组织 ID
        """
        self.db_context = db_context
        self.notification_service = notification_service
        self.user_email = user_email
        self.user_id = user_id
        self.organization_id = organization_id

        # 创建后台调度器
        self.scheduler = BackgroundScheduler()

    def start(self):
        """启动调度器"""
        if self.scheduler.running:
            logger.warning("Scheduler is already running")
            return

        # 添加定时任务
        self._add_morning_brief_job()
        self._add_evening_review_job()

        # 启动
        self.scheduler.start()
        logger.info("MIRIX Scheduler started successfully")

    def stop(self):
        """停止调度器"""
        if not self.scheduler.running:
            logger.warning("Scheduler is not running")
            return

        self.scheduler.shutdown(wait=False)
        logger.info("MIRIX Scheduler stopped")

    def _add_morning_brief_job(self):
        """
        添加晨间简报任务

        触发时间: 每天 08:00
        """
        trigger = CronTrigger(hour=8, minute=0)
        self.scheduler.add_job(
            func=self._send_morning_brief,
            trigger=trigger,
            id="morning_brief",
            name="Morning Brief (08:00)",
            replace_existing=True,
        )
        logger.info("Added job: Morning Brief (08:00)")

    def _add_evening_review_job(self):
        """
        添加晚间复盘任务

        触发时间: 每天 21:00
        """
        trigger = CronTrigger(hour=21, minute=0)
        self.scheduler.add_job(
            func=self._send_evening_review,
            trigger=trigger,
            id="evening_review",
            name="Evening Review (21:00)",
            replace_existing=True,
        )
        logger.info("Added job: Evening Review (21:00)")

    def _send_morning_brief(self):
        """
        发送晨间简报（任务执行函数）
        """
        try:
            if not self.user_email:
                logger.warning("User email not configured. Skipping morning brief.")
                return

            if not self.user_id or not self.organization_id:
                logger.warning("User ID or Organization ID not configured. Skipping morning brief.")
                return

            logger.info(f"Generating morning brief for user {self.user_id}...")

            # 生成简报
            from mirix.agents.morning_brief_agent import MorningBriefAgent

            morning_agent = MorningBriefAgent(self.db_context)
            brief_data = morning_agent.generate_brief(
                datetime.now(),
                self.user_id,
                self.organization_id
            )

            # 发送邮件
            success = self.notification_service.send_morning_brief(
                self.user_email,
                brief_data
            )

            if success:
                logger.info(f"Morning brief sent successfully to {self.user_email}")
            else:
                logger.error(f"Failed to send morning brief to {self.user_email}")

        except Exception as e:
            logger.error(f"Error in morning brief job: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def _send_evening_review(self):
        """
        发送晚间复盘（任务执行函数）
        """
        try:
            if not self.user_email:
                logger.warning("User email not configured. Skipping evening review.")
                return

            if not self.user_id or not self.organization_id:
                logger.warning("User ID or Organization ID not configured. Skipping evening review.")
                return

            logger.info(f"Generating daily review for user {self.user_id}...")

            # 生成复盘
            from mirix.agents.growth_analysis_agent import GrowthAnalysisAgent

            growth_agent = GrowthAnalysisAgent(self.db_context)
            review_data = growth_agent.daily_review(
                datetime.now(),
                self.user_id,
                self.organization_id
            )

            # 发送邮件
            success = self.notification_service.send_daily_review(
                self.user_email,
                review_data
            )

            if success:
                logger.info(f"Evening review sent successfully to {self.user_email}")
            else:
                logger.error(f"Failed to send evening review to {self.user_email}")

        except Exception as e:
            logger.error(f"Error in evening review job: {e}")
            import traceback
            logger.error(traceback.format_exc())

    def trigger_morning_brief_now(self):
        """
        立即触发晨间简报（用于测试）
        """
        logger.info("Manually triggering morning brief...")
        self._send_morning_brief()

    def trigger_evening_review_now(self):
        """
        立即触发晚间复盘（用于测试）
        """
        logger.info("Manually triggering evening review...")
        self._send_evening_review()

    def get_jobs(self):
        """
        获取所有定时任务列表

        Returns:
            定时任务列表
        """
        jobs = []
        for job in self.scheduler.get_jobs():
            jobs.append({
                "id": job.id,
                "name": job.name,
                "next_run_time": job.next_run_time.isoformat() if job.next_run_time else None,
                "trigger": str(job.trigger),
            })
        return jobs
