import uuid
from sqlalchemy import Column, String, Float, DateTime, JSON
from sqlalchemy.orm import Mapped, mapped_column
from .base import Base

class MechSession(Base):
    __tablename__ = "mech_sessions"

    id: Mapped[str] = mapped_column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    
    mech_id = Column(String, nullable=False)
    start_time = Column(DateTime, nullable=False)
    end_time = Column(DateTime, nullable=False)
    
    # Metrics
    capability_growth = Column(Float, default=0.0)
    wealth_generated = Column(Float, default=0.0)
    influence_gained = Column(Float, default=0.0)
    focus_score = Column(Float, default=0.0)
    
    # Qualitative
    reflection = Column(String, nullable=True)
    tasks_completed = Column(JSON, default=list) # List of task objects
    
    def __repr__(self):
        return f"<MechSession(id={self.id}, mech={self.mech_id}, tasks={len(self.tasks_completed)})>"
