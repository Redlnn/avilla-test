"""
用法：

在本Bot账号所在的任一一QQ群中发送 `!roll` 或 `!roll {任意字符}` 均可触发本插件功能
触发后会回复一个由0至100之间的任一随机整数
"""

from random import randint

from avilla.core import Context, MessageReceived
from avilla.core.message import Message
from avilla.standard.qq.elements import Dice
from avilla.twilight.twilight import RegexMatch, RegexResult, Twilight, WildcardMatch
from graia.amnesia.message.chain import MessageChain
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen

channel = Channel.current()

channel.meta['name'] = '随机数'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '获得一个随机数\n用法：\n  [!！.]roll {要roll的事件}\n  [!！.](dice|骰子|色子)'


@listen(MessageReceived)
@dispatch(Twilight(RegexMatch(r'[!！.]roll'), 'target' @ WildcardMatch()))
async def roll(ctx: Context, message: Message, target: RegexResult):
    if target.result is None:
        return
    t = str(target.result).strip()
    chain = f'{t}的概率为：{randint(0, 100)}%' if t else str(randint(0, 100))
    await ctx.scene.send_message(chain, reply=message)


@listen(MessageReceived)
@dispatch(Twilight(RegexMatch(r'[!！.](dice|骰子|色子)')))
async def dice(ctx: Context):
    await ctx.scene.send_message(MessageChain([Dice(randint(1, 6))]))
