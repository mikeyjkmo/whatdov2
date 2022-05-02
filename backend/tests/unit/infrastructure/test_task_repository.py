import asyncio
from datetime import datetime
from typing import Any, Callable
from uuid import UUID
from whatdo2.domain.task.public import create_task, TaskType
from whatdo2.infrastructure.task_repository import MongoTaskRepository, TaskRepository
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
import pytest
from motor.motor_asyncio import AsyncIOMotorClient


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

    original_task = create_task(
        name="hello",
        importance=5,
        time=5,
        task_type=TaskType.HOME,
        activation_time=now,
    )
    await repository.save(original_task)

    # Add cleanup for task
    request.addfinalizer(
        _delete_task_finalizer(event_loop, repository, original_task.id)
    )

    result = await repository.get(task_id=original_task.id)

    assert result == original_task