from collections import defaultdict
from typing import Callable, Dict, List, Type

from whatdo2.domain.typedefs import DomainEvent

EventHandler = Callable[[DomainEvent], None]


class EventBus:
    def __init__(self) -> None:
        self._handlers: Dict[Type[DomainEvent], List[EventHandler]] = defaultdict(list)

    def register(self, event_type: Type[DomainEvent], handler: EventHandler) -> None:
        self._handlers[event_type].append(handler)
