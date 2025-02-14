from pero.cmd.command_manager import command_manager
from pero.utils.logger import logger


class CommandRegistry(type):
    def __init__(cls, name, bases, attrs):
        if hasattr(cls, "command_name") and cls.command_name:
            if cls.command_name not in command_manager.commands:
                command_manager.register(cls.command_name, cls)
                logger.info(f"Auto-registered command: {cls.command_name}")
