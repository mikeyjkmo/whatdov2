import dataclasses as dc
from uuid import UUID

from whatdo2.domain.typedefs import DomainEvent


@dc.dataclass(frozen=True)
class TaskEvent(DomainEvent):
    task_id: UUID


@dc.dataclass(frozen=True)
class TaskCreated(TaskEvent):
    pass


@dc.dataclass(frozen=True)
class TaskActivated(TaskEvent):
    pass


@dc.dataclass(frozen=True)
class TaskDeactivated(TaskEvent):
    pass
