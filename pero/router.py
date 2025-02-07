import asyncio

from pero.logger import get_log
from pero.parse import parse
from pero.type import EventType, MessageType

_log = get_log()


class MessageRouter:
    def __init__(self):
        self.handlers = {}

    def register(
        self,
        event_type: EventType,
        message_type: MessageType,
    ):
        """装饰器: 将函数注册到路由表, type=None时表示不需要验证"""

        def decorator(func):
            key = (
                event_type,
                message_type,
            )
            self.handlers[key] = func
            _log.info(f"Register handler for {key}")
            return func

        return decorator

    def handle_message(self, message):
        (
            event_type,
            message_type,
        ) = parse(message)

        for (
            reg_event_type,
            reg_message_type,
        ), handler in self.handlers.items():
            if (reg_event_type == event_type) and (reg_message_type == message_type):
                asyncio.create_task(handler(message))
                return


# 全局路由实例
router = MessageRouter()
