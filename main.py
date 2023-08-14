import logging
import pkgutil
import sys
import traceback
from asyncio import AbstractEventLoop

import kayaku
from avilla.console.protocol import ConsoleProtocol
from avilla.core import Avilla

# from avilla.red.net.ws_client import RedWsClientConfig, RedWsClientNetworking
# from avilla.red.protocol import RedProtocol
from creart import create
from graia.broadcast import Broadcast
from graia.saya import Saya
from launart import Launart
from loguru import logger

# from yarl import URL
from libs.aiohttp_service import AiohttpClientService
from libs.database.service import DatabaseService
from libs.path import modules_path
from utils import loguru_exc_callback, loguru_exc_callback_async, loguru_handler

loop = create(AbstractEventLoop)
broadcast = create(Broadcast)
saya = create(Saya)
launart = create(Launart)
avilla = Avilla(broadcast=broadcast, launch_manager=launart, message_cache_size=0)

launart.add_component(DatabaseService())
launart.add_component(AiohttpClientService())

# red_protocol = RedProtocol()
# conn = RedWsClientNetworking(
#     red_protocol,
#     RedWsClientConfig(
#         URL("ws://localhost:16530"),
#         '6cc94a89762da4cb5261b561e5078946f65f348a129883798d5a4d7366447f16',
#     ),
# )
# red_protocol.service.connections.append(conn)
# avilla.apply_protocols(red_protocol)

avilla.apply_protocols(ConsoleProtocol())

kayaku.initialize({"{**}": "./config/{**}"})

ignore = ('__init__.py', '__pycache__')
with saya.module_context():
    for module in pkgutil.iter_modules([str(modules_path)]):
        if module.name in ignore or module.name[0] in ('#', '.', '_'):
            continue
        saya.require(f'modules.{module.name}')


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

kayaku.bootstrap()
launart.launch_blocking()
