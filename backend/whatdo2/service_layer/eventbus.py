from collections import defaultdict
from typing import Any, Awaitable, Callable, Dict, List, Type, TypeVar

from whatdo2.domain.typedefs import DomainEvent

T = TypeVar("T", bound=DomainEvent)


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[
            Type[DomainEvent], List[Callable[[Any], Awaitable[Any]]]
        ] = defaultdict(list)

    def register(
        self, event_type: Type[T], handler: Callable[[T], Awaitable[Any]]
    ) -> None:
        self._handlers[event_type].append(handler)

    async def dispatch(self, *events: DomainEvent) -> None:
        for event in events:
            for handler in self._handlers[type(event)]:
                await handler(event)
