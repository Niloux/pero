import asyncio
from typing import Any, Callable, Dict, List, Tuple

from pero.logger import get_log

_log = get_log()


class EventDispatcher:
    _event_handlers: Dict[str, List[Callable[..., Any]]] = {}

    @classmethod
    def register_event(cls, event_type: str):
        """装饰器：注册事件处理函数"""

        def decorator(func: Callable[..., Any]):
            if event_type not in cls._event_handlers:
                cls._event_handlers[event_type] = []
            cls._event_handlers[event_type].append(func)
            return func

        return decorator

    @classmethod
    async def dispatch(cls, event: dict):
        """异步分发事件"""
        event_type = event.get("event")
        handlers = cls._event_handlers.get(event_type, [])

        if not handlers:
            print(f"未处理的事件类型: {event_type}")
            return None

        # 并发执行所有处理函数
        results = await asyncio.gather(*(handler(event) for handler in handlers))
        return results  # 返回所有处理函数的结果


# 消息适配器
class MessageAdapter:
    _message_handlers: Dict[Tuple[str, str, str], List[Callable[..., Any]]] = {}

    @classmethod
    def register_message(
        cls, message_type: str, source_type: str = None, sender_type: str = None
    ):
        """装饰器：注册消息类型处理函数"""

        def decorator(func: Callable[..., Any]):
            # 默认匹配所有 source_type 和 sender_type
            actual_source_type = "*" if source_type is None else source_type
            actual_sender_type = "*" if sender_type is None else sender_type

            # 处理注册
            key = (message_type, actual_source_type, actual_sender_type)
            if key not in cls._message_handlers:
                cls._message_handlers[key] = []
            cls._message_handlers[key].append(func)
            return func

        return decorator

    @classmethod
    def get_handlers(cls, message_type: str, source_type: str, sender_type: str):
        """获取注册的处理函数"""
        # 尝试匹配具体的 (message_type, source_type, sender_type)
        # 如果有 * 需要进行宽松匹配
        handlers = []
        for (
            reg_message_type,
            reg_source_type,
            reg_sender_type,
        ), funcs in cls._message_handlers.items():
            # 只要 message_type 对应，且 source_type 和 sender_type 匹配，或者为 "*"
            if (
                reg_message_type == message_type
                and (reg_source_type == source_type or reg_source_type == "*")
                and (reg_sender_type == sender_type or reg_sender_type == "*")
            ):
                handlers.extend(funcs)
        return handlers

    @classmethod
    async def handle_message(cls, event: dict):
        """处理 message 事件, 一个event_message可能携带多种message_type"""
        message_types = event.get("message_types", [])
        source_type = event.get("source_type")  # 来源类型（如群聊、私聊等）
        sender_type = event.get("sender_type")  # 发送者类型（如好友、群成员等）

        for message_type in message_types:
            handlers = cls.get_handlers(message_type, source_type, sender_type)
            if len(handlers) == 0:
                print(f"未注册的消息类型: {message_type}")
                continue
            for handler in handlers:
                _log.info(f"调用消息处理器: {handler.__name__}, 处理事件: {event}")
                await handler(event)


# ========== 注册事件处理器 ==========


# 示例：注册多个异步处理函数
@EventDispatcher.register_event("message")
async def handler1(event):
    await asyncio.sleep(1)  # 模拟异步操作（比如数据库查询）
    print(f"处理器 1 处理消息: {event}")


@EventDispatcher.register_event("message")
async def handler2(event):
    await asyncio.sleep(0.5)  # 模拟异步操作（比如 HTTP 请求）
    print(f"处理器 2 处理消息: {event}")


@EventDispatcher.register_event("message")
async def handle_message_event(event: dict):
    """处理 message 事件"""
    await MessageAdapter.handle_message(event)


# ========== 注册不同的 message 类型处理器 ==========


@MessageAdapter.register_message("text")
async def handle_text_message(event: dict):
    """处理文本消息"""
    print(
        f"[文本消息] 来源: {event.get('source_type')}, 发送者: {event.get('sender_type')}, 内容: {event.get('content')}"
    )
    return {"response": f"收到文本: {event.get('content')}"}


@MessageAdapter.register_message("image")
async def handle_image_message(event: dict, source_type: str, sender_type: str):
    """处理图片消息"""
    print(
        f"[图片消息] 来源: {source_type}, 发送者: {sender_type}, 图片URL: {event.get('url')}"
    )
    return {"response": "收到图片，处理中..."}


@MessageAdapter.register_message("voice")
async def handle_voice_message(event: dict, source_type: str, sender_type: str):
    """处理语音消息"""
    print(
        f"[语音消息] 来源: {source_type}, 发送者: {sender_type}, 语音文件: {event.get('file')}"
    )
    return {"response": "收到语音，处理中..."}


# ========== 测试 ==========

if __name__ == "__main__":
    # 示例事件
    events = [
        {
            "event": "message",
            "message_type": "text",
            "source_type": "private",
            "sender_type": "friend",
            "content": "你好，主人！",
        },
        {
            "event": "message",
            "message_type": "image",
            "source_type": "group",
            "sender_type": "other",
            "url": "http://example.com/image.jpg",
        },
        {
            "event": "message",
            "message_type": "voice",
            "source_type": "private",
            "sender_type": "other",
            "file": "voice.mp3",
        },
        {"event": "user_join", "user_id": 12345},
        {"event": "unknown_event", "data": "???"},
    ]

    for event in events:
        response = EventDispatcher.dispatch(event)
        if response:
            print("响应:", response)
