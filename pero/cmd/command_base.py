class Command:
    """命令基类"""

    def __init__(self, command: str, text: str):
        self.command = command
        self.text = text

    async def execute(self) -> str:
        """命令执行的具体实现"""
        raise NotImplementedError
