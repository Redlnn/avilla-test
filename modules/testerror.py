from avilla.core import Context, MessageReceived
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema

channel = Channel.current()


@channel.use(ListenerSchema(listening_events=[MessageReceived]))
async def main(ctx: Context, event: MessageReceived):
    if str(event.message.content) != '/testerror':
        return
    raise ValueError('test')
