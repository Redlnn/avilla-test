from typing import Any, Literal

from launart import Service
from loguru import logger
from sqlalchemy.engine import make_url
from sqlalchemy.engine.url import URL

from libs.database.manager import DatabaseManager


class DatabaseService(Service):
    id: str = "database/init"
    db_manager: DatabaseManager

    def __init__(self, url: str | URL) -> None:
        if isinstance(url, str):
            url = make_url(url)
        self.db_manager = DatabaseManager(url)
        super().__init__()

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
