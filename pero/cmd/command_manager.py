import re
from typing import Dict

from pero.api import PERO_API
from pero.cmd.commander import Command
from pero.utils.logger import logger


class CommandParser:
    def __init__(self):
        # 定义一个正则表达式来匹配"/cmd"命令格式
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_]+)(?:\s+(.*))?$")

    async def parse(self, input_str: str):
        """
        解析输入的命令字符串，并返回命令和文本
        """
        match = self.command_pattern.match(input_str)
        if match:
            command = match.group(1)  # 提取命令部分
            text = match.group(2) if match.group(2) else ""  # 提取文本部分（如果有）
            return command, text
        else:
            # raise ValueError("无效的命令格式喵！请确保是以 /cmd 开头并后跟空格的文本。")
            return None, ""


class CommandManager:
    def __init__(self):
        # 存储注册的命令和对应的命令类
        self.commands = {}

    def register(self, command_name: str, command_class: Command):
        """注册命令到命令管理器"""
        self.commands[command_name] = command_class
        logger.info(f"register cmd: {command_name}--{command_class}")

    async def execute(self, event: Dict) -> bool:
        """根据命令解析执行对应的命令"""
        # 从 event 中提取文本并解析命令
        text = await self._extract_text(event)
        try:
            command_parser = CommandParser()
            command_name, command_text = await command_parser.parse(text)

            # 非命令文本，则不执行
            if not command_name:
                return False

            # 如果命令注册表中存在该命令，则执行对应命令
            if command_name in self.commands:
                # 创建命令实例并执行
                command_class = self.commands[command_name]
                command_instance = command_class(command_name, command_text)
                response = await command_instance.execute()
                # 回显响应
                await self._send_response(event, response)
            else:
                # 如果命令不存在，则返回无效命令响应
                await self._send_response(event, f"{command_name}命令无效喵！")
                return False
        except ValueError:
            # 命令格式错误
            await self._send_response(
                event, f"{command_name}无效的命令格式喵！请确保命令格式正确。"
            )
            return False

    async def _extract_text(self, event: Dict) -> str:
        """从 event 中提取文本消息"""
        for content in event.get("content", []):
            if content.get("type") == "text":
                return content.get("data", {}).get("text", "")
        return ""

    async def _send_response(self, event: Dict, message: str):
        """根据event中的类型发送回复"""
        if event.get("source_type") == "private":
            return await PERO_API.post_private_msg(
                user_id=event.get("target"), text=message
            )
        elif event.get("source_type") == "group":
            return await PERO_API.post_group_msg(
                group_id=event.get("target"), text=message
            )


# 创建 CommandManager 实例
command_manager = CommandManager()


def register_command(command_name: str):
    """装饰器：自动注册命令"""

    def decorator(command_class):
        command_manager.register(command_name, command_class)
        return command_class

    return decorator
