import ipaddress
import re
from typing import TYPE_CHECKING

from .aiodns_resolver import dns_resolver, dns_resolver_srv

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


async def ip_resolver(string: str) -> tuple[str, str]:
    if res := ipv4_re.match(string):
        ip, port = res.groups()
        return ip, port
    elif res := ipv6_re.match(string):
        ip, port = res.groups()
        if not verify_ipv6(ip):
            raise ValueError('Is not a ipv6 address')
        return ip, port
    elif res := domain_re.match(string):
        ip, port = res.groups()
        if dns_res := await dns_resolver_srv(ip):
            target_ip, target_port = dns_res
            if target_ip is False:
                dns_res = await dns_resolver(ip)
                if dns_res is False:
                    raise ValueError(f'Can not resolve domain: {ip}')
                ip = dns_res
            elif TYPE_CHECKING and target_port is False:
                raise
            else:
                ip, port = target_ip, target_port
        return ip, port
    else:
        raise ValueError('Is not a ipv4 address or a url')
