from datetime import datetime
from typing import List
from uuid import UUID

from motor.motor_asyncio import AsyncIOMotorClient

from whatdo2.adapters.task_repository import MongoTaskRepository
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import Task, TaskType
from whatdo2.domain.task.events import TaskActivated, TaskDeactivated, TaskEvent
from whatdo2.utils import flatten


class TaskCommandService:
    def __init__(self) -> None:
        self._get_current_time = datetime.utcnow
        self._repository = MongoTaskRepository(
            db=AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
        )

    async def _dispatch(self, *events: TaskEvent) -> None:
        for event in events:
            if isinstance(event, TaskActivated) or isinstance(event, TaskDeactivated):
                # list tasks that are dependencies for this task,
                # then update their statuses
                pass

    async def create_task(
        self,
        name: str,
        importance: int,
        time: int,
        task_type: TaskType,
        activation_time: datetime,
    ) -> Task:
        new_task = Task.new(
            name=name,
            importance=importance,
            time=time,
            task_type=task_type,
            activation_time=activation_time,
            is_active=True,
        ).update_is_active(current_time=datetime.utcnow())
        await self._repository.save(new_task)
        return new_task

    async def add_dependent_task(self, task_id: UUID, dependent_task_id: UUID) -> Task:
        t1 = await self._repository.get(task_id=task_id)
        t2 = await self._repository.get(task_id=dependent_task_id)

        result = t1.add_dependent_tasks([t2])
        await self._repository.save(result)
        return result

    async def activate_ready_tasks(self) -> None:
        tasks = await self._repository.list_inactive_with_past_activation_times()
        tasks = [t.update_is_active(datetime.utcnow()) for t in tasks]
        events: List[TaskEvent] = flatten([t.events for t in tasks])

        for task in tasks:
            await self._repository.save(task)

        await self._dispatch(*events)
