from datetime import datetime
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from whatdo2.adapters.task_repository import MongoTaskRepository
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task import public as core
from whatdo2.domain.task.typedefs import Task, TaskType


class TaskService:
    def __init__(self) -> None:
        self._get_current_time = datetime.utcnow
        self._repository = MongoTaskRepository(
            db=AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
        )

    async def create_task(
        self,
        name: str,
        importance: int,
        time: int,
        task_type: TaskType,
        activation_time: datetime,
    ) -> Task:
        new_task = core.create_task(
            name=name,
            importance=importance,
            time=time,
            task_type=task_type,
            activation_time=activation_time,
            creation_time=self._get_current_time(),
        )
        await self._repository.save(new_task)
        return new_task

    async def add_dependent_task(self, task_id: UUID, dependent_task_id: UUID) -> Task:
        t1 = await self._repository.get(task_id=task_id)
        t2 = await self._repository.get(task_id=dependent_task_id)

        new_t1 = core.make_prerequisite_of(t1, [t2])
        await self._repository.save(new_t1)

        return new_t1