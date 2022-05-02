from typing import Tuple
import dataclasses as dc
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
    depends_on: Tuple["Task", ...]


@dc.dataclass(frozen=True)
class PartiallyInitializedTask(BaseTask):
    pass


@dc.dataclass(frozen=True)
class Task(BaseTask):
    density: float
    effective_density: float
