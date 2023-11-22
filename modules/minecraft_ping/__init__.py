"""
Ping mc服务器

获取指定mc服务器的信息

> 命令：/ping [mc服务器地址]
"""

import asyncio
import socket
from dataclasses import field
from typing import Any

import kayaku
from avilla.core import Context, MessageReceived
from avilla.twilight.twilight import RegexMatch, RegexResult, Twilight
from graia.saya import Channel
from graiax.shortcut.saya import decorate, dispatch, listen
from loguru import logger

from libs.control import require_disable

from .ping_client import ping
from .utils import ip_resolver

channel = Channel.current()

channel.meta['name'] = 'Ping 我的世界服务器'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '获取指定mc服务器的信息\n用法：\n[!！.]ping {mc服务器地址}'


@kayaku.config(channel.module)
class McServerPingConfig:
    servers: dict[str, str] = field(default_factory=lambda: {'123456789': 'localhost:25565'})
    """指定群组的默认服务器"""


def message_maker(ping_result: dict[str, Any]):
    if ping_result['motd'] is not None and ping_result['motd'] != '':
        motd_list: list[str] = ping_result['motd'].split('\n')
        motd = f' | {motd_list[0].strip()}'
        if len(motd_list) == 2:
            motd += f'\n | {motd_list[1].strip()}'
    else:
        motd = None
    msg = f'咕咕咕！🎉\n服务器版本: [{ping_result["protocol"]}] {ping_result["version"]}\n'
    msg += f'MOTD:\n{motd}\n' if motd is not None else ''
    msg += f'延迟: {ping_result["delay"]}ms\n'
    msg += f'在线人数: {ping_result["online_player"]}/{ping_result["max_player"]}'
    if ping_result['online_player'] != '0' and ping_result['player_list']:
        players_list = ''.join(f' | {_["name"]}\n' for _ in ping_result['player_list'])
        if int(ping_result['online_player']) != len(ping_result['player_list']):
            msg += f'\n在线列表：\n{players_list.rstrip()}\n | ...'
        else:
            msg += f'\n在线列表：\n{players_list.rstrip()}'
    return msg


@listen(MessageReceived)
@dispatch(Twilight(RegexMatch(r'[!！.]ping'), 'ping_target' @ RegexMatch(r'\S+', optional=True)))
# @decorate(require_disable(channel.module))
async def main(ctx: Context, ping_target: RegexResult):
    """
    Ping 我的世界服务器

    仅支持QQ平台的群或任何满足 `ctx.scene.follows('::group')` 的平台

    Args:
        ctx (Context): _description_
        ping_target (RegexResult): _description_
    """

    if not ctx.scene.follows('::group'):
        return

    if ping_target.matched and ping_target.result is not None:
        server_address = str(ping_target.result).strip()
    else:
        ping_cfg = kayaku.create(McServerPingConfig, flush=True)
        if ctx.scene['group'] not in ping_cfg.servers:
            await ctx.scene.send_message('该群组没有设置默认服务器地址')
            return
        server_address = ping_cfg.servers[ctx.scene['group']]

    if '://' in server_address:
        await ctx.scene.send_message('不支持带有协议前缀的地址')
        return
    elif '/' in server_address:
        await ctx.scene.send_message('ping目标地址出现意外字符')
        return

    ip, port = await ip_resolver(server_address)
    port = int(port) if port is not None else 25565
    try:
        ping_result = await asyncio.to_thread(ping, host=ip, port=port)
    except ConnectionRefusedError:
        await ctx.scene.send_message('连接被目标拒绝，该地址（及端口）可能不存在 Minecraft 服务器')
        logger.warning(f'连接被目标拒绝，该地址（及端口）可能不存在Minecraft服务器，目标地址：{ip}:{port}')
        return
    except socket.timeout:
        await ctx.scene.send_message('连接超时')
        logger.warning(f'连接超时，目标地址：{ip}:{port}')
        return
    except socket.gaierror as e:
        await ctx.scene.send_message('出错了，可能是无法解析目标地址\n' + str(e))
        logger.exception(e)
        return

    if not ping_result:
        await ctx.scene.send_message('无法解析目标地址')
        logger.warning('无法解析目标地址')
        return

    await ctx.scene.send_message(message_maker(ping_result))
