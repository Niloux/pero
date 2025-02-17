from typing import Any, Dict, List, Optional

from pero.cmd.command_parser import Command, command_parser
from pero.core.common import At, Image, MessageElement, Text


class Message:
    def __init__(self):
        self.sender: Optional[str] = None
        self.source: Optional[str] = None
        self.reply: Optional[str] = None
        self.target: Optional[str] = None
        self.content: Dict[str, MessageElement] = {}
        self.types: List[str] = []
        self.command: Optional[Command] = None

    def get_text(self) -> str:
        return self.content.get("text").text


class MessageParser:
    """消息解析器类"""

    async def parse(self, event: Dict[str, Any]) -> Message:
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
        if "text" in message.content and message.content["text"].text:
            message.command = await command_parser.parse(message.content["text"].text)

        return message


message_parser = MessageParser()
