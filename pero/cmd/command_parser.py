import re
from typing import Optional, Tuple


class CommandParser:
    def __init__(self):
        # 定义一个正则表达式来匹配"/cmd"命令格式
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_]+)(?:\s+(.*))?$")

    async def parse(self, input_str: str) -> Tuple[Optional[str], str]:
        """
        解析输入的命令字符串，并返回命令和文本
        """
        match = self.command_pattern.match(input_str)
        if match:
            command = match.group(1)  # 提取命令部分
            text = match.group(2) if match.group(2) else ""  # 提取文本部分（如果有）
            return command, text
        else:
            return None, None
