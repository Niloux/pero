import re
from typing import Any, Dict, List, Optional

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


class Command:
    def __init__(self, name: str, argv: List[str]):
        self.name = name
        self.argv = argv  # 参数列表


class CommandParser:
    def __init__(self):
        # 修改正则表达式，支持中文字符
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_\u4e00-\u9fa5]+)(?:\s+(.*))?$")

    @classmethod
    async def parse(cls, input_str: str) -> Optional[Command]:
        """
        解析输入的命令字符串，并返回命令和多个参数（列表形式）
        """
        command_pattern = re.compile(r"^/([a-zA-Z0-9_\u4e00-\u9fa5]+)(?:\s+(.*))?$")
        match = command_pattern.match(input_str)
        if match:
            name = match.group(1)  # 提取命令部分
            argv_str = match.group(2) if match.group(2) else ""  # 提取参数部分
            # 使用空格和中英文逗号将参数字符串分割为列表
            argv = re.split(r"[,\s，]+", argv_str) if argv_str else []
            return Command(name, argv)
        else:
            return None
