"""
搜索我的世界中文Wiki

用法：在群内发送【!wiki {关键词}】即可
"""

from asyncio.exceptions import TimeoutError
from urllib.parse import quote

from avilla.core import Context, MessageReceived
from avilla.twilight.twilight import RegexMatch, RegexResult, SpacePolicy, Twilight
from graia.saya import Channel
from graiax.shortcut.saya import dispatch, listen
from launart import Launart
from selectolax.parser import HTMLParser

from libs.aiohttp_service import AiohttpClientInterface

channel = Channel.current()

channel.meta['name'] = '我的世界中文Wiki搜索'
channel.meta['author'] = ['Red_lnn']
channel.meta['description'] = '[!！.]wiki <要搜索的关键词>'


@listen(MessageReceived)
@dispatch(Twilight(RegexMatch(r'[!！.]wiki').space(SpacePolicy.FORCE), 'keyword' @ RegexMatch(r'\S+')))
async def main(ctx: Context, keyword: RegexResult):
    if keyword.result is None:
        return
    key_word: str = str(keyword.result).strip()
    search_parm: str = quote(key_word, encoding='utf-8')

    bili_search_url = f'https://searchwiki.biligame.com/mc/index.php?search={search_parm}'
    fandom_search_url = f'https://minecraft.fandom.com/zh/index.php?search={search_parm}'

    bili_url = f'https://wiki.biligame.com/mc/{search_parm}'
    fandom_url = f'https://minecraft.fandom.com/zh/wiki/{search_parm}?variant=zh-cn'

    launart = Launart.current()
    session = launart.get_interface(AiohttpClientInterface).service.session
    try:
        async with session.get(bili_url) as resp:
            status_code = resp.status
            text = await resp.text()
    except TimeoutError:
        status_code = -1
        text = ''

    match status_code:
        case 404:
            msg = (
                f'Minecraft Wiki 没有名为【{key_word}】的页面，'
                '要继续搜索请点击下面的链接：\n'
                f'Bilibili 镜像: {bili_search_url}\n'
                f'Fandom: {fandom_search_url}'
            )
        case 200:
            tree = HTMLParser(text)
            title = tree.css_first('html head title').text()
            introduction_list = tree.css('p:has(~ .toc)')
            introduction = '\n'.join(_.text().strip() for _ in introduction_list)
            msg = f'{title}\n\n{introduction}\n\nBilibili 镜像: {bili_url}\nFandom: {fandom_url}'
        case _:
            msg = (
                f'无法查询 Minecraft Wiki，错误代码：{status_code}\n'
                f'要继续搜索【{key_word}】请点击下面的链接：\n'
                f'Bilibili 镜像: {bili_search_url}\n'
                f'Fandom: {fandom_search_url}'
            )

    await ctx.scene.send_message(msg)
