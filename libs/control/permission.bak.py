import kayaku
from avilla.core.context import Context
from avilla.standard.core.privilege import Privilege
from graia.broadcast import ExecutionStop
from graia.broadcast.builtin.decorators import Depend

from libs.config import BasicConfig


class GroupPermission:
    """
    用于管理权限的类，不应被实例化

    适用于群消息和来自群的临时会话
    """

    BOT_MASTER: int = 100  # Bot主人
    BOT_ADMIN: int = 90  # Bot管理员
    OWNER: int = 30  # 群主
    ADMIN: int = 20  # 群管理员
    USER: int = 10  # 群成员/好友
    BANED: int = 0  # Bot黑名单成员
    DEFAULT: int = USER

    @classmethod
    async def get(cls, ctx: Context):
        """
        获取用户的权限等级

        :param target: Friend 或 Member 实例
        :return: 等级，整数
        """
        basic_cfg = kayaku.create(BasicConfig, flush=True)
        if int(ctx.client.last_value) == basic_cfg.admin.masterId:
            return cls.BOT_MASTER
        if int(ctx.client.last_value) in basic_cfg.admin.admins:
            return cls.BOT_ADMIN
        if ctx.scene.follows('::group.*'):
            # privilege_info.available  # 对象是否持有特权
            # privilege_info.effective  # 自身对对象是否可以产生影响，通常情况下这也表示自身的特权超越对方
            # 判断群主
            privilege_info = await ctx.client.pull(Privilege >> Privilege)
            if privilege_info.available:
                ...
            # 判断群管
            privilege_info = await ctx.client.pull(Privilege)
            if privilege_info.available:
                ...
            else:
                ...
        if ctx.scene.follows('::channel.*'):
            ...
            # 通过身份组判断
            ## 判断频道主
            ## 判断超级管理员
            ## 判断分组管理员（成员分组）
            ## 判断子频道管理员

            # 通过manage\speak\read等权限判断 avilla/qqapi/const.py
        else:
            return cls.DEFAULT

    @classmethod
    def require(
        cls,
        perm: int = 0,
        send_alert: bool = True,
        alert_text: str = '你没有权限执行此指令',
    ) -> Depend:
        """
        群消息权限检查

        指示需要 `level` 以上等级才能触发

        :param perm: 至少需要什么权限才能调用
        :param send_alert: 是否发送无权限消息
        :param alert_text: 无权限提示的消息内容
        """

        async def wrapper(ctx: Context):
            if ctx.scene.follows('::group.*'):
                ...
            if ctx.scene.follows('::channel.*'):
                ...
            # if isinstance(perm, MemberPerm):
            #     target = cls._levels[perm]
            # elif isinstance(perm, int):
            #     target = perm
            # else:
            #     raise ValueError('perm 参数类型错误')
            # if (await cls.get(member)) < target:
            #     if send_alert:
            #         await app.send_message(group, MessageChain(At(member.id), Plain(f' {alert_text}')))
            #     raise ExecutionStop()

        return Depend(wrapper)
