import asyncio
from datetime import datetime
import logging
from typing import List
from uuid import UUID

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.main import BaseModel

from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import TaskType
from whatdo2.service_layer.task_command_service import TaskCommandService
from whatdo2.service_layer.task_query_service import TaskDTO, TaskQueryService
from whatdo2.logging import set_up_logging

set_up_logging()
app = FastAPI()
db = AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
command_service = TaskCommandService()
query_service = TaskQueryService()

ACTIVATION_BACKGROUND_TASK = None
logger = logging.getLogger(__name__)


class TaskCreationPayload(BaseModel):
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime


class DependentTaskPayload(BaseModel):
    id: UUID


class TaskListReponse(BaseModel):
    tasks: List[TaskDTO]


class TaskResponse(BaseModel):
    task: TaskDTO


@app.get("/tasks")
async def task_list() -> TaskListReponse:
    return TaskListReponse(tasks=await query_service.list_tasks())


@app.post("/tasks")
async def create_task(task: TaskCreationPayload) -> TaskResponse:
    result = await command_service.create_task(
        name=task.name,
        importance=task.importance,
        time=task.time,
        task_type=task.task_type,
        activation_time=task.activation_time,
    )
    return TaskResponse(task=TaskDTO.parse_obj(result.to_raw()))


@app.post("/task/{task_id}/dependent_tasks")
async def add_dependent_task(
    task_id: UUID,
    dependent_task: DependentTaskPayload,
) -> TaskResponse:
    result = await command_service.add_dependent_task(
        task_id=task_id,
        dependent_task_id=dependent_task.id,
    )
    return TaskResponse(task=TaskDTO.parse_obj(result.to_raw()))


async def run_activate_ready_task_loop() -> None:
    """
    Main background task loop
    """
    async def _activate_ready_tasks() -> None:
        logger.debug("Activating inactive ready tasks")
        await command_service.activate_ready_tasks()

    while True:
        try:
            await _activate_ready_tasks()
        except Exception:
            logger.exception("An error occurred during background task:")

        await asyncio.sleep(10)


@app.on_event("startup")
async def start_regular_task_activation_task() -> None:
    loop = asyncio.get_running_loop()
    global ACTIVATION_BACKGROUND_TASK
    ACTIVATION_BACKGROUND_TASK = loop.create_task(run_activate_ready_task_loop())


@app.on_event("shutdown")
async def stop_regular_task_activation_task() -> None:
    if ACTIVATION_BACKGROUND_TASK:
        ACTIVATION_BACKGROUND_TASK.cancel()
