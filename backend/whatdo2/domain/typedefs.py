from uuid import UUID

from pydantic import dataclasses as dc


@dc.dataclass(frozen=True)
class Entity:
    id: UUID
