from abc import ABCMeta
from typing import List
from uuid import UUID

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

    async def list_prerequisites_for_task(self, task_id: UUID) -> List[Task]:
        ...
