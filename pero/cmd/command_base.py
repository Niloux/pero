from pero.cmd.command_registry import CommandRegistry


class BaseCommand(metaclass=CommandRegistry):
    command_name = None

    def __init__(self, name, text):
        self.name = name
        self.text = text

    async def execute(self):
        raise NotImplementedError("Subclasses must implement this method")
