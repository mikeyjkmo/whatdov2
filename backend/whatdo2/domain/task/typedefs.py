from typing import Tuple, Type
from pydantic import dataclasses as dc
from datetime import datetime
from enum import Enum
from whatdo2.domain.typedefs import Entity


class TaskType(str, Enum):
    HOME = "HOME"
    WORK = "WORK"


@dc.dataclass(frozen=True)
class BaseTask(Entity):
    name: str
    importance: int
    task_type: TaskType
    time: int
    activation_time: datetime


@dc.dataclass(frozen=True)
class DependentTask(BaseTask):
    density: float
    effective_density: float

    @classmethod
    def from_task(cls: Type["DependentTask"], t: "Task") -> "DependentTask":
        return cls(
            id=t.id,
            name=t.name,
            importance=t.importance,
            task_type=t.task_type,
            time=t.time,
            activation_time=t.activation_time,
            density=t.density,
            effective_density=t.effective_density,
        )


@dc.dataclass(frozen=True)
class PartiallyInitializedTask(BaseTask):
    depends_on: Tuple[DependentTask, ...]


@dc.dataclass(frozen=True)
class Task(PartiallyInitializedTask):
    density: float
    effective_density: float
