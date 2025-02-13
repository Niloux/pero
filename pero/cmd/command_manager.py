from typing import Dict

from pero.api import PERO_API
from pero.cmd.command_parser import CommandParser


class CommandManager:
    def __init__(self):
        # 存储注册的命令和对应的命令类
        self.commands = {}

    def register(self, command_name: str, command_class):
        """注册命令到命令管理器"""
        self.commands[command_name] = command_class

    async def execute(self, event: Dict) -> bool:
        """根据命令解析执行对应的命令"""
        # 从 event 中提取文本并解析命令
        text = await self._extract_text(event)
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
