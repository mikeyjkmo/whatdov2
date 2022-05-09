from dataclasses import asdict as dc_asdict
from dataclasses import fields as dc_fields
from dataclasses import replace as dc_replace
from typing import Any, Dict, Type, TypeVar
from uuid import UUID

from pydantic import dataclasses as dc

T = TypeVar("T", bound="Entity")


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

    @classmethod
    def from_orm(cls: Type[T], orm: Any) -> T:
        fields = dc_fields(cls)
        constr_dict = {
            field.name: getattr(orm, field.name)
            for field in fields
            if hasattr(orm, field.name)
        }
        return cls(**constr_dict)

    def _replace(self: T, **params: Any) -> T:
        """
        Create a new Entity with the parameters replaced
        """
        return dc_replace(self, **params)
