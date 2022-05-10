from datetime import datetime
from typing import List, cast
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import selectinload

from whatdo2.adapters.orm import Association, TaskDBModel
from whatdo2.adapters.task_repository import TaskRepository
from whatdo2.domain.task.core import Task


class SQLTaskRepository(TaskRepository):
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def _get_single_db_instance(
        self,
        task_id: UUID,
    ) -> TaskDBModel:
        result = await self._session.execute(
            select(TaskDBModel)
            .filter_by(id=str(task_id))
            .options(selectinload(TaskDBModel.is_prerequisite_for))
        )
        return cast(TaskDBModel, result.scalar_one())

    async def get(self, task_id: UUID) -> Task:
        result = await self._session.execute(
            select(TaskDBModel)
            .filter_by(id=str(task_id))
            .options(selectinload(TaskDBModel.is_prerequisite_for))
        )
        db_task = result.scalar_one()
        return Task.from_orm(db_task)

    async def save(self, task: Task) -> None:
        raw_task = task.to_raw()
        raw_task["id"] = str(raw_task["id"])
        raw_task["ultimately_blocks"] = (
            str(raw_task["ultimately_blocks"])
            if raw_task["ultimately_blocks"] is not None
            else None
        )
        is_prerequisite_for = raw_task.pop("is_prerequisite_for")

        task_db_model = TaskDBModel(**raw_task)
        await self._session.merge(task_db_model)

        for t in is_prerequisite_for:
            assoc = Association(
                parent_id=task_db_model.id,
                child_id=str(t["id"]),
            )
            await self._session.merge(assoc)

        await self._session.commit()

    async def list_inactive_with_past_activation_times(self) -> List[Task]:
        many_results = await self._session.execute(
            select(TaskDBModel)
            .filter(
                TaskDBModel.activation_time <= datetime.utcnow(),
            )
            .filter_by(is_active=False)
            .options(selectinload(TaskDBModel.is_prerequisite_for))
        )

        db_tasks = many_results.scalars().all()
        return [Task.from_orm(t) for t in db_tasks]

    async def list_prerequisites_for_task(self, task_id: UUID) -> List[Task]:
        many_results = await self._session.execute(
            select(TaskDBModel)
            .join(Association, onclause=(TaskDBModel.id == Association.parent_id))
            .filter_by(child_id=str(task_id))
            .options(selectinload(TaskDBModel.is_prerequisite_for))
        )

        db_tasks = many_results.scalars().all()
        return [Task.from_orm(t) for t in db_tasks]
