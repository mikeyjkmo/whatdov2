from typing import Dict, Any, cast
from uuid import UUID

from sqlalchemy.orm import selectinload
from whatdo2.domain.task.core import Task

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select

from whatdo2.adapters.task_repository import TaskRepository
from whatdo2.adapters.orm import TaskDBModel
from whatdo2.config import POSTGRES_URI


def db_model_to_dict(db_model: Any) -> Dict[Any, Any]:
    dictret = dict(db_model.__dict__)
    dictret.pop("_sa_instance_state", None)
    return dictret


class SQLTaskRepository(TaskRepository):
    def __init__(self) -> None:
        self._engine = create_async_engine(POSTGRES_URI, echo=True)

    @staticmethod
    async def _get_single_db_instance(
        session: AsyncSession,
        task_id: UUID,
    ) -> TaskDBModel:
        result = await session.execute(
            select(TaskDBModel)
            .filter_by(id=str(task_id))
            .options(selectinload(TaskDBModel.is_prerequisite_for))
        )
        return cast(TaskDBModel, result.scalar_one())

    async def get(self, task_id: UUID) -> Task:
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            result = await session.execute(
                select(TaskDBModel)
                .filter_by(id=str(task_id))
                .options(selectinload(TaskDBModel.is_prerequisite_for))
            )
            db_task = result.scalar_one()
            raw_task = db_model_to_dict(db_task)
            raw_dependencies = tuple(
                db_model_to_dict(t) for t in db_task.is_prerequisite_for
            )
            return Task.from_raw(raw_task, raw_dependencies)

    async def save(self, task: Task) -> None:
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            raw_task = task.to_raw()
            raw_task["id"] = str(raw_task["id"])
            is_prerequisite_for = raw_task.pop("is_prerequisite_for")

            child_db_models = [
                await self._get_single_db_instance(session, t["id"])
                for t in is_prerequisite_for
            ]
            task_db_model = TaskDBModel(**raw_task)
            task_db_model.is_prerequisite_for = child_db_models

            session.add(task_db_model)
            await session.commit()
