import datetime as dt
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column, DateTime, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from mirix.constants import MAX_EMBEDDING_DIM
from mirix.orm.custom_columns import CommonVector, EmbeddingConfigColumn
from mirix.orm.mixins import OrganizationMixin, UserMixin
from mirix.orm.sqlalchemy_base import SqlalchemyBase
from mirix.settings import settings

if TYPE_CHECKING:
    from mirix.orm.organization import Organization
    from mirix.orm.user import User


class Task(SqlalchemyBase, OrganizationMixin, UserMixin):
    """
    任务 - 项目下的具体任务

    A Task represents a specific work item or action item within a project.
    It tracks status, dependencies, and blocking relationships.

    Attributes:
        id: Unique ID for this task
        title: Task title
        description: Detailed task description
        status: Current status (todo, in_progress, blocked, completed, cancelled)
        priority: Priority level (1-10)
        project_id: Associated project ID (nullable for standalone tasks)
        estimated_hours: Estimated time to complete (in hours)
        actual_hours: Actual time spent (in hours)
        due_date: Task deadline (optional)
        completed_at: When the task was completed (optional)
        dependencies: List of task IDs that must be completed before this task
        blocking: List of task IDs that are blocked by this task
        metadata_: Additional metadata (assignee, tags, subtasks, etc.)
    """

    __tablename__ = "task"

    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        doc="Unique ID for this task",
    )

    # Basic info
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="任务标题 / Task title",
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="任务详细描述 / Detailed task description",
    )

    # Status and priority
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="todo",
        doc="任务状态 / Task status: todo, in_progress, blocked, completed, cancelled",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        doc="优先级 (1-10) / Priority level, 1=lowest, 10=highest",
    )

    # Project association
    project_id: Mapped[Optional[str]] = mapped_column(
        String,
        nullable=True,
        doc="关联的项目ID / Associated project ID (nullable for standalone tasks)",
    )

    # Time tracking
    estimated_hours: Mapped[Optional[float]] = mapped_column(
        Integer,
        nullable=True,
        doc="预计耗时（小时） / Estimated time to complete in hours",
    )

    actual_hours: Mapped[Optional[float]] = mapped_column(
        Integer,
        nullable=True,
        doc="实际耗时（小时） / Actual time spent in hours",
    )

    # Date tracking
    due_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="截止日期 / Task deadline",
    )

    completed_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="完成时间 / When the task was completed",
    )

    # Task relationships
    dependencies: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="依赖的任务ID列表 / List of task IDs that must be completed before this task",
    )

    blocking: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="阻塞的任务ID列表 / List of task IDs that are blocked by this task",
    )

    # Additional metadata
    metadata_: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
        doc="其他元数据 / Additional metadata (assignee, tags, subtasks, related_urls, etc.)",
    )

    # Last modification tracking
    last_modify: Mapped[dict] = mapped_column(
        JSON,
        nullable=False,
        default=lambda: {
            "timestamp": datetime.now(dt.timezone.utc).isoformat(),
            "operation": "created",
        },
        doc="Last modification info including timestamp and operation type",
    )

    # Created timestamp
    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=lambda: datetime.now(dt.timezone.utc),
        nullable=False,
        doc="Timestamp when this task was created",
    )

    embedding_config: Mapped[Optional[dict]] = mapped_column(
        EmbeddingConfigColumn, nullable=True, doc="Embedding configuration"
    )

    # Vector embedding field based on database type
    if settings.mirix_pg_uri_no_default:
        from pgvector.sqlalchemy import Vector

        description_embedding = mapped_column(
            Vector(MAX_EMBEDDING_DIM),
            nullable=True,
            doc="Vector embedding of task description for semantic search",
        )
    else:
        description_embedding = Column(
            CommonVector,
            nullable=True,
            doc="Vector embedding of task description for semantic search",
        )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        """
        Relationship to the Organization that owns this task.
        """
        return relationship(
            "Organization", back_populates="tasks", lazy="selectin"
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        """
        Relationship to the User that owns this task.
        """
        return relationship("User", lazy="selectin")
