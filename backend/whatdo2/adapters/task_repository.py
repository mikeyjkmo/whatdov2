import dataclasses as dc
from abc import ABCMeta
from uuid import UUID

import motor.motor_asyncio

from whatdo2.domain.task.core import TaskModel


class TaskRepository(metaclass=ABCMeta):
    async def save(self, task: TaskModel) -> None:
        ...

    async def get(self, task_id: UUID) -> TaskModel:
        ...

    async def delete(self, task_id: UUID) -> None:
        ...


class MongoTaskRepository(TaskRepository):
    def __init__(
        self,
        db: motor.motor_asyncio.AsyncIOMotorDatabase,
    ):
        self.db = db

    async def save(self, task: TaskModel) -> None:
        raw_task = dc.asdict(task)
        raw_task["id"] = str(task.id)
        raw_task["is_prerequisite_for"] = [
            {"id": str(t.id)} for t in task.is_prerequisite_for
        ]
        await self.db.tasks.replace_one({"id": raw_task["id"]}, raw_task, upsert=True)

    async def get(self, task_id: UUID) -> TaskModel:
        raw_task = await self.db.tasks.find_one({"id": str(task_id)})
        raw_dependencies = await self.db.tasks.find(
            {"id": {"$in": [t["id"] for t in raw_task["is_prerequisite_for"]]}},
        ).to_list(length=None)
        return TaskModel.from_raw(raw_task, raw_dependencies)

    async def delete(self, task_id: UUID) -> None:
        await self.db.tasks.delete_one({"id": str(task_id)})
