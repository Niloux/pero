import re
from typing import Dict

from pero.api import BotAPI


async def send_response(event: Dict, api: BotAPI, message: str):
    """发送回显消息"""
    if event.get("source_type") == "private":
        await api.post_private_msg(user_id=event.get("target"), text=message)
    elif event.get("source_type") == "group":
        await api.post_group_msg(group_id=event.get("target"), text=message)


def extract_text(event: Dict) -> str:
    """从event中提取text消息"""
    for content in event.get("content", []):
        if content.get("type") == "text":
            return content.get("data", {}).get("text", "")
    return ""


class CommandParser:
    def __init__(self):
        # 定义一个正则表达式来匹配"/cmd"命令格式
        self.command_pattern = re.compile(r"^/([a-zA-Z0-9_]+)(?:\s+(.*))?$")

    def parse(self, input_str):
        """
        解析输入的命令字符串，并返回命令和文本
        """
        match = self.command_pattern.match(input_str)
        if match:
            command = match.group(1)  # 提取命令部分
            text = match.group(2) if match.group(2) else ""  # 提取文本部分（如果有）
            return command, text
        else:
            raise ValueError("无效的命令格式喵！请确保是以 /cmd 开头并后跟空格的文本。")


Parser = CommandParser()

# 测试用例
if __name__ == "__main__":
    parser = CommandParser()

    # 示例命令
    test_cases = [
        "/cmd hello",
        "/cmd greet world",
        "/cmd",
        "cmd hello",  # 错误命令，测试错误处理
    ]

    for case in test_cases:
        try:
            command, text = parser.parse(case)
            print(f"命令: {command}, 文本: {text}")
        except ValueError as e:
            print(e)
