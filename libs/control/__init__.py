import kayaku
from avilla.core import Context, MessageReceived
from avilla.standard.core.activity.event import ActivityTrigged
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend
from graia.broadcast.entities.event import Dispatchable

from libs.config import ModulesConfig


def require_disable(module_name: str) -> Depend:
    def wrapper(event: Dispatchable):
        modules_cfg = kayaku.create(ModulesConfig, True)
        if module_name in modules_cfg.globalDisabledModules:
            raise ExecutionStop
        elif module_name in modules_cfg.disabledGroups:
            if isinstance(event, MessageReceived):
                if (
                    event.context.scene.follows('::group.*')
                    and str(event.context.client.last_value) in modules_cfg.disabledGroups[module_name]
                ):
                    raise ExecutionStop
                elif event.context.scene.follows('::channel.*'):
                    guild_id = int(event.context.scene.last_value)
                    channel_id = int(event.context.client.last_value)
                    if guild_id not in modules_cfg.disabledGuilds[module_name]:
                        return
                    for guild in modules_cfg.disabledGuilds[module_name]:
                        if guild_id != guild.guildID:
                            continue
                        if guild.globalDisabled:
                            raise ExecutionStop
                        if channel_id in guild.disabledSubchannel:
                            raise ExecutionStop
                else:
                    return
            elif (
                isinstance(event, ActivityTrigged)
                and event.context.endpoint.last_value in modules_cfg.disabledGroups[module_name]
            ):
                raise ExecutionStop

    return Depend(wrapper)
