from motor.motor_asyncio import AsyncIOMotorClient
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.adapters.task_repository import MongoTaskRepository
from whatdo2.domain.task.typedefs import TaskType, Task
from whatdo2.domain.task import public as core
from datetime import datetime


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
