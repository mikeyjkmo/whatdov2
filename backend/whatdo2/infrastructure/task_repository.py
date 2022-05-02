from abc import ABCMeta
from uuid import UUID
import dataclasses as dc

import motor

from whatdo2.domain.task.public import Task


class TaskRepository(metaclass=ABCMeta):
    async def save(self, task: Task) -> None:
        ...

    async def get(self, task_id: UUID) -> Task:
        ...


class MongoTaskRepository(TaskRepository):
    def __init__(
        self,
        db: motor.motor_asyncio.AsyncIOMotorDatabase,
    ):
        self.db = db

    async def save(self, task: Task) -> None:
        raw_task = dc.asdict(task)
        raw_task["depends_on"] = [
            {"id": t.id} for t in task.depends_on
        ]
        await self.db.tasks.insert_one(raw_task)

    async def get(self, task_id: UUID) -> Task:
        raw_task = await self.db.tasks.find_one({"id": task_id})
        raw_dependencies = await (
            self.db.tasks.find(
                {'id': {'$in': [t["id"] for t in raw_task["depends_on"]]}},
            )
        )
        dependencies = [
            Task(**raw_task) for raw_task in raw_dependencies
        ]

        raw_task["depends_on"] = dependencies
        return Task(**raw_task)
