from datetime import datetime
from typing import List
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from whatdo2.adapters.orm import TaskDBModel
from whatdo2.config import POSTGRES_URI
from whatdo2.domain.task.core import TaskType


class DependentTaskDTO(BaseModel):
    id: UUID

    class Config:
        orm_mode = True


class TaskDTO(BaseModel):
    id: UUID
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime
    is_active: bool
    density: float
    effective_density: float
    is_prerequisite_for: List[DependentTaskDTO]

    class Config:
        orm_mode = True


class TaskQueryService:
    def __init__(self) -> None:
        self._engine = create_async_engine(POSTGRES_URI, echo=False)

    async def list_tasks(self) -> List[TaskDTO]:
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            many_results = await session.execute(
                select(TaskDBModel)
                .order_by(TaskDBModel.effective_density.desc())
                .options(selectinload(TaskDBModel.is_prerequisite_for))
            )
            db_tasks = many_results.scalars().all()
            return [TaskDTO.from_orm(t) for t in db_tasks]
