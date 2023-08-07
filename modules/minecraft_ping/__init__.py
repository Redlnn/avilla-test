"""
Ping mc服务器

获取指定mc服务器的信息

> 命令：/ping [mc服务器地址]
"""

import ipaddress
import re
import socket

from avilla.core import Context, MessageReceived
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from loguru import logger

from .aiodns_resolver import dns_resolver, dns_resolver_srv
from .ping_client import ping

channel = Channel.current()

channel.meta['name'] = 'Ping 我的世界服务器'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '获取指定mc服务器的信息\n用法：\n[!！.]ping {mc服务器地址}'

ipv4_re = re.compile(
    r'(localhost|(?:(?:25[0-5]|2[0-4]\d|[01]?\d\d?)\.){3}(?:25[0-5]|2[0-4]\d|[01]?\d\d?))(?::([1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]|[1-9][0-9]{1,3}|[1-9]))?'
)
ipv6_re = re.compile(
    r'(?:(?:\[((?:[0-9a-f]*:){6}[0-9a-f]*)\]):([1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]|[1-9][0-9]{1,3}|[1-9]))|(?:(?:[0-9a-f]*:){6}[0-9a-f]*)'
)
domain_re = re.compile(
    r'((?:(?:[a-zA-Z]{1})|(?:[a-zA-Z]{1}[a-zA-Z]{1})|'
    r'(?:[a-zA-Z]{1}[0-9]{1})|(?:[0-9]{1}[a-zA-Z]{1})|'
    r'(?:[a-zA-Z0-9][-_.a-zA-Z0-9]{0,61}[a-zA-Z0-9]))\.'
    r'(?:[a-zA-Z]{2,13}|[a-zA-Z0-9-]{2,30}.[a-zA-Z]{2,3})):?([1-5][0-9]{4}|6[0-4][0-9]{3}|65[0-4][0-9]{2}|655[0-2][0-9]|6553[0-5]|[1-9][0-9]{1,3}|[1-9])?'
)


def verify_ipv6(ipv6: str):
    return bool(ipaddress.ip_address(ipv6))


@channel.use(ListenerSchema(listening_events=[MessageReceived]))
async def main(ctx: Context, event: MessageReceived):
    message = str(event.message.content)
    if message.startswith('/ping '):
        return
    else:
        message = message[6:]

    try:
        if res := ipv4_re.match(message):
            ip, port = res.groups()
        elif res := ipv6_re.match(message):
            ip, port = res.groups()
            if not verify_ipv6(ip):
                return
        elif res := domain_re.match(message):
            ip, port = res.groups()
            if dns_res := await dns_resolver_srv(ip):
                target_ip, target_port = dns_res
                if target_ip is not False:
                    ip, port = target_ip, target_port
                else:
                    dns_res = await dns_resolver(ip)
                    if dns_res is False:
                        return
                    ip = dns_res
        else:
            return
        logger.success(f'{ip}:{port}')
        port = int(port) if port is not None else 25565
        try:
            ping_result = await ping(ip, port)
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

        if ping_result['motd'] is not None and ping_result['motd'] != '':
            motd_list: list[str] = ping_result['motd'].split('\n')
            motd = f' | {motd_list[0].strip()}'
            if len(motd_list) == 2:
                motd += f'\n | {motd_list[1].strip()}'
        else:
            motd = None
        msg_send = f'咕咕咕！🎉\n服务器版本: [{ping_result["protocol"]}] {ping_result["version"]}\n'
        msg_send += f'MOTD:\n{motd}\n' if motd is not None else ''
        msg_send += f'延迟: {ping_result["delay"]}ms\n'
        msg_send += f'在线人数: {ping_result["online_player"]}/{ping_result["max_player"]}'
        if ping_result['online_player'] != '0' and ping_result['player_list']:
            players_list = ''.join(f' | {_["name"]}\n' for _ in ping_result['player_list'])
            if int(ping_result['online_player']) != len(ping_result['player_list']):
                msg_send += f'\n在线列表：\n{players_list.rstrip()}\n | ...'
            else:
                msg_send += f'\n在线列表：\n{players_list.rstrip()}'

        await ctx.scene.send_message(msg_send)
    except Exception as e:
        logger.exception(e)
