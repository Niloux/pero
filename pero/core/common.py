"""发布订阅的通用消息结构"""

from dataclasses import dataclass
from datetime import datetime
from enum import Enum, auto
from typing import Any, Dict, Generic, List, Tuple, TypeVar

from pero.core.message_types import Text

T = TypeVar("T")


class MessagePriority(Enum):
    """消息优先级"""

    LOW = auto()
    NORMAL = auto()
    HIGH = auto()


@dataclass
class Message(Generic[T]):
    """消息封装类"""

    topic: str
    data: T
    priority: MessagePriority = MessagePriority.NORMAL
    timestamp: datetime = None

    def __post_init__(self):
        self.timestamp = datetime.now()


@dataclass
class _Message:
    """event_type为message的消息封装类"""

    type: str  # 二级topic节点
    sub_type: str  # 三级topic节点
    sender: Dict[str, Any]  # 发送者信息
    content: List[Any]  # 内容列表，包括Text, At, Imgae, Video等
    content_types: List[str]  # 内容类型列表
    id: int  # 该条message的唯一标识
    target: int  # 消息接收者
    has_cmd: bool = False  # 是否包含命令
    command: Tuple[str, List[str]]  # 命令和命令参数

    def get_text(self) -> str:
        """获取消息内容中的Text部分"""
        for i in self.content:
            if isinstance(i, Text):
                return i.text
        return ""


@dataclass
class _Meta:
    """event_type为meta_event的消息封装类"""

    type: str
    sub_type: str
    time: int  # 时间戳
    status: Dict[str, Any] = None  # 心跳包状态信息


@dataclass
class _Status:
    """event_type为status的消息封装类"""

    type: str
    sub_type: str
    id: int
    wording: str  # napcat响应信息
