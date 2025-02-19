"""弃用"""

from pero.cmd.command_base import BaseCommand


class ByeCommand(BaseCommand):
    command_name = "bye"

    async def execute(self) -> str:
        return "Goodbye, world!"


class HelloCommand(BaseCommand):
    command_name = "hello"

    async def execute(self) -> str:
        return "Hello, world!"
