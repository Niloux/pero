from enum import Enum


class Meta(str, Enum):
    ENABLE = "lifecycle_enable"
    DISABLE = "lifecycle_disable"
    CONNECT = "lifecycle_connect"
    HEARTBEAT = "heartbeat"


class Message(str, Enum):
    FRIEND = "private_friend"
    GROUP = "private_group"
    GROUP_SELF = "private_group_self"
    OTHER = "private_other"
    NORMAL = "group_normal"
    ANONYMOUS = "group_anonymous"
    NOTICE = "group_notice"


class Request(str, Enum):
    FRIEND = "friend"
    ADD = "group_add"
    INVITE = "group_invite"


class Notice(str, Enum):
    # TODO, 有什么需求就加什么类型
    pass


class EventType:
    META = Meta
    MESSAGE = Message
    REQUEST = Request
    NOTICE = Notice


class MessageType(str, Enum):
    TEXT = "TEXT"
    FACE = "FACE"
    IMAGE = "IMAGE"
    RECORD = "RECORD"
    VIDEO = "VIDEO"
    MUSIC = "MUSIC"
    AT = "AT"
    RPS = "RPS"
    FILE = "FILE"
    DICE = "DICE"
    SHAKE = "SHAKE"
    POKE = "POKE"
    SHARE = "SHARE"
    LOCATION = "LOCATION"
    CONTACT = "CONTACT"
    IMPRESSION = "IMPRESSION"
    REPLY = "REPLY"
    FORWARD = "FORWARD"
    NODE = "NODE"
    JSON = "JSON"
    MFACE = "MFACE"
    MARKDOWN = "MARKDOWN"
    LIGHTAPP = "LIGHTAPP"
