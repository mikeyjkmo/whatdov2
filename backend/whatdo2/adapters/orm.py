from typing import Any

from sqlalchemy import Boolean, Column, DateTime, Float, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship

from whatdo2.config import POSTGRES_URI

Base = declarative_base()


class Association(Base):
    __tablename__ = "association"
    parent_id: str = Column(ForeignKey("task.id"), primary_key=True)
    child_id: str = Column(ForeignKey("task.id"), primary_key=True)


class TaskDBModel(Base):
    __tablename__ = "task"
    id: str = Column(UUID, primary_key=True)
    name = Column(String(128))
    importance = Column(Integer())
    task_type = Column(String(32))
    density = Column(Float())
    effective_density = Column(Float())
    time = Column(Integer())
    activation_time = Column(DateTime())
    is_active = Column(Boolean())
    ultimately_blocks: str = Column(ForeignKey("task.id"), nullable=True)
    is_prerequisite_for: Any = relationship(
        "TaskDBModel",
        secondary=Association.__table__,
        primaryjoin=(Association.__table__.c.parent_id == id),
        secondaryjoin=(Association.__table__.c.child_id == id),
    )


async def delete_and_create_tables() -> None:
    engine = create_async_engine(POSTGRES_URI, echo=True)

    meta = Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)
