from avilla.core import Context, MessageReceived
from graia.saya import Channel
from graia.saya.builtins.broadcast.schema import ListenerSchema
from graiax.shortcut.saya import listen
from launart import Launart
from loguru import logger
from sqlalchemy.sql import select

from libs.database.interface import Database

from .model import Test

channel = Channel.current()


@listen(MessageReceived)
async def main(ctx: Context, event: MessageReceived):
    if str(event.message.content) != '/testdb':
        return

    logger.info('get mgr')
    launart = Launart.current()
    logger.info('get db')
    db = launart.get_interface(Database)

    # logger.info('write')
    # await ctx.scene.send_message('write')
    # await db.add(Test(qq=1846913566, sex=0))
    logger.info('select')
    # await ctx.scene.send_message('select')
    result: Test | None = await db.select_first(select(Test))
    logger.info(f'result: {result}')
    # await ctx.scene.send_message(f'result: {result}')
