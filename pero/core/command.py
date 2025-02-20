"""从文本中解析出命令和参数"""

import re
from typing import List, Optional, Tuple


class CommandParser:
    def __init__(self):
        # 修改正则表达式，支持中文字符
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_\u4e00-\u9fa5]+)(?:\s+(.*))?$")

    @classmethod
    async def parse(cls, input_list: List[str]) -> List[Optional[Tuple[str, List[str]]]]:
        """
        解析输入的命令列表，并返回命令和多个参数（列表形式）
        """
        result = []

        for input_str in input_list:
            match = cls.command_pattern.match(input_str)
            if match:
                name = match.group(1)  # 提取命令部分
                argv_str = match.group(2) if match.group(2) else ""  # 提取参数部分
                # 使用空格和中英文逗号将参数字符串分割为列表
                argv = re.split(r"[,\s，]+", argv_str) if argv_str else []
                result.append((name, argv))
            else:
                result.append(None)

        return result
