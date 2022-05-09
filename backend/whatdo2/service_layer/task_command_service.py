import logging
from datetime import datetime
from typing import List
from uuid import UUID

from whatdo2.domain.task.core import Task, TaskType
from whatdo2.domain.task.events import TaskActivated, TaskDeactivated, TaskEvent
from whatdo2.service_layer.unit_of_work import UnitOfWork, new_uow
from whatdo2.utils import flatten

logger = logging.getLogger(__name__)


class TaskCommandService:
    def __init__(self) -> None:
        self._get_current_time = datetime.utcnow

    async def _dispatch(self, *events: TaskEvent) -> None:
        # TODO: Change to using eventbus
        for event in events:
            if isinstance(event, TaskActivated) or isinstance(event, TaskDeactivated):
                logger.debug(
                    "Task %s has been activated or deactivated. Updating "
                    "prerequisite tasks",
                    event.task_id,
                )
                await self.update_is_active_for_prerequisite_tasks(event.task_id)

    async def update_is_active_for_prerequisite_tasks(self, task_id: UUID) -> None:
        async with new_uow() as uow:
            tasks = await uow.task_repository.list_prerequisites_for_task(
                task_id,
            )
            await self._multiple_update_is_active(uow, tasks)

    async def _multiple_update_is_active(
        self, uow: UnitOfWork, tasks: List[Task]
    ) -> None:
        logger.debug(
            "Calling update_is_active on the following tasks: %s",
            [t.id for t in tasks],
        )
        tasks = [t.update_is_active(datetime.utcnow()) for t in tasks]
        events: List[TaskEvent] = flatten([t.events for t in tasks])

        for task in tasks:
            await uow.task_repository.save(task)

        await self._dispatch(*events)

    async def create_task(
        self,
        name: str,
        importance: int,
        time: int,
        task_type: TaskType,
        activation_time: datetime,
    ) -> Task:
        async with new_uow() as uow:
            new_task = Task.new(
                name=name,
                importance=importance,
                time=time,
                task_type=task_type,
                activation_time=activation_time,
                is_active=True,
            ).update_is_active(current_time=datetime.utcnow())
            await uow.task_repository.save(new_task)
            return new_task

    async def add_dependent_task(self, task_id: UUID, dependent_task_id: UUID) -> Task:
        async with new_uow() as uow:
            t1 = await uow.task_repository.get(task_id=task_id)
            t2 = await uow.task_repository.get(task_id=dependent_task_id)

            result = t1.add_dependent_tasks([t2])
            await uow.task_repository.save(result)
            return result

    async def activate_ready_tasks(self) -> None:
        async with new_uow() as uow:
            tasks = await uow.task_repository.list_inactive_with_past_activation_times()
            await self._multiple_update_is_active(uow, tasks)
