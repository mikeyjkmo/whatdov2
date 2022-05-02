from whatdo2.service_layer.task_service import TaskService
from whatdo2.domain.task.typedefs import TaskType
from datetime import datetime
from pydantic.main import BaseModel
import dataclasses as dc
from fastapi import FastAPI
from typing import Dict, Any
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


@app.get("/tasks")
async def task_list() -> Dict[Any, Any]:
    def _clean(t: Dict[Any, Any]) -> Dict[Any, Any]:
        result = t.copy()
        del result["_id"]
        return result

    return {
        "tasks": [
            _clean(t)
            for t in await db.tasks.find()
            .sort("effective_density", -1)
            .to_list(length=None)
        ]
    }


@app.post("/tasks")
async def create_task(task: TaskCreationPayload) -> Dict[Any, Any]:
    result = await service.create_task(
        name=task.name,
        importance=task.importance,
        time=task.time,
        task_type=task.task_type,
        activation_time=task.activation_time,
    )
    return {
        "task": dc.asdict(result),
    }
