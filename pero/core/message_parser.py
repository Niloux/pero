from typing import Any, Dict, List, Optional

from pero.cmd.command_parser import Command, CommandParser
from pero.core.message import At, Image, MessageElement, Text


class Message:
    def __init__(self):
        self.sender: Optional[str] = None
        self.source: Optional[str] = None
        self.reply: Optional[str] = None
        self.target: Optional[str] = None
        self.content: Dict[str, MessageElement] = {}
        self.types: List[str] = []
        self.command: Optional[Command] = None

    def __str__(self) -> str:
        content_str = "\n".join([f"{key}: {value.to_dict()}" for key, value in self.content.items()])
        return (
            f"Message(\n"
            f"  sender: {self.sender},\n"
            f"  source: {self.source},\n"
            f"  reply: {self.reply},\n"
            f"  target: {self.target},\n"
            f"  content: {{\n{content_str}\n  }},\n"
            f"  types: {self.types},\n"
            f"  command: {self.command}\n"
            f")"
        )

    def get_text(self) -> str:
        return self.content.get("text").text


class MessageParser:
    """消息解析器类"""

    @classmethod
    async def parse(cls, event: Dict[str, Any]) -> Message:
        message = Message()
        """解析消息"""
        # 解析content内容
        content = event.get("content", [])
        for i in content:
            if i.get("type") == "text":
                message.content["text"] = Text.from_dict(i)
                message.types.append("text")
            elif i.get("type") == "at":
                message.content["at"] = At.from_dict(i)
                message.types.append("at")
            elif i.get("type") == "image":
                message.content["image"] = Image.from_dict(i)
                message.types.append("image")
        if message.types:
            message.types = sorted(message.types)
        # 解析必要项
        message.sender = event.get("sender")
        message.source = event.get("source")
        message.reply = event.get("reply")
        message.target = event.get("target")
        # 解析指令
        if "text" in message.types and message.get_text():
            # 当content中有多条内容时，比如@机器人 + 指令，此时不会被解析为指令
            # 本来以为出现了bug，后来才发现get_text()的str中有空格，所以指令解析失败
            # 误打误撞了属于是💧
            message.command = await CommandParser.parse(message.get_text())

        return message
