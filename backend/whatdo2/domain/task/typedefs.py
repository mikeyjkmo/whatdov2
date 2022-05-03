from datetime import datetime
from enum import Enum

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
