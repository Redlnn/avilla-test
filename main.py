import pkgutil
from asyncio import AbstractEventLoop

import kayaku
from arclet.alconna.graia import AlconnaBehaviour
from avilla.core.application import Avilla
from avilla.elizabeth.protocol import ElizabethConfig, ElizabethProtocol
from avilla.onebot.v11.protocol import OneBot11ForwardConfig, OneBot11Protocol
from avilla.qqapi.protocol import Intents, QQAPIConfig, QQAPIProtocol
from creart import it
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graia.scheduler import GraiaScheduler
from graia.scheduler.service import SchedulerService
from graiax.playwright.service import PlaywrightService
from launart import Launart
from yarl import URL

from libs.logger import replace_logger
from utils.test import ABotDispatcher

kayaku.initialize({"{**}": "./config/{**}"})

# ruff: noqa: E402

from libs import RedbotDispatcher
from libs.aiohttp_service import AiohttpClientService
from libs.config import BasicConfig
from libs.control import require_blacklist, require_disable
from libs.database.service import DatabaseService
from libs.path import modules_path

loop = it(AbstractEventLoop)

replace_logger(loop, "DEBUG")

bcc = it(Broadcast)
saya = it(Saya)
launart = it(Launart)
it(AlconnaBehaviour)
avilla = Avilla(broadcast=bcc, launch_manager=launart, message_cache_size=0)

bcc.finale_dispatchers.append(RedbotDispatcher)
# inject_bypass_listener(broadcast=bcc)

ignore = ('__init__.py', '__pycache__')
with saya.module_context():
    for module in pkgutil.iter_modules([str(modules_path)]):
        if module.name in ignore or module.name[0] in ('#', '.', '_'):
            continue
        channel = saya.require(f'modules.{module.name}')
        for listener in bcc.listeners:
            for cube in channel.content:
                if isinstance(cube.metaclass, ListenerSchema) and listener.callable == cube.content:
                    listener.decorators.append(require_blacklist())
                    listener.decorators.append(require_disable(channel.module))


kayaku.bootstrap()
basic_cfg = kayaku.create(BasicConfig)

launart.add_component(SchedulerService(it(GraiaScheduler)))
launart.add_component(PlaywrightService())
launart.add_component(DatabaseService(basic_cfg.databaseUrl))
launart.add_component(AiohttpClientService())

if basic_cfg.protocol.miraiApiHttp.enabled:
    avilla.apply_protocols(
        ElizabethProtocol().configure(
            ElizabethConfig(
                basic_cfg.protocol.miraiApiHttp.account,
                basic_cfg.protocol.miraiApiHttp.host,
                basic_cfg.protocol.miraiApiHttp.port,
                basic_cfg.protocol.miraiApiHttp.verifyKey,
            )
        )
    )

if basic_cfg.protocol.QQAPI.enabled:
    avilla.apply_protocols(
        QQAPIProtocol().configure(
            QQAPIConfig(
                id=basic_cfg.protocol.QQAPI.id,
                token=basic_cfg.protocol.QQAPI.token,
                secret=basic_cfg.protocol.QQAPI.secret,
                is_sandbox=basic_cfg.protocol.QQAPI.isSandbox,
                intent=Intents(guild_messages=True, at_messages=False, direct_message=True),
            )
        )
    )

if basic_cfg.protocol.OneBot11.enabled:
    avilla.apply_protocols(
        OneBot11Protocol().configure(
            OneBot11ForwardConfig(
                URL(basic_cfg.protocol.OneBot11.forward_url),
                basic_cfg.protocol.OneBot11.forward_token,
            )
        )
    )

bcc.prelude_dispatchers.append(ABotDispatcher)
launart.launch_blocking()
kayaku.save_all()
