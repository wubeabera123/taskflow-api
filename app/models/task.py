from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from app.core.database import Base


class Task(Base):
    __tablename__ = "tasks"

    id = Column(Integer, primary_key=True, index=True)

    title = Column(String, nullable=False)
    description = Column(String, nullable=True)   # ✅ ADD
    priority = Column(String, default="medium")   # ✅ ADD
    is_ai_generated = Column(Boolean, default=False)
    ai_prompt = Column(String, nullable=True)   # ✅ ADD THIS
    owner_id = Column(Integer, ForeignKey("users.id"))

    owner = relationship("User")