from contextlib import asynccontextmanager
from typing import AsyncGenerator

from sqlalchemy.ext.asyncio.engine import create_async_engine
from sqlalchemy.ext.asyncio.session import AsyncSession

from whatdo2.adapters.sql_task_repository import SQLTaskRepository
from whatdo2.config import POSTGRES_URI


class UnitOfWork:
    def __init__(self, session: AsyncSession):
        self.task_repository = SQLTaskRepository(session)


@asynccontextmanager
async def new_uow() -> AsyncGenerator[UnitOfWork, None]:
    engine = create_async_engine(POSTGRES_URI, echo=False)
    async with AsyncSession(engine, expire_on_commit=False) as session:
        yield UnitOfWork(session)
        await session.commit()
