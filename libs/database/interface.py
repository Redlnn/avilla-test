import contextlib
from collections.abc import AsyncGenerator, Sequence
from typing import TYPE_CHECKING, Any

from sqlalchemy.engine.result import Result
from sqlalchemy.ext.asyncio import AsyncSession, async_scoped_session
from sqlalchemy.sql.base import Executable
from sqlalchemy.sql.selectable import TypedReturnsRows

from libs.database.manager import T_Row
from libs.database.model import Base

if TYPE_CHECKING:
    from libs.database.manager import DatabaseManager


class DatabaseImpl:
    db: "DatabaseManager"

    def __init__(self, db: "DatabaseManager"):
        self.db = db

    if not TYPE_CHECKING:

        def __getattr__(self, name: str) -> Any:
            return self.db.__getattribute__(name)


class DatabaseStub:
    db: "DatabaseManager"

    def __init__(self, db: "DatabaseManager"):
        self.db = db

    @contextlib.asynccontextmanager
    async def async_session(self) -> AsyncGenerator[async_scoped_session[AsyncSession], Any]:
        ...

    async def exec(self, sql: Executable) -> Result:
        ...

    async def select_all(self, sql: TypedReturnsRows[tuple[T_Row]]) -> Sequence[T_Row]:
        ...

    async def select_first(self, sql: TypedReturnsRows[tuple[T_Row]]) -> T_Row | None:
        ...

    async def add(self, row):
        ...

    async def add_many(self, rows: Sequence[Base]):
        ...

    async def update_or_add(self, row):
        ...

    async def delete_exist(self, row):
        ...

    async def delete_many_exist(self, *rows):
        ...


Database = DatabaseStub if TYPE_CHECKING else DatabaseImpl
