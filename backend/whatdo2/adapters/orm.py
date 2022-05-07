import asyncio
from typing import Any

from sqlalchemy.ext.asyncio.engine import create_async_engine
from whatdo2.config import POSTGRES_URI
from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Float,
    Integer,
    String,
    Table,
)
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
from sqlalchemy.ext.declarative import declarative_base

Base = declarative_base()


AssociationTable = Table(
    "association",
    Base.metadata,
    Column("parent_id", ForeignKey("task.id")),
    Column("child_id", ForeignKey("task.id")),
)


class TaskDBModel(Base):
    __tablename__ = "task"
    id: UUID = Column(UUID, primary_key=True)
    name = Column(String(128))
    importance = Column(Integer())
    task_type = Column(String(32))
    density = Column(Float())
    effective_density = Column(Float())
    time = Column(Integer())
    activation_time = Column(DateTime())
    is_active = Column(Boolean())
    is_prerequisite_for: Any = relationship(
        "TaskDBModel",
        secondary=AssociationTable,
        primaryjoin=AssociationTable.c.parent_id == id,
        secondaryjoin=AssociationTable.c.child_id == id,
    )


async def _create_tables() -> None:
    engine = create_async_engine(POSTGRES_URI, echo=True)

    meta = Base.metadata
    async with engine.begin() as conn:
        await conn.run_sync(meta.drop_all)
        await conn.run_sync(meta.create_all)


def create_tables() -> None:
    asyncio.run(_create_tables())
