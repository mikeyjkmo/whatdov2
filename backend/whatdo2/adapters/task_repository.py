from abc import ABCMeta
from datetime import datetime
from typing import List
from uuid import UUID

import motor.motor_asyncio

from whatdo2.domain.task.core import Task


class TaskRepository(metaclass=ABCMeta):
    async def save(self, task: Task) -> None:
        ...

    async def get(self, task_id: UUID) -> Task:
        ...

    async def delete(self, task_id: UUID) -> None:
        ...

    async def list_inactive_with_past_activation_times(self) -> List[Task]:
        ...


class MongoTaskRepository(TaskRepository):
    def __init__(
        self,
        db: motor.motor_asyncio.AsyncIOMotorDatabase,
        collection_name: str = "tasks",
    ):
        self.db = db
        self._collection_name = collection_name

    @property
    def _collection(self) -> motor.motor_asyncio.AsyncIOMotorCollection:
        return self.db[self._collection_name]

    async def save(self, task: Task) -> None:
        raw_task = task.to_raw()
        raw_task["id"] = str(task.id)
        raw_task["is_prerequisite_for"] = [
            {"id": str(t.id)} for t in task.is_prerequisite_for
        ]
        await self._collection.replace_one(
            {"id": raw_task["id"]},
            raw_task,
            upsert=True,
        )

    async def get(self, task_id: UUID) -> Task:
        raw_task = await self._collection.find_one({"id": str(task_id)})
        raw_dependencies = await self._collection.find(
            {"id": {"$in": [t["id"] for t in raw_task["is_prerequisite_for"]]}},
        ).to_list(length=None)
        return Task.from_raw(raw_task, raw_dependencies)

    async def delete(self, task_id: UUID) -> None:
        await self._collection.delete_one({"id": str(task_id)})

    async def list_inactive_with_past_activation_times(self) -> List[Task]:
        raw_results = await self._collection.find(
            {"activation_time": {"$lte": datetime.utcnow()}, "is_active": False},
        ).to_list(length=None)

        results = []

        for raw_task in raw_results:
            raw_dependencies = await self._collection.find(
                {"id": {"$in": [t["id"] for t in raw_task["is_prerequisite_for"]]}},
            ).to_list(length=None)
            results.append(Task.from_raw(raw_task, raw_dependencies))

        return results

    async def list_prerequisites_for_task(self, task_id: UUID) -> List[Task]:
        raw_results = await self._collection.find(
            {"is_prerequisite_for": {"$elemMatch": {"id": str(task_id)}}},
        )

        results = []

        for raw_task in raw_results:
            raw_dependencies = await self._collection.find(
                {"id": {"$in": [t["id"] for t in raw_task["is_prerequisite_for"]]}},
            ).to_list(length=None)
            results.append(Task.from_raw(raw_task, raw_dependencies))

        return results
