from typing import Literal

from dns.asyncresolver import Resolver
from dns.rdata import Rdata
from dns.rdatatype import RdataType
from dns.rdtypes.IN.SRV import SRV


# # A 记录或 CNAME 记录
async def dns_resolver(domain: str) -> Literal[False] | str:
    resolver = Resolver()
    resolver.nameservers = ["119.29.29.29"]
    try:
        resolve_result = await resolver.resolve(domain, "A", tcp=True, lifetime=5)
    except Exception:
        return False
    if resolve_result.rrset is None:
        return False
    ips: list[Rdata] = list(resolve_result.rrset)
    return ips[0].to_text()


async def dns_resolver_srv(domain: str) -> tuple[str, str] | tuple[Literal[False], Literal[False]]:
    resolver = Resolver()
    resolver.nameservers = ["119.29.29.29"]
    try:
        resolve_result = await resolver.resolve(f"_minecraft._tcp.{domain}", "SRV", tcp=True, lifetime=5)
    except Exception:
        return False, False
    if resolve_result.rrset is None:
        return False, False
    if resolve_result.rdtype == RdataType.SRV:
        results: list[SRV] = list(resolve_result.rrset)
        host: str = results[0].target.to_text().strip(".")
        port: int = results[0].port
        return host, str(port)
    return False, False


# import asyncio
# from typing import Literal

# import aiodns
# from aiodns.error import DNSError

# resolver = aiodns.DNSResolver(loop=asyncio.get_event_loop(), nameservers=['119.29.29.29'])


# async def dns_resolver(domain: str) -> Literal[False] | str:
#     try:
#         result = await resolver.query(domain, 'A')
#         return result[0].host
#     except DNSError:
#         return False


# async def dns_resolver_srv(domain: str) -> tuple[str, str] | tuple[Literal[False], Literal[False]]:
#     try:
#         result = await resolver.query(f'_minecraft._tcp.{domain}', 'SRV')
#         return result[0].host, result[0].port
#     except DNSError:
#         return False, False
