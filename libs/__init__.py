from importlib import metadata

from graia.broadcast import Broadcast


def get_graia_version():
    extra: list[tuple[str, str]] = []
    official: list[tuple[str, str]] = []
    community: list[tuple[str, str]] = []

    for dist in metadata.distributions():
        name: str = dist.metadata['Name']
        version: str = dist.version
        if name in {'launart', 'creart', 'creart-graia', 'statv', 'richuru'}:
            extra.append((name, version))
        elif name.startswith('graia-'):
            official.append((name, version))
        elif name.startswith('graiax-'):
            community.append((name, version))

    return extra, official, community


def get_version(prefix: str):
    packages: list[tuple[str, str]] = []

    for dist in metadata.distributions():
        name: str = dist.metadata['Name']
        if name.startswith(prefix):
            packages.append((name, dist.version))

    return packages


def inject_bypass_listener(broadcast: Broadcast):
    """注入 BypassListener 以享受子事件解析.

    Args:
        broadcast (Broadcast): 外部事件系统, 提供了 event_class_generator 方法以生成子事件.
    """

    from collections.abc import Callable

    from graia.broadcast.entities.decorator import Decorator
    from graia.broadcast.entities.event import Dispatchable
    from graia.broadcast.entities.listener import Listener
    from graia.broadcast.entities.namespace import Namespace
    from graia.broadcast.typing import T_Dispatcher

    class BypassListener(Listener):
        """透传监听器的实现"""

        def __init__(
            self,
            callable: Callable,
            namespace: Namespace,
            listening_events: list[type[Dispatchable]],
            inline_dispatchers: list[T_Dispatcher] | None = None,
            decorators: list[Decorator] | None = None,
            priority: int = 16,
        ) -> None:
            events = []
            for event in listening_events:
                events.append(event)
                events.extend(broadcast.event_class_generator(event))
            super().__init__(
                callable,
                namespace,
                events,
                inline_dispatchers=inline_dispatchers or [],
                decorators=decorators or [],
                priority=priority,
            )

    import creart
    import graia.broadcast.entities.listener

    graia.broadcast.entities.listener.Listener = BypassListener  # type: ignore
    graia.broadcast.Listener = BypassListener  # type: ignore

    if creart.exists_module("graia.saya"):
        import graia.saya.builtins.broadcast.schema

        graia.saya.builtins.broadcast.schema.Listener = BypassListener  # type: ignore
