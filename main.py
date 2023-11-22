import pkgutil
from asyncio import AbstractEventLoop

import creart
import kayaku
from avilla.core.application import Avilla
from avilla.elizabeth.protocol import ElizabethConfig, ElizabethProtocol
from avilla.qqapi.protocol import Intents, QQAPIConfig, QQAPIProtocol
from graia.broadcast import Broadcast
from graia.saya import Saya
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graiax.playwright.service import PlaywrightService
from launart import Launart

from libs.logger import replace_logger

kayaku.initialize({"{**}": "./config/{**}"})

# ruff: noqa: E402

from libs.aiohttp_service import AiohttpClientService
from libs.config import BasicConfig
from libs.control import require_blacklist, require_disable
from libs.database.service import DatabaseService
from libs.path import modules_path

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
        channel = saya.require(f'modules.{module.name}')
        # for func in channel.content:
        #     if isinstance(func.metaclass, ListenerSchema):
        #         func.metaclass.decorators.append(require_blacklist())
        #         func.metaclass.decorators.append(require_disable(channel.module))


kayaku.bootstrap()
basic_cfg = kayaku.create(BasicConfig)

launart.add_component(PlaywrightService())
launart.add_component(DatabaseService(basic_cfg.databaseUrl))
launart.add_component(AiohttpClientService())

if basic_cfg.miraiApiHttp.enabled:
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

if basic_cfg.qqAPI.enabled:
    avilla.apply_protocols(
        QQAPIProtocol().configure(
            QQAPIConfig(
                id=basic_cfg.qqAPI.id,
                token=basic_cfg.qqAPI.token,
                secret=basic_cfg.qqAPI.secret,
                is_sandbox=basic_cfg.qqAPI.isSandbox,
                intent=Intents(guild_messages=True, at_messages=False, direct_message=True),
            )
        )
    )

replace_logger(loop, 'DEBUG')

launart.launch_blocking()
kayaku.save_all()
