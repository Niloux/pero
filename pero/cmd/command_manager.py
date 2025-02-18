import importlib.util
import os
from typing import Any, Dict, Tuple

from pero.core.api import PERO_API as pero
from pero.core.message_parser import Message
from pero.utils.logger import logger


class CommandManager:
    def __init__(self):
        # 存储注册的命令和对应的命令类
        self.commands = {}

    def register(self, command_name: str, command_class):
        """注册命令到命令管理器"""
        if command_name not in self.commands:
            self.commands[command_name] = command_class

    def load_commands(self, commands_directory: str):
        """动态加载命令目录中的所有命令"""
        loaded_files = set()
        for filename in os.listdir(commands_directory):
            if filename.endswith(".py") and not filename.startswith("__"):
                module_name = filename[:-3]
                module_path = os.path.join(commands_directory, filename)
                if module_path in loaded_files:
                    continue
                spec = importlib.util.spec_from_file_location(module_name, module_path)
                module = importlib.util.module_from_spec(spec)
                spec.loader.exec_module(module)
                loaded_files.add(module_path)

    async def execute(self, message: Message) -> Any:
        """根据命令解析执行对应的命令"""
        command = message.command
        logger.info(f"接收到命令: {command.name} {command.argv}")

        # 如果命令注册表中存在该命令，则执行对应命令
        if command.name in self.commands:
            # 创建命令实例并执行
            command_class = self.commands[command.name]
            command_instance = command_class(command.name, command.argv)
            response = await command_instance.execute()
            # 回显响应
            return await self._send_response(message, response)
        else:
            # 如果命令不存在，则返回无效命令响应
            return await self._send_response(message, f"{command.name}命令无效喵！")

    async def _send_response(self, message: Message, response: str) -> Tuple[str, Dict]:
        """根据event中的类型发送回复"""
        if message.source == "private":
            return await pero.post_private_msg(user_id=message.target, text=response)
        elif message.source == "group":
            return await pero.post_group_msg(group_id=message.target, text=response)


# 创建 CommandManager 实例
command_manager = CommandManager()
