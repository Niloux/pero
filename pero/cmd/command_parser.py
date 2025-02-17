import re


class Command:
    def __init__(self, name: str, argv: list):
        self.name = name
        self.argv = argv  # 参数列表


class CommandParser:
    def __init__(self):
        # 修改正则表达式，支持中文字符
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_\u4e00-\u9fa5]+)(?:\s+(.*))?$")

    async def parse(self, input_str: str) -> Command:
        """
        解析输入的命令字符串，并返回命令和多个参数（列表形式）
        """
        match = self.command_pattern.match(input_str)
        if match:
            name = match.group(1)  # 提取命令部分
            argv_str = match.group(2) if match.group(2) else ""  # 提取参数部分
            # 使用空格将参数字符串分割为列表
            argv = argv_str.split() if argv_str else []
            return Command(name, argv)
        else:
            return None


command_parser = CommandParser()
