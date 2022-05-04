from datetime import datetime
from typing import List
from uuid import UUID

from fastapi import FastAPI
from motor.motor_asyncio import AsyncIOMotorClient
from pydantic.main import BaseModel

from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME
from whatdo2.domain.task.core import TaskType
from whatdo2.service_layer.task_command_service import TaskCommandService
from whatdo2.service_layer.task_query_service import TaskDTO, TaskQueryService

app = FastAPI()
db = AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
command_service = TaskCommandService()
query_service = TaskQueryService()


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
