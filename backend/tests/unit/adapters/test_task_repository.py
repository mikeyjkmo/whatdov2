import asyncio
from datetime import datetime
from typing import Any, Callable
from uuid import UUID

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from whatdo2.adapters.task_repository import MongoTaskRepository, TaskRepository
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import AddDependentTasks, CreateTask, TaskType

__pytestmark__ = ["db_unit_test"]


@pytest.fixture(name="repository")
def mongo_repository() -> MongoTaskRepository:
    return MongoTaskRepository(
        db=AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
    )


def _delete_task_finalizer(
    event_loop: asyncio.BaseEventLoop,
    repository: TaskRepository,
    task_id: UUID,
) -> Callable[[], None]:
    def delete_task() -> None:
        event_loop.run_until_complete(
            repository.delete(task_id=task_id),
        )

    return delete_task


@pytest.mark.asyncio
async def test_save_and_get(
    event_loop: asyncio.BaseEventLoop,
    repository: TaskRepository,
    request: Any,
) -> None:
    now = datetime.now().replace(microsecond=0)
    create_task = CreateTask(at_time=now)

    original_task = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=now,
    )
    dep_task = create_task(
        name="hello 2",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=now,
    )
    new_task = AddDependentTasks(
        at_time=now,
        dependent_tasks=[dep_task],
    )(original_task)

    await repository.save(dep_task)
    await repository.save(new_task)

    # Add cleanup for task
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, new_task.id))
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, dep_task.id))

    result = await repository.get(task_id=new_task.id)
    assert result == new_task
