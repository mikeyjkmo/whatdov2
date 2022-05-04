from dataclasses import asdict as dc_asdict
from typing import Any, Dict
from uuid import UUID

from pydantic import dataclasses as dc


@dc.dataclass(frozen=True)
class DomainEvent:
    pass


@dc.dataclass(frozen=True)
class Entity:
    id: UUID

    def to_raw(self) -> Dict[Any, Any]:
        result = dc_asdict(self)
        if "events" in result:
            del result["events"]
        return result
