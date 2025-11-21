import datetime as dt
from datetime import datetime
from typing import TYPE_CHECKING, Optional

from sqlalchemy import JSON, Column, DateTime, Float, String
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from mirix.constants import MAX_EMBEDDING_DIM
from mirix.orm.custom_columns import CommonVector, EmbeddingConfigColumn
from mirix.orm.mixins import OrganizationMixin, UserMixin
from mirix.orm.sqlalchemy_base import SqlalchemyBase
from mirix.settings import settings

if TYPE_CHECKING:
    from mirix.orm.organization import Organization
    from mirix.orm.user import User


class Pattern(SqlalchemyBase, OrganizationMixin, UserMixin):
    """
    模式 - AI发现的用户行为模式

    A Pattern represents a behavioral pattern discovered by AI analysis
    of the user's work habits, productivity trends, and recurring situations.

    Pattern Types:
        - temporal: Time-based patterns (e.g., "最高效时段: 9-11am")
        - causal: Cause-effect patterns (e.g., "会议多 → 编码时间少")
        - anomaly: Unusual deviations (e.g., "本周加班3天")
        - trend: Long-term trends (e.g., "专注时长持续下降")

    Attributes:
        id: Unique ID for this pattern
        pattern_type: Type of pattern (temporal, causal, anomaly, trend)
        title: Pattern title/summary
        description: Detailed pattern description
        confidence: AI confidence score (0-1)
        frequency: How often this pattern occurs (e.g., "daily", "weekly", "monthly")
        evidence: JSON array of supporting evidence (work_session IDs, statistics)
        first_detected: When this pattern was first detected
        last_confirmed: When this pattern was last confirmed by new data
        metadata_: Additional metadata (affected_projects, time_range, etc.)
    """

    __tablename__ = "pattern"

    # Primary key
    id: Mapped[str] = mapped_column(
        String,
        primary_key=True,
        doc="Unique ID for this pattern",
    )

    # Pattern classification
    pattern_type: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="模式类型 / Pattern type: temporal, causal, anomaly, trend",
    )

    # Basic info
    title: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="模式标题 / Pattern title/summary",
    )

    description: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="模式详细描述 / Detailed pattern description with context and implications",
    )

    # AI metrics
    confidence: Mapped[float] = mapped_column(
        Float,
        nullable=False,
        doc="置信度 (0-1) / AI confidence score for this pattern",
    )

    frequency: Mapped[str] = mapped_column(
        String,
        nullable=False,
        doc="频率 / How often this pattern occurs: daily, weekly, monthly, occasional",
    )

    # Evidence
    evidence: Mapped[list] = mapped_column(
        JSON,
        default=list,
        nullable=False,
        doc="支持证据 / Array of supporting evidence (work_session IDs, statistics, examples)",
    )

    # Time tracking
    first_detected: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        doc="首次发现时间 / When this pattern was first detected",
    )

    last_confirmed: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
        doc="最后确认时间 / When this pattern was last confirmed by new data",
    )

    # Additional metadata
    metadata_: Mapped[dict] = mapped_column(
        JSON,
        default=dict,
        nullable=True,
        doc="其他元数据 / Additional metadata (affected_projects, time_range, impact_score, etc.)",
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
        doc="Timestamp when this pattern was created",
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
            doc="Vector embedding of pattern description for semantic search",
        )
    else:
        description_embedding = Column(
            CommonVector,
            nullable=True,
            doc="Vector embedding of pattern description for semantic search",
        )

    @declared_attr
    def organization(cls) -> Mapped["Organization"]:
        """
        Relationship to the Organization that owns this pattern.
        """
        return relationship(
            "Organization", back_populates="patterns", lazy="selectin"
        )

    @declared_attr
    def user(cls) -> Mapped["User"]:
        """
        Relationship to the User that owns this pattern.
        """
        return relationship("User", lazy="selectin")
