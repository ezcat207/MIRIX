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


class Goal(SqlalchemyBase, OrganizationMixin, UserMixin):
    """
    目标 - 用户定义的长期目标

    A Goal represents a user-defined long-term objective that may span
    multiple projects and time periods. It tracks progress and related activities.

    Goal Types:
        - career: 职业发展目标
        - skill: 技能学习目标
        - business: 创业/商业目标
        - health: 健康目标
        - financial: 财务目标
        - personal: 个人成长目标

    Attributes:
        id: Unique ID for this goal
        goal_type: Type of goal (career, skill, business, health, financial, personal)
        title: Goal title
        description: Detailed goal description
        target_date: Target completion date (optional)
        progress: Current progress percentage (0-100)
        status: Current status (active, on_hold, achieved, abandoned)
        milestones: List of milestone definitions with progress tracking
        related_projects: List of project IDs contributing to this goal
        related_insights: List of insight IDs relevant to this goal
        metadata_: Additional metadata (success_criteria, resources, obstacles, etc.)
    """

    __tablename__ = "goal"

    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        doc="Unique ID for this goal",
    )

    # Goal classification
    goal_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="目标类型 / Goal type: career, skill, business, health, financial, personal",
    )

    # Basic info
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="目标标题 / Goal title",
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="目标详细描述 / Detailed goal description with context and motivation",
    )

    # Progress tracking
    target_date: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="目标日期 / Target completion date (optional for open-ended goals)",
    )

    progress: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        default=0.0,
        doc="当前进度百分比 (0-100) / Current progress percentage",
    )

    status: Mapped[str] = mapped_column(
        String,
        nullable=False,
        default="active",
        doc="状态 / Current status: active, on_hold, achieved, abandoned",
    )

    # Milestones
    milestones: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="里程碑列表 / List of milestone definitions with title, target_date, completed, etc.",
    )

    # Related entities
    related_projects: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="相关项目ID列表 / List of project IDs contributing to this goal",
    )

    related_insights: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="相关洞察ID列表 / List of insight IDs relevant to achieving this goal",
    )

    # Additional metadata
    metadata_: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
        doc="其他元数据 / Additional metadata (success_criteria, resources_needed, obstacles, reflections, etc.)",
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
        doc="Timestamp when this goal was created",
    )

    # Achievement timestamp
    achieved_at: Mapped[Optional[datetime]] = mapped_column(
        DateTime,
        nullable=True,
        doc="达成时间 / When this goal was achieved",
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
            doc="Vector embedding of goal description for semantic search",
        )
    else:
        description_embedding = Column(
            CommonVector,
            nullable=True,
            doc="Vector embedding of goal description for semantic search",
        )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        """
        Relationship to the Organization that owns this goal.
        """
        return relationship(
            "Organization", back_populates="goals", lazy="selectin"
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        """
        Relationship to the User that owns this goal.
        """
        return relationship("User", lazy="selectin")
