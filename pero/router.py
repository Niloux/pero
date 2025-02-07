class MessageRouter:
    def __init__(self):
        self.handlers = {}

    def register(self, event_type, message_type, source_type=None, identifer=None):
        """装饰器：将函数注册到路由表，type=None时表示不需要验证"""

        def decorator(func):
            key = (
                event_type,
                message_type,
                source_type
                if source_type is not None
                else "ALL_SOURCE",  # Default value if None
                identifer
                if identifer is not None
                else "ALL_USERS",  # Default value if None
            )
            self.handlers[key] = func
            print(f"Registered handler for {key}")
            return func

        return decorator

    def handle_message(
        self, event_type, message_type, source_type=None, identifer=None
    ):
        """根据路由表处理消息，identifer=None时表示不验证用户"""
        source_type = source_type if source_type is not None else "ALL_SOURCE"
        identifer = identifer if identifer is not None else "ALL_USERS"

        key = (event_type, message_type, source_type, identifer)
        handler = self.handlers.get(key)
        if handler:
            return self.handlers[key]()
        else:
            print("No handler found for this message.")


# 全局路由实例
router = MessageRouter()
