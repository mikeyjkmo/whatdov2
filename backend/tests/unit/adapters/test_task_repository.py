import asyncio
from datetime import datetime, timedelta
from typing import Any, Callable
from uuid import UUID

import pytest
from motor.motor_asyncio import AsyncIOMotorClient

from whatdo2.adapters.task_repository import MongoTaskRepository, TaskRepository
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import Task, TaskType

pytestmark = pytest.mark.db_unit_test


@pytest.fixture(name="repository")
def mongo_repository() -> MongoTaskRepository:
    return MongoTaskRepository(
        db=AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME],
        collection_name="tasks_test",
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
    """
    Given that I have a parent and child task
    When I persist it and retrieve it using the repository
    Then I should get the same domain object back
    """
    now = datetime.now().replace(microsecond=0)

    child = Task.new(
        name="hello 2",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=now,
        is_active=True,
    )
    parent = Task.new(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=now,
        is_active=True,
    ).add_dependent_tasks([child])

    await repository.save(child)
    await repository.save(parent)

    # Add cleanup for task
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, parent.id))
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, child.id))

    result = await repository.get(task_id=parent.id)
    assert result == parent


@pytest.mark.asyncio
async def test_list_inactive_with_past_activation_time(
    event_loop: asyncio.BaseEventLoop,
    repository: TaskRepository,
    request: Any,
) -> None:
    """
    Given that I have a parent and child task, the parent of which is inactive
      with a past activation time
    When I persist it and call list_inactive_with_past_activation_times
    Then I should get the same domain object back
    """
    past = datetime.now().replace(microsecond=0) - timedelta(days=1)

    child = Task.new(
        name="hello 2",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=past,
        is_active=True,
    )
    task = Task.new(
        name="TEST PAST ACTIVATION TIME INACTIVE TASK",
        importance=8,
        time=5,
        task_type=TaskType.HOME,
        activation_time=past,
        is_active=False,
    ).add_dependent_tasks([child])

    await repository.save(child)
    await repository.save(task)

    # Add cleanup for task
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, task.id))
    request.addfinalizer(_delete_task_finalizer(event_loop, repository, child.id))

    result = await repository.list_inactive_with_past_activation_times()

    assert result == [task]
