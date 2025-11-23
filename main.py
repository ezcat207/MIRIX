#!/usr/bin/env python3
"""
Mirix - AI Assistant Application
Entry point for the Mirix application.
"""

import argparse
import atexit
import logging
import os
import sys
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

logger = logging.getLogger(__name__)

# Global scheduler instance
scheduler_instance = None


def initialize_scheduler():
    """
    Initialize and start the scheduler for automated notifications

    Reads configuration from environment variables:
    - MIRIX_USER_EMAIL: User email for notifications
    - MIRIX_USER_ID: User ID
    - MIRIX_ORGANIZATION_ID: Organization ID
    - SMTP_SERVER: SMTP server (default: smtp.gmail.com)
    - SMTP_PORT: SMTP port (default: 587)
    - SMTP_USERNAME: SMTP username
    - SMTP_PASSWORD: SMTP password

    Returns:
        MirixScheduler instance if configured, None otherwise
    """
    try:
        from mirix.scheduler import MirixScheduler
        from mirix.services.notification_service import NotificationService
        from mirix.server.server import db_context

        # Read configuration from environment
        user_email = os.getenv("MIRIX_USER_EMAIL")
        user_id = os.getenv("MIRIX_USER_ID")
        organization_id = os.getenv("MIRIX_ORGANIZATION_ID")

        smtp_server = os.getenv("SMTP_SERVER", "smtp.gmail.com")
        smtp_port = int(os.getenv("SMTP_PORT", "587"))
        smtp_username = os.getenv("SMTP_USERNAME")
        smtp_password = os.getenv("SMTP_PASSWORD")
        from_email = os.getenv("SMTP_FROM_EMAIL", smtp_username)

        # Check if scheduler is configured
        if not user_email or not user_id or not organization_id:
            logger.info("Scheduler not configured (missing user email/ID/org). Skipping...")
            return None

        # Create notification service
        notification_service = NotificationService(
            smtp_server=smtp_server,
            smtp_port=smtp_port,
            smtp_username=smtp_username,
            smtp_password=smtp_password,
            from_email=from_email,
        )

        # Create and start scheduler
        scheduler = MirixScheduler(
            db_context=db_context,
            notification_service=notification_service,
            user_email=user_email,
            user_id=user_id,
            organization_id=organization_id,
        )

        scheduler.start()
        logger.info(f"Scheduler started successfully for user {user_email}")
        logger.info("Scheduled jobs:")
        for job in scheduler.get_jobs():
            logger.info(f"  - {job['name']} (next run: {job['next_run_time']})")

        return scheduler

    except Exception as e:
        logger.error(f"Failed to initialize scheduler: {e}")
        import traceback
        logger.error(traceback.format_exc())
        return None


def shutdown_scheduler():
    """Shutdown the scheduler gracefully"""
    global scheduler_instance
    if scheduler_instance:
        try:
            scheduler_instance.stop()
            logger.info("Scheduler stopped successfully")
        except Exception as e:
            logger.error(f"Error stopping scheduler: {e}")


def main():
    """Main entry point for Mirix application."""
    global scheduler_instance

    parser = argparse.ArgumentParser(description="Mirix AI Assistant Server")
    parser.add_argument("--host", default="0.0.0.0", help="Host to bind the server to")
    parser.add_argument(
        "--port", type=int, default=None, help="Port to bind the server to"
    )
    parser.add_argument(
        "--no-scheduler",
        action="store_true",
        help="Disable the automated notification scheduler"
    )

    args = parser.parse_args()

    # Determine port from command line, environment variable, or default
    port = args.port
    if port is None:
        port = int(os.environ.get("PORT", 47283))

    print(f"Starting Mirix server on {args.host}:{port}")

    # Initialize scheduler (unless disabled)
    if not args.no_scheduler:
        scheduler_instance = initialize_scheduler()

        # Register cleanup handler
        if scheduler_instance:
            atexit.register(shutdown_scheduler)

    import uvicorn

    from mirix.server import app

    # Increase concurrency to prevent health check timeouts
    # when backend is processing heavy requests (e.g., image uploads, OCR)
    # Note: workers parameter requires app to be passed as import string
    uvicorn.run(
        app, 
        host=args.host, 
        port=port,
        limit_concurrency=100,  # Allow more concurrent connections
        timeout_keep_alive=120,  # Increase keep-alive timeout
        limit_max_requests=1000  # Restart worker after 1000 requests to prevent memory leaks
    )


if __name__ == "__main__":
    main()
