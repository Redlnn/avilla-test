from arclet.alconna import Alconna, Arg, Args, CommandMeta, Option, OptionResult
from arclet.alconna.graia import AlconnaDispatcher
from avilla.core import Context, Message, MessageReceived
from avilla.core.elements import Notice
from avilla.standard.core.activity.event import ActivityTrigged
from graia.saya import Channel
from graia.scheduler.saya.schema import SchedulerSchema
from graia.scheduler.timers import every_second
from graiax.shortcut.saya import dispatch, listen
from loguru import logger

# for ruff
# ruff: noqa: F841

channel = Channel.current()


@channel.use(SchedulerSchema(every_second()))
async def work_scheduled(ctx: Context) -> None:
    print(ctx)
    logger.info('早安！')


# 各种普通消息接收
@listen(MessageReceived)
async def main1(ctx: Context, event: MessageReceived, msg: Message):
    logger.debug(event)
    logger.debug(ctx.client)  # sender (member / friend )
    logger.debug(ctx.endpoint)  # group / friend
    logger.debug(ctx.scene)  # group / friend
    logger.debug(ctx.self)  # bot
    logger.debug(msg)  # message
    logger.debug(msg.content.copy())  # message


@listen(ActivityTrigged)
async def main2(event: ActivityTrigged):
    ctx = event.context
    logger.debug(event)

    # NudgeEvent 戳一戳消息
    if event.id == 'nudge':
        logger.debug(event.id)  # "nudge"
        logger.debug(event.scene)  # == ctx.scene  所在群组/好友
        logger.debug(event.activity)  # == ctx.client.nudge(raw_event["action"])  动作
        logger.debug(event.trigger)  # == ctx.client  发送者
        logger.debug(ctx.client)  # sender (group / friend)
        logger.debug(ctx.endpoint)  # target
        logger.debug(ctx.scene)  # group / friend
        logger.debug(ctx.self)  # bot


# Alc 测试
# @listen(MessageReceived)
# @dispatch(AlconnaDispatcher(Alconna('/测试'), remove_tome=True))
# async def main3(msg: Message, event: MessageReceived):
#     logger.debug(msg)
#     logger.debug(event)
