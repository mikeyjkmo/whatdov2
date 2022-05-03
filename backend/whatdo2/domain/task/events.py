import dataclasses as dc
from uuid import UUID


@dc.dataclass(frozen=True)
class TaskEvent:
    pass


@dc.dataclass(frozen=True)
class TaskCreated(TaskEvent):
    id: UUID


@dc.dataclass(frozen=True)
class TaskActivated(TaskEvent):
    id: UUID


@dc.dataclass(frozen=True)
class TaskDeactivated(TaskEvent):
    id: UUID
