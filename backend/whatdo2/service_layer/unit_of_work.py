from contextlib import asynccontextmanager
from typing import AsyncGenerator, List

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from whatdo2.adapters.sql_task_repository import SQLTaskRepository
from whatdo2.config import POSTGRES_URI
from whatdo2.domain.typedefs import DomainEvent
from whatdo2.service_layer.eventbus import EventBus


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.task_repository = SQLTaskRepository(session)
        self._events: List[DomainEvent] = []

    def push_events(self, *events: DomainEvent) -> None:
        for event in events:
            self._events.append(event)

    @property
    def pushed_events(self) -> List[DomainEvent]:
        return self._events


@asynccontextmanager
async def new_uow(eventbus: EventBus) -> AsyncGenerator[UnitOfWork, None]:
    engine = create_async_engine(POSTGRES_URI, echo=False)

    async with AsyncSession(engine, expire_on_commit=False) as session:
        uow = UnitOfWork(session)
        yield uow
        await session.commit()

    # Publish events after transaction is over
    await eventbus.dispatch(*uow.pushed_events)
