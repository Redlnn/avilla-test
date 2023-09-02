import traceback
from io import StringIO

import kayaku
from avilla.core.application import Avilla
from avilla.core.elements import Picture, Text
from avilla.core.resource import RawResource
from avilla.core.selector import Selector
from avilla.standard.core.message import MessageSend
from graia.amnesia.message.chain import MessageChain
from graia.broadcast.builtin.event import ExceptionThrowed
from graia.saya import Channel
from graiax.shortcut.saya import listen

from libs.config import BasicConfig
from libs.text2img import md2img

channel = Channel.current()


@listen(ExceptionThrowed)
async def except_handle(event: ExceptionThrowed):
    if isinstance(event.event, ExceptionThrowed):
        return
    with StringIO() as fp:
        traceback.print_tb(event.exception.__traceback__, file=fp)
        tb = fp.getvalue()
    msg = f'''\
## 异常事件：

`{str(event.event.__repr__())}`

## 异常类型：

`{type(event.exception)}`

## 异常内容：

{str(event.exception)}

## 异常追踪：

```py
{tb}
```
'''
    img_bytes = await md2img(msg, 1500)
    message = MessageChain([Text('发生异常\n'), Picture(RawResource(img_bytes))])
    account = next(
        (v.account for k, v in Avilla.current().accounts.items() if k.pattern['land'] == 'qq'),
        None,
    )
    if account is None:
        return
    basic_cfg = kayaku.create(BasicConfig, flush=True)
    await account.staff.call_fn(
        MessageSend.send,
        Selector().land('qq').friend(str(basic_cfg.admin.masterId)),
        message,
    )
