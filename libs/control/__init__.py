from collections.abc import Sequence

import kayaku
from avilla.core import MessageReceived
from avilla.core.elements import Notice, Text
from avilla.core.event import AvillaEvent
from avilla.standard.core.activity.event import ActivityTrigged
from avilla.standard.core.privilege import Privilege
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.entities.event import Dispatchable
from graia.broadcast.exceptions import ExecutionStop
from loguru import logger

from libs.config import BasicConfig, ModulesConfig, PermConfig


def require_platform(land: Sequence[str], exclude: bool):
    """
    判断插件是否在特定平台禁用

    Args:
        land (Sequence[str]): qq、qqapi...
        exclude (bool): 是否在指定的平台外
    """

    async def __wrapper__(event: Dispatchable):
        if isinstance(event, AvillaEvent) and event.context.scene['land'] in land:
            if exclude:
                return True
            else:
                raise ExecutionStop

    return Depend(__wrapper__)


def require_disable(module_name: str) -> Depend:
    """
    判断插件是否禁用

    QQ频道时分为整个频道、某些子频道（官方APi应该用开发者后台管理吧？）
    """

    async def __wrapper__(event: Dispatchable):
        modules_cfg = kayaku.create(ModulesConfig, True)
        if module_name in modules_cfg.globalDisabledModules:
            logger.warning(f'{module_name} is disabled globally.')
            raise ExecutionStop
        elif module_name in modules_cfg.disabledGroups:
            if isinstance(event, MessageReceived):
                if (
                    event.context.scene.follows('::group.*')
                    and event.context.scene['group'] in modules_cfg.disabledGroups[module_name]
                ):
                    logger.warning(f'{module_name} is disabled for {event.context.scene['group']}.')
                    raise ExecutionStop
                elif event.context.scene.follows('::guild.*'):
                    guild_id = event.context.scene['guild']
                    channel_id = event.context.scene['channel'] or None
                    if guild_id not in modules_cfg.disabledGuilds[module_name]:
                        return True
                    for guild in modules_cfg.disabledGuilds[module_name]:
                        if guild_id != guild.guildID:
                            continue
                        if guild.globalDisabled:
                            logger.warning(f'{module_name} is disabled for guild {guild}.')
                            raise ExecutionStop
                        if channel_id in guild.disabledSubchannel:
                            logger.warning(f'{module_name} is disabled for channel {channel_id} of guild {guild}.')
                            raise ExecutionStop
                else:
                    return True
            elif (
                isinstance(event, ActivityTrigged)
                and event.context.endpoint.last_value in modules_cfg.disabledGroups[module_name]
            ):
                raise ExecutionStop

    return Depend(__wrapper__)


def require_blacklist() -> Depend:
    """判断触发者是否在黑名单或白名单内"""

    async def __wrapper__(event: Dispatchable):
        if not isinstance(event, AvillaEvent):
            return True
        perm_cfg = kayaku.create(PermConfig, True)
        if event.context.client.last_value in perm_cfg.usersBlacklist:
            raise ExecutionStop
        if perm_cfg.whitelistEndbled:
            if event.context.scene.follows('::group.*') and event.context.client['group'] not in perm_cfg.whitelist:
                raise ExecutionStop
            if event.context.scene.follows('::channel.*') and event.context.scene['guild'] not in perm_cfg.whitelist:
                raise ExecutionStop

    return Depend(__wrapper__)


def require_admin(only: bool = False):
    """
    判断是否需要管理员权限（群/频道管理员）

    判断依据是 privilege_info.available，由各个 Avilla 的适配器来确定

    ```python
    # privilege_info.available  # 对象是否持有特权
    # privilege_info.effective  # 自身对对象是否可以产生影响，通常情况下这也表示自身的特权超越对方
    ```
    """

    async def __wrapper__(event: Dispatchable):
        if not isinstance(event, AvillaEvent):
            return True
        if event.context.scene['land'] != 'qq':
            if event.context.scene.follows('::group.*'):
                return True
            if event.context.scene.follows('::friend.*'):
                return True
            private = "user" in event.context.scene
        else:
            private = "friend" in event.context.scene

        config = kayaku.create(BasicConfig, True)

        if event.context.client.last_value in config.admin.admins:
            return True
        privilege_info = await event.context.client.pull(Privilege)
        if not only and (privilege_info.available or event.context.client.last_value in config.admin.admins):
            return True
        text = "权限不足！" if private else [Notice(event.context.client), Text("\n权限不足！")]
        await event.context.scene.send_message(text)
        raise ExecutionStop

    return Depend(__wrapper__)
