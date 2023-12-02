from typing import Any, Literal

from launart import Service
from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.engine.url import URL

from libs.database.interface import Database
from libs.database.manager import DatabaseManager


class DatabaseService(Service):
    id: str = "database/init"
    db_manager: DatabaseManager
    supported_interface_types: set[Any] = {Database}

    def __init__(self, url: str | URL) -> None:
        if isinstance(url, str):
            url = make_url(url)
        self.db_manager = DatabaseManager(url)
        super().__init__()

    def get_interface(self, typ: type[Database]) -> Database:
        return Database(self.db_manager)

    @property
    def required(self) -> set[str]:
        return set()

    @property
    def stages(self) -> set[Literal["preparing", "blocking", "cleanup"]]:
        return {"preparing", "cleanup"}

    async def launch(self, _):
        logger.info("Initializing database...")
        await self.db_manager.initialize()
        logger.success("Database initialized!")

        async with self.stage("preparing"):
            ...

        async with self.stage("cleanup"):
            await self.db_manager.stop()
