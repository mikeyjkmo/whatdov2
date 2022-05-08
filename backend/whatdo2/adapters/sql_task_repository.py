from datetime import datetime
from typing import Dict, Any, List, cast
from uuid import UUID

from sqlalchemy.orm import selectinload
from whatdo2.domain.task.core import Task

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.future import select

from whatdo2.adapters.task_repository import TaskRepository
from whatdo2.adapters.orm import Association, TaskDBModel
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

            task_db_model = TaskDBModel(**raw_task)
            await session.merge(task_db_model)

            for t in is_prerequisite_for:
                assoc = Association(
                    parent_id=task_db_model.id,
                    child_id=str(t["id"]),
                )
                await session.merge(assoc)

            await session.commit()

    async def list_inactive_with_past_activation_times(self) -> List[Task]:
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            many_results = await session.execute(
                select(TaskDBModel)
                .filter(
                    TaskDBModel.activation_time <= datetime.utcnow(),
                )
                .filter_by(is_active=False)
                .options(selectinload(TaskDBModel.is_prerequisite_for))
            )

            db_tasks = many_results.scalars().all()

            result = []

            for dbt in db_tasks:
                raw_task = db_model_to_dict(dbt)
                raw_dependencies = tuple(
                    db_model_to_dict(t) for t in dbt.is_prerequisite_for
                )
                result.append(Task.from_raw(raw_task, raw_dependencies))

            return result

    async def list_prerequisites_for_task(self, task_id: UUID) -> List[Task]:
        async with AsyncSession(self._engine, expire_on_commit=False) as session:
            many_results = await session.execute(
                select(TaskDBModel)
                .join(Association, onclause=(TaskDBModel.id == Association.parent_id))
                .filter_by(child_id=str(task_id))
                .options(selectinload(TaskDBModel.is_prerequisite_for))
            )

            db_tasks = many_results.scalars().all()

            result = []

            for dbt in db_tasks:
                raw_task = db_model_to_dict(dbt)
                raw_dependencies = tuple(
                    db_model_to_dict(t) for t in dbt.is_prerequisite_for
                )
                result.append(Task.from_raw(raw_task, raw_dependencies))

            return result
