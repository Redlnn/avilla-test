import asyncio
import contextlib
import os
from pathlib import Path
from random import choice, randrange, uniform

import kayaku
from avilla.core.context import Context
from avilla.core.elements import Picture, Text
from avilla.core.exceptions import NetworkError, UnknownTarget
from avilla.standard.core.activity import ActivityTrigger
from avilla.standard.core.activity.event import ActivityTrigged
from graia.amnesia.message.chain import MessageChain
from graia.saya import Channel
from graiax.shortcut.saya import listen

from libs.config import BasicConfig
from libs.path import data_path

channel = Channel.current()

channel.meta['name'] = '别戳我'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '不要戳 Bot！（仅支持 QQ 平台）'

msg = (
    '别{}啦别{}啦，无论你再怎么{}，我也不会多说一句话的~',
    '你再{}！你再{}！你再{}试试！！',
    '那...那里...那里不能{}...绝对...绝对不能（小声）...',
    '那里不可以...',
    '怎么了怎么了？发生什么了？！纳尼？没事？没事你{}我干哈？',
    '气死我了！别{}了别{}了！再{}就坏了呜呜...┭┮﹏┭┮',
    '呜…别{}了…',
    '呜呜…受不了了',
    '别{}了！...把手拿开呜呜..',
    'hentai！八嘎！无路赛！',
    '変態！バカ！うるさい！',
    '。',
    '哼哼╯^╰',
)


async def get_message(event: ActivityTrigged):
    tmp = randrange(0, len(os.listdir(Path(data_path, 'Nudge'))) + len(msg))
    if tmp < len(msg):
        return MessageChain([Text(msg[tmp].replace('{}', event.activity['nudge'][0]))])
    if not Path(data_path, 'Nudge').exists():
        Path(data_path, 'Nudge').mkdir()
    elif len(os.listdir(Path(data_path, 'Nudge'))) == 0:
        return MessageChain([Text(choice(msg).replace('{}', event.activity['nudge'][0]))])
    return MessageChain([Picture(Path(data_path, 'Nudge', os.listdir(Path(data_path, 'Nudge'))[tmp - len(msg)]))])


@listen(ActivityTrigged)
# @decorate(require_disable(channel.module))
async def main(ctx: Context, event: ActivityTrigged):
    if event.id != 'nudge':
        return

    sender = ctx.client
    target = ctx.endpoint
    # group = ctx.scene
    # bot = ctx.self

    basic_cfg = kayaku.create(BasicConfig, flush=True)
    if target['member'] != str(basic_cfg.miraiApiHttp.account):
        return
    # elif not ManualInterval.require(f'{event.supplicant}_{event.target}', 3):
    #     return
    await asyncio.sleep(uniform(0.2, 0.6))
    with contextlib.suppress(UnknownTarget, NetworkError):
        await ctx[ActivityTrigger.trigger](sender.activity('nudge'))
        await asyncio.sleep(uniform(0.2, 0.6))
        if ctx.scene.follows('::group.*') or ctx.scene.follows('::friend.*'):
            await ctx.scene.send_message(await get_message(event))
