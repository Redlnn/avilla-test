from avilla.core import Context, MessageReceived
from avilla.elizabeth.perform.event.activity import ElizabethEventActivityPerform
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


@listen(ActivityTrigged)
async def main2(event: ActivityTrigged):
    ctx = event.context
    logger.debug(event)

    # NudgeEvent 戳一戳消息
    if event.activity.follows('::group.member.activity(nudge).*'):
        logger.debug(event.context.client)  # sender
        logger.debug(event.context.endpoint)  # target
        logger.debug(event.context.scene)  # group
        logger.debug(event.context.self)  # bot
