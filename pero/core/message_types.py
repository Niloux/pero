"""消息类型"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional


@dataclass
class MessageElement(ABC):
    """消息元素的基类"""

    type: str = None

    @abstractmethod
    def to_dict(self) -> Dict[str, Any]:
        """将消息元素转换为字典格式"""
        pass

    @classmethod
    @abstractmethod
    def from_dict(cls, data: Dict[str, Any]) -> "MessageElement":
        """从字典格式创建消息元素"""
        pass


@dataclass
class Text(MessageElement):
    """文本消息元素"""

    text: str
    type: str = "text"

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "data": {"text": self.text}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Text":
        return cls(data.get("data", {}).get("text", ""))


@dataclass
class At(MessageElement):
    """@ 消息元素"""

    qq: str
    type: str = "at"

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "data": {"qq": self.qq}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "At":
        return cls(data.get("data", {}).get("qq", ""))


@dataclass
class Image(MessageElement):
    """图片消息元素"""

    url: str
    file_id: Optional[str] = None
    type: str = "image"

    def to_dict(self) -> Dict[str, Any]:
        return {"type": self.type, "data": {"url": self.url, "file_id": self.file_id}}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Image":
        data_dict = data.get("data", {})
        return cls(url=data_dict.get("url", ""), file_id=data_dict.get("file_id"))


# ... 其他消息元素类 ...
