"""弃用"""

from pero.cmd.command_registry import CommandRegistry


class BaseCommand(metaclass=CommandRegistry):
    command_name = None

    def __init__(self, name, argv):
        self.name = name
        self.argv = argv

    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")
