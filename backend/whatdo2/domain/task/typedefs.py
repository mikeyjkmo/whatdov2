from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional, Tuple, Type

from pydantic import dataclasses as dc

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
    is_active: bool


@dc.dataclass(frozen=True)
class DependentTask(BaseTask):
    density: float
    effective_density: float

    @classmethod
    def from_task(cls: Type["DependentTask"], t: "Task") -> "DependentTask":
        if t.density is None or t.effective_density is None:
            raise ValueError(
                "Initialized task cannot have None as density or effective_density",
            )

        return cls(
            id=t.id,
            name=t.name,
            importance=t.importance,
            task_type=t.task_type,
            time=t.time,
            activation_time=t.activation_time,
            is_active=t.is_active,
            density=t.density,
            effective_density=t.effective_density,
        )

    @classmethod
    def from_raw(cls: Type["DependentTask"], data: Dict[Any, Any]) -> "DependentTask":
        init_data = data.copy()
        del init_data["_id"]
        del init_data["is_prerequisite_for"]
        return cls(**init_data)


@dc.dataclass(frozen=True)
class Task(BaseTask):
    density: Optional[float] = None
    effective_density: Optional[float] = None
    is_prerequisite_for: Tuple[DependentTask, ...] = ()

    @classmethod
    def from_raw(
        cls: Type["Task"],
        raw_task: Dict[Any, Any],
        raw_dependencies: Tuple[Dict[Any, Any], ...],
    ) -> "Task":
        raw_task["is_prerequisite_for"] = tuple(
            DependentTask.from_raw(t) for t in raw_dependencies
        )
        del raw_task["_id"]
        return cls(**raw_task)
