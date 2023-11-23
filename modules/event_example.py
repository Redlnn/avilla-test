from avilla.core import Context, MessageReceived
from avilla.standard.core.activity.event import ActivityTrigged
from graia.saya import Channel
from graiax.shortcut.saya import listen
from loguru import logger

# for ruff
# ruff: noqa: F841

channel = Channel.current()


# 各种普通消息接收
@listen(MessageReceived)
async def main1(ctx: Context, event: MessageReceived):
    logger.debug(event)
    logger.debug(ctx.client)  # sender (member / friend )
    logger.debug(ctx.endpoint)  # group / friend
    logger.debug(ctx.scene)  # group / friend
    logger.debug(ctx.self)  # bot


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
