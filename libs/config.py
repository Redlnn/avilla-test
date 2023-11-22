from dataclasses import dataclass, field

from kayaku import config


@dataclass
class MAHConfig:
    enabled: bool = False
    account: int = 123456789
    """Mirai Api Http 已登录的账号"""
    host: str = 'localhost'
    """Mirai Api Http 地址"""
    port: int = 8080
    """Mirai Api Http 端口"""
    verifyKey: str = 'VerifyKey'
    """Mirai Api Http 的 verifyKey"""


@dataclass
class QQAPIConfig:
    enabled: bool = False
    id: str = '123456789'
    """机器人ID"""
    token: str = 'xxx'
    secret: str = 'xxx'
    isSandbox: bool = False
    """是否是沙箱环境"""


@dataclass
class AdminConfig:
    masterId: int = 731347477
    """机器人主人的QQ号"""
    masterName: str = 'Red_lnn'
    """机器人主人的称呼"""
    admins: list[int] = field(default_factory=lambda: [731347477])
    """机器人管理员列表"""


@config('redbot')
class BasicConfig:
    botName: str = 'RedBot'
    """机器人的名字"""
    logChat: bool = True
    """是否将聊天信息打印在日志中"""
    debug: bool = False
    """是否启用调试模式"""
    databaseUrl: str = 'sqlite+aiosqlite:///data/database.db'
    """数据库地址

    MySQL示例：mysql+asyncmy://user:pass@hostname/dbname?charset=utf8mb4
    """
    miraiApiHttp: MAHConfig = field(default_factory=lambda: MAHConfig())
    """Mirai Api Http 配置"""
    qqAPI: QQAPIConfig = field(default_factory=lambda: QQAPIConfig())
    """QQ官方API配置"""
    admin: AdminConfig = field(default_factory=lambda: AdminConfig())
    """机器人管理相关配置"""


@dataclass
class guildDisabled:
    guildID: str
    """频道ID"""
    globalDisabled: bool = False
    """在所有子频道停用"""
    disabledSubchannel: list[str] = field(default_factory=lambda: [])
    """要停用的子频道"""


@config('modules')
class ModulesConfig:
    enabled: bool = True
    """是否允许加载模块"""
    globalDisabledModules: list[str] = field(default_factory=lambda: [])
    """全局禁用的模块列表"""
    disabledGroups: dict[str, list[str]] = field(default_factory=lambda: dict())
    """分群禁用模块的列表，列表内为群号（`{模块名称: [123456789,]}`）"""
    disabledGuilds: dict[str, list[guildDisabled]] = field(default_factory=lambda: dict())
    """分频道禁用模块的列表
    （`{模块名称: [{guildID: 123, globalDisabled: true, disabledSubchannel: [123456789,]},]}`）"""


@config('permission')
class PermConfig:
    whitelistEndbled: bool = False
    whitelist: list[int] = field(default_factory=lambda: [])
    """白名单群组/频道列表"""
    usersBlacklist: list[str] = field(default_factory=lambda: [])
    """用户黑名单列表"""
