"""
Notification Service - Phase 2 Week 3 Task 3.5
发送邮件和其他通知
"""

import logging
import smtplib
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)


class NotificationService:
    """
    通知服务

    职责：
    1. 发送邮件通知
    2. 格式化通知内容
    3. （未来）支持更多通知渠道（Webhook, Slack, etc.）
    """

    def __init__(
        self,
        smtp_server: Optional[str] = None,
        smtp_port: Optional[int] = None,
        smtp_username: Optional[str] = None,
        smtp_password: Optional[str] = None,
        from_email: Optional[str] = None,
    ):
        """
        初始化通知服务

        Args:
            smtp_server: SMTP 服务器地址
            smtp_port: SMTP 端口
            smtp_username: SMTP 用户名
            smtp_password: SMTP 密码
            from_email: 发件人邮箱
        """
        self.smtp_server = smtp_server or "smtp.gmail.com"
        self.smtp_port = smtp_port or 587
        self.smtp_username = smtp_username
        self.smtp_password = smtp_password
        self.from_email = from_email or smtp_username

    def send_morning_brief(
        self, to_email: str, brief_data: Dict[str, Any]
    ) -> bool:
        """
        发送晨间简报邮件

        Args:
            to_email: 收件人邮箱
            brief_data: 简报数据（来自 MorningBriefAgent）

        Returns:
            True if 发送成功, False otherwise
        """
        try:
            subject = f"🌅 晨间简报 - {brief_data.get('date', datetime.now().date())}"
            body = self._format_morning_brief(brief_data)

            return self._send_email(to_email, subject, body)

        except Exception as e:
            logger.error(f"Error sending morning brief: {e}")
            return False

    def send_daily_review(
        self, to_email: str, review_data: Dict[str, Any]
    ) -> bool:
        """
        发送每日复盘邮件

        Args:
            to_email: 收件人邮箱
            review_data: 复盘数据（来自 GrowthAnalysisAgent）

        Returns:
            True if 发送成功, False otherwise
        """
        try:
            subject = f"📊 每日复盘 - {review_data.get('date', datetime.now().date())}"
            body = self._format_daily_review(review_data)

            return self._send_email(to_email, subject, body)

        except Exception as e:
            logger.error(f"Error sending daily review: {e}")
            return False

    def _format_morning_brief(self, brief_data: Dict[str, Any]) -> str:
        """
        格式化晨间简报邮件内容

        Args:
            brief_data: 简报数据

        Returns:
            HTML 格式的邮件内容
        """
        greeting = brief_data.get("greeting", "早安！")
        yesterday_summary = brief_data.get("yesterday_summary", {})
        today_priorities = brief_data.get("today_priorities", [])
        reminders = brief_data.get("reminders", [])
        motivational_message = brief_data.get("motivational_message", "")

        # 构建 HTML 内容
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #2563eb;">🌅 {greeting}</h1>

            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">

            <h2 style="color: #1f2937;">📊 昨日回顾</h2>
            <p>{yesterday_summary.get('brief', '暂无数据')}</p>

            <h2 style="color: #1f2937;">🎯 今日优先级</h2>
            <ol style="line-height: 1.8;">
"""

        # 添加优先级任务（最多 5 个）
        for task in today_priorities[:5]:
            html += f"""
                <li>
                    <strong>{task.get('task_title', 'Untitled')}</strong>
                    <br>
                    <span style="color: #6b7280; font-size: 14px;">
                        项目: {task.get('project_name', 'N/A')} |
                        优先级: {task.get('priority_score', 0)}/100
                    </span>
                </li>
"""

        html += """
            </ol>

            <h2 style="color: #1f2937;">🔔 提醒事项</h2>
            <ul style="line-height: 1.8;">
"""

        # 添加提醒
        if reminders:
            for reminder in reminders[:5]:
                html += f"""
                <li>
                    <strong>{reminder.get('title', '')}</strong>:
                    {reminder.get('content', '')}
                </li>
"""
        else:
            html += "<li>暂无提醒</li>"

        html += """
            </ul>

            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">

            <p style="color: #10b981; font-style: italic; font-size: 16px;">
                💡 {motivational_message}
            </p>

            <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                Generated by MIRIX at {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </p>
        </body>
        </html>
"""

        html = html.replace("{motivational_message}", motivational_message)
        return html

    def _format_daily_review(self, review_data: Dict[str, Any]) -> str:
        """
        格式化每日复盘邮件内容

        Args:
            review_data: 复盘数据

        Returns:
            HTML 格式的邮件内容
        """
        time_allocation = review_data.get("time_allocation", {})
        efficiency = review_data.get("efficiency", {})
        summary = review_data.get("summary", "暂无总结")
        insights = review_data.get("insights", [])

        # 构建 HTML 内容
        html = f"""
        <html>
        <body style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto; padding: 20px;">
            <h1 style="color: #7c3aed;">📊 每日复盘</h1>

            <hr style="border: 1px solid #e5e7eb; margin: 20px 0;">

            <h2 style="color: #1f2937;">⏱️ 时间分配</h2>
            <ul style="line-height: 1.8;">
                <li>总工作时长: {time_allocation.get('total_work_hours', 0):.1f} 小时</li>
                <li>工作会话数: {time_allocation.get('total_sessions', 0)} 个</li>
                <li>平均会话时长: {time_allocation.get('average_session_minutes', 0):.0f} 分钟</li>
            </ul>

            <h2 style="color: #1f2937;">📈 效率评估</h2>
            <ul style="line-height: 1.8;">
                <li>效率评级: <strong>{efficiency.get('efficiency_rating', 'N/A')}</strong></li>
                <li>平均专注度: {efficiency.get('average_focus_score', 0):.1f}/10</li>
                <li>深度工作时间: {efficiency.get('deep_work_hours', 0):.1f} 小时
                    ({efficiency.get('deep_work_percentage', 0):.1f}%)</li>
            </ul>

            <h2 style="color: #1f2937;">✨ AI 总结</h2>
            <div style="background-color: #f3f4f6; padding: 15px; border-radius: 8px; line-height: 1.6;">
                {summary.replace(chr(10), '<br>')}
            </div>

            <h2 style="color: #1f2937;">💡 洞察与建议</h2>
            <ul style="line-height: 1.8;">
"""

        # 添加洞察（最多 3 个）
        if insights:
            for insight in insights[:3]:
                html += f"""
                <li>
                    <strong>{insight.get('title', '')}</strong>
                    <br>
                    <span style="color: #6b7280; font-size: 14px;">
                        {insight.get('content', '')}
                    </span>
                </li>
"""
        else:
            html += "<li>暂无洞察</li>"

        html += f"""
            </ul>

            <p style="color: #6b7280; font-size: 12px; margin-top: 30px;">
                Generated by MIRIX at {datetime.now().strftime("%Y-%m-%d %H:%M")}
            </p>
        </body>
        </html>
"""

        return html

    def _send_email(
        self, to_email: str, subject: str, body_html: str
    ) -> bool:
        """
        发送邮件（HTML 格式）

        Args:
            to_email: 收件人邮箱
            subject: 邮件主题
            body_html: 邮件内容（HTML）

        Returns:
            True if 发送成功, False otherwise
        """
        # 如果没有配置 SMTP，记录日志但不报错
        if not self.smtp_username or not self.smtp_password:
            logger.warning("SMTP credentials not configured. Email sending skipped.")
            logger.info(f"Would send email to {to_email}: {subject}")
            return True  # 返回 True 以免阻塞定时任务

        try:
            # 创建邮件
            msg = MIMEMultipart("alternative")
            msg["From"] = self.from_email
            msg["To"] = to_email
            msg["Subject"] = subject

            # 添加 HTML 内容
            html_part = MIMEText(body_html, "html")
            msg.attach(html_part)

            # 连接 SMTP 服务器并发送
            with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_username, self.smtp_password)
                server.send_message(msg)

            logger.info(f"Email sent successfully to {to_email}: {subject}")
            return True

        except Exception as e:
            logger.error(f"Failed to send email to {to_email}: {e}")
            return False
