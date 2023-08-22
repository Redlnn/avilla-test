import logging
import pkgutil
import sys
import traceback
from asyncio import AbstractEventLoop

import kayaku
from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla
from avilla.elizabeth.connection.ws_client import (
    ElizabethWsClientConfig,
    ElizabethWsClientNetworking,
)
from avilla.elizabeth.protocol import ElizabethProtocol

# from avilla.red.net.ws_client import RedWsClientConfig, RedWsClientNetworking
# from avilla.red.protocol import RedProtocol
from creart import create
from graia.broadcast import Broadcast
from graia.saya import Saya
from graiax.playwright.service import PlaywrightService
from launart import Launart
from loguru import logger
from yarl import URL

from libs.aiohttp_service import AiohttpClientService
from libs.config import BasicConfig
from libs.database.service import DatabaseService
from libs.path import modules_path
from utils import loguru_exc_callback, loguru_exc_callback_async, loguru_handler

loop = create(AbstractEventLoop)
broadcast = create(Broadcast)
saya = create(Saya)
launart = create(Launart)
avilla = Avilla(broadcast=broadcast, launch_manager=launart, message_cache_size=0)

kayaku.initialize({"{**}": "./config/{**}"})

ignore = ('__init__.py', '__pycache__')
with saya.module_context():
    for module in pkgutil.iter_modules([str(modules_path)]):
        if module.name in ignore or module.name[0] in ('#', '.', '_'):
            continue
        saya.require(f'modules.{module.name}')

kayaku.bootstrap()
basic_cfg = create(BasicConfig)

launart.add_component(PlaywrightService())
launart.add_component(DatabaseService(basic_cfg.databaseUrl))
launart.add_component(AiohttpClientService())

# avilla.apply_protocols(ConsoleProtocol())

# red_protocol = RedProtocol()
# red_conn = RedWsClientNetworking(
#     red_protocol,
#     RedWsClientConfig(
#         URL("ws://localhost:16530"),
#         '6cc94a89762da4cb5261b561e5078946f65f348a129883798d5a4d7366447f16',
#     ),
# )
# red_protocol.service.connections.append(red_conn)
# avilla.apply_protocols(red_protocol)

mah_protocol = ElizabethProtocol()
mah_conn = ElizabethWsClientNetworking(
    mah_protocol,
    ElizabethWsClientConfig(
        URL(basic_cfg.miraiApiHttp.host),
        basic_cfg.miraiApiHttp.verifyKey,
        basic_cfg.miraiApiHttp.account,
    ),
)
mah_protocol.service.connections.append(mah_conn)
avilla.apply_protocols(mah_protocol)

logging.basicConfig(handlers=[loguru_handler], level=0, force=True)
for name in logging.root.manager.loggerDict:
    _logger = logging.getLogger(name)
    for handler in _logger.handlers:
        if isinstance(handler, logging.StreamHandler):
            _logger.removeHandler(handler)

logger.remove()
logger.add(sys.stderr, level="INFO", enqueue=True)

loop.set_exception_handler(loguru_exc_callback_async)
traceback.print_exception = loguru_exc_callback

launart.launch_blocking()
kayaku.save_all()
