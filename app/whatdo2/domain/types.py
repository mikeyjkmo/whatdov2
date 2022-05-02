from uuid import UUID
import dataclasses as dc


@dc.dataclass(frozen=True)
class Entity:
    id: UUID
