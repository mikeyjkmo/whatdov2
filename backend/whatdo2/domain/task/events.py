import dataclasses as dc
from uuid import UUID

from whatdo2.domain.typedefs import DomainEvent


@dc.dataclass(frozen=True)
class TaskEvent(DomainEvent):
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
