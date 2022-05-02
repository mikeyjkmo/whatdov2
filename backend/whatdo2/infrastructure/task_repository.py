from abc import ABCMeta
from typing import Dict, Tuple, Any
from uuid import UUID
import dataclasses as dc
from whatdo2.domain.task.typedefs import DependentTask

import motor.motor_asyncio

from whatdo2.domain.task.public import Task


class TaskRepository(metaclass=ABCMeta):
    async def save(self, task: Task) -> None:
        ...

    async def get(self, task_id: UUID) -> Task:
        ...

    async def delete(self, task_id: UUID) -> None:
        ...


class MongoTaskRepository(TaskRepository):
    def __init__(
        self,
        db: motor.motor_asyncio.AsyncIOMotorDatabase,
    ):
        self.db = db

    async def save(self, task: Task) -> None:
        raw_task = dc.asdict(task)
        raw_task["id"] = str(task.id)
        raw_task["depends_on"] = [
            {"id": str(t.id)} for t in task.depends_on
        ]
        await self.db.tasks.insert_one(raw_task)

    def _raw_task_to_task(
        self,
        raw_task: Dict[Any, Any],
        raw_dependencies: Tuple[Dict[Any, Any], ...],
    ) -> Task:
        raw_task["depends_on"] = tuple(
            DependentTask.from_raw(t) for t in raw_dependencies
        )
        del raw_task["_id"]
        return Task(**raw_task)

    async def get(self, task_id: UUID) -> Task:
        raw_task = await self.db.tasks.find_one({"id": str(task_id)})
        raw_dependencies = await self.db.tasks.find(
            {'id': {'$in': [t["id"] for t in raw_task["depends_on"]]}},
        ).to_list(length=None)
        return self._raw_task_to_task(raw_task, raw_dependencies)

    async def delete(self, task_id: UUID) -> None:
        await self.db.tasks.delete_one({"id": str(task_id)})
