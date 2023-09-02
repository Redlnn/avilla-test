import logging
import pkgutil
import sys
import traceback
from asyncio import AbstractEventLoop

import creart
import kayaku
from avilla.core.application import Avilla
from avilla.elizabeth.protocol import ElizabethConfig, ElizabethProtocol
from graia.broadcast import Broadcast
from graia.saya import Saya
from graiax.playwright.service import PlaywrightService
from launart import Launart
from loguru import logger

kayaku.initialize({"{**}": "./config/{**}"})

# ruff: noqa: E402

from libs.aiohttp_service import AiohttpClientService
from libs.config import BasicConfig
from libs.database.service import DatabaseService
from libs.path import modules_path
from utils import loguru_exc_callback, loguru_exc_callback_async, loguru_handler

loop = creart.create(AbstractEventLoop)
broadcast = creart.create(Broadcast)
saya = creart.create(Saya)
launart = creart.create(Launart)
avilla = Avilla(broadcast=broadcast, launch_manager=launart, message_cache_size=0)

ignore = ('__init__.py', '__pycache__')
with saya.module_context():
    for module in pkgutil.iter_modules([str(modules_path)]):
        if module.name in ignore or module.name[0] in ('#', '.', '_'):
            continue
        saya.require(f'modules.{module.name}')

kayaku.bootstrap()
basic_cfg = kayaku.create(BasicConfig)

launart.add_component(PlaywrightService())
launart.add_component(DatabaseService(basic_cfg.databaseUrl))
launart.add_component(AiohttpClientService())

avilla.apply_protocols(
    ElizabethProtocol().configure(
        ElizabethConfig(
            basic_cfg.miraiApiHttp.account,
            basic_cfg.miraiApiHttp.host,
            basic_cfg.miraiApiHttp.port,
            basic_cfg.miraiApiHttp.verifyKey,
        )
    )
)


logging.basicConfig(handlers=[loguru_handler], level=0, force=True)
for name in logging.root.manager.loggerDict:
    _logger = logging.getLogger(name)
    for handler in _logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            _logger.removeHandler(handler)

logger.remove()
logger.add(sys.stderr, level="DEBUG", enqueue=True)

loop.set_exception_handler(loguru_exc_callback_async)
traceback.print_exception = loguru_exc_callback

launart.launch_blocking()
kayaku.save_all()
