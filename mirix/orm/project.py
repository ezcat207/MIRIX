import datetime as dt
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column, DateTime, Float, Integer, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from mirix.constants import MAX_EMBEDDING_DIM
from mirix.orm.custom_columns import CommonVector, EmbeddingConfigColumn
from mirix.orm.mixins import OrganizationMixin, UserMixin
from mirix.orm.sqlalchemy_base import SqlalchemyBase
from mirix.settings import settings

if TYPE_CHECKING:
    from mirix.orm.organization import Organization
    from mirix.orm.user import User


class Project(SqlalchemyBase, OrganizationMixin, UserMixin):
    """
    项目 - 用户的工作项目或目标

    A Project represents a user's work project, side project, or major goal.
    It tracks overall progress, time invested, and related goals.

    Attributes:
        id: Unique ID for this project
        name: Project name
        description: Project description
        status: Current status (active, paused, completed, archived)
        priority: Priority level (1-10, higher is more important)
        progress: Overall progress percentage (0-100)
        total_time_spent: Total time spent in seconds
        start_date: When the project started
        target_end_date: Target completion date (optional)
        actual_end_date: Actual completion date (optional)
        related_goals: List of goal IDs associated with this project
        metadata_: Additional metadata (repo URL, tech stack, collaborators, etc.)
    """

    __tablename__ = "project"

    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        doc="Unique ID for this project",
    )

    # Basic info
    name: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="项目名称 / Project name",
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="项目描述 / Detailed project description",
    )

    # Status and priority
    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
        doc="项目状态 / Project status: active, paused, completed, archived",
    )

    priority: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=5,
        doc="优先级 (1-10) / Priority level, 1=lowest, 10=highest",
    )

    # Progress tracking
    progress: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="整体进度百分比 (0-100) / Overall progress percentage",
    )

    total_time_spent: Mapped[int] = mapped_column(
        Integer,
        nullable=False,
        default=0,
        doc="总投入时间（秒） / Total time spent on this project in seconds",
    )

    # Date tracking
    start_date: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        doc="项目开始日期 / When the project started",
    )

    target_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="目标完成日期 / Target completion date (optional)",
    )

    actual_end_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="实际完成日期 / Actual completion date (set when status becomes 'completed')",
    )

    # Goals association
    related_goals: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="关联的目标ID列表 / List of goal IDs associated with this project",
    )

    # Additional metadata
    metadata_: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
        doc="其他元数据 / Additional metadata (repo_url, tech_stack, collaborators, etc.)",
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
        doc="Timestamp when this project was created",
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
            doc="Vector embedding of project description for semantic search",
        )
    else:
        description_embedding = Column(
            CommonVector,
            nullable=True,
            doc="Vector embedding of project description for semantic search",
        )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        """
        Relationship to the Organization that owns this project.
        """
        return relationship(
            "Organization", back_populates="projects", lazy="selectin"
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        """
        Relationship to the User that owns this project.
        """
        return relationship("User", lazy="selectin")
