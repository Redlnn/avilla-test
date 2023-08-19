from avilla.core import Context, MessageReceived
from graia.saya import Channel
from graiax.shortcut.saya import listen

channel = Channel.current()


@listen(MessageReceived)
async def main(ctx: Context, event: MessageReceived):
    if str(event.message.content) != '/testerror':
        return
    raise ValueError('test')
