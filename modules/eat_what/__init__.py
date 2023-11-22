import random
from pathlib import Path

from aiofile import async_open
from avilla.core import Context, MessageReceived
from avilla.twilight.twilight import RegexMatch, SpacePolicy, Twilight
from graia.saya import Channel
from graiax.shortcut.saya import decorate, dispatch, listen

from libs.control import require_disable

channel = Channel.current()

channel.meta['name'] = '吃啥'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '[!！.]吃[啥咩]'


async def get_food():
    async with async_open(Path(Path(__file__).parent, 'foods.txt')) as afp:
        foods = await afp.read()
    return random.choice(foods.strip().split('\n'))


@listen(MessageReceived)
@dispatch(Twilight(RegexMatch(r'[!！.]吃啥').space(SpacePolicy.NOSPACE)))
# @decorate(require_disable(channel.module))
# @decorate(GroupPermission.require(), require_disable(channel.module))
async def main(ctx: Context, event: MessageReceived):
    food = await get_food()
    await ctx.scene.send_message(f'吃{food}', reply=event.message)
