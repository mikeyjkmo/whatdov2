from datetime import datetime
from typing import List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient
from pydantic import BaseModel

from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import TaskType


class DependentTaskDTO(BaseModel):
    id: UUID


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


class TaskQueryService:
    def __init__(self) -> None:
        self._db = AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]

    async def list_tasks(self) -> List[TaskDTO]:
        return [
            TaskDTO(**t)
            for t in await self._db.tasks.find()
            .sort("effective_density", -1)
            .to_list(length=None)
        ]
