from uuid import UUID
from whatdo2.service_layer.task_service import TaskService
from whatdo2.domain.task.typedefs import TaskType
from datetime import datetime
from pydantic.main import BaseModel
import dataclasses as dc
from fastapi import FastAPI
from typing import Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorClient
from whatdo2.config import MONGO_CONNECTION_STR, MONGO_DB_NAME

app = FastAPI()
db = AsyncIOMotorClient(MONGO_CONNECTION_STR)[MONGO_DB_NAME]
service = TaskService()


class TaskCreationPayload(BaseModel):
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime


class DependentTaskPayload(BaseModel):
    id: UUID


class DependentTask(BaseModel):
    id: UUID


class Task(BaseModel):
    id: UUID
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime
    is_active: bool
    density: float
    effective_density: float
    is_prerequisite_for: List[DependentTask]


class TaskListReponse(BaseModel):
    tasks: List[Task]


class TaskResponse(BaseModel):
    task: Task


@app.get("/tasks")
async def task_list() -> TaskListReponse:
    def _clean(t: Dict[Any, Any]) -> Dict[Any, Any]:
        result = t.copy()
        del result["_id"]
        return result

    return TaskListReponse.parse_obj({
        "tasks": [
            _clean(t)
            for t in await db.tasks.find()
            .sort("effective_density", -1)
            .to_list(length=None)
        ]
    })


@app.post("/tasks")
async def create_task(task: TaskCreationPayload) -> TaskResponse:
    result = await service.create_task(
        name=task.name,
        importance=task.importance,
        time=task.time,
        task_type=task.task_type,
        activation_time=task.activation_time,
    )
    return TaskResponse(task=Task.parse_obj(dc.asdict(result)))


@app.post("/task/{task_id}/dependent_tasks")
async def add_dependent_task(
    task_id: UUID,
    dependent_task: DependentTaskPayload,
) -> TaskResponse:
    result = await service.add_dependent_task(
        task_id=task_id,
        dependent_task_id=dependent_task.id,
    )
    return TaskResponse(task=Task.parse_obj(dc.asdict(result)))
