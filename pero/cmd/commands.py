from pero.cmd.command_base import Command
from pero.cmd.command_registry import CommandRegistry


class BaseCommand(Command, metaclass=CommandRegistry):
    command_name = None


class HelloCommand(BaseCommand):
    command_name = "hello"

    async def execute(self) -> str:
        return "Hello, world!"


class ByeCommand(BaseCommand):
    command_name = "bye"

    async def execute(self) -> str:
        return "Goodbye, world!"
