import asyncio
from typing import Any, Callable, Dict, List

from pero.utils.logger import logger


class MessageAdapter:
    handlers = {
        "request": {},
        "notice": {},
        "message": {},
        "meta_event": {},
        "status": {},
    }

    @classmethod
    def register_handler(cls, handler_type: str, event_type: str):
        def decorator(handler: Callable):
            if event_type not in cls.handlers[handler_type]:
                cls.handlers[handler_type][event_type] = []
            cls.handlers[handler_type][event_type].append(handler)
            logger.debug(f"Registered {handler_type} handler for type: {event_type}")
            return handler

        return decorator

    @classmethod
    async def handle_event(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        handler_type = event.get("event")
        event_type = event.get(f"{handler_type}_type")
        results = []

        if isinstance(event_type, list):
            for type in event_type:
                handlers = cls.handlers[handler_type].get(type, [])
                results.extend(
                    await asyncio.gather(*[handler(event) for handler in handlers])
                )
        else:
            handlers = cls.handlers[handler_type].get(event_type, [])
            results.extend(
                await asyncio.gather(*[handler(event) for handler in handlers])
            )

        return results

    @classmethod
    async def handle_request(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await cls.handle_event("request", event)

    @classmethod
    async def handle_notice(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await cls.handle_event("notice", event)

    @classmethod
    async def handle_message(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await cls.handle_event("message", event)

    @classmethod
    async def handle_meta_event(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        return await cls.handle_event("meta_event", event)


# 示例：注册处理message类型事件的方法
@MessageAdapter.register_handler("message", "text")
async def handle_friend_message(event: Dict[str, Any]) -> Dict[str, Any]:
    from pero.api import PERO_API

    if event.get("source_type") != "private":
        return await PERO_API.post_group_msg(
            group_id=event.get("target"),
            text="私人测试功能喵～",
            reply=event.get("reply"),
        )
    logger.info(f"测试收到消息: {event}")
    return await PERO_API.post_private_msg(
        user_id=event.get("target"),
        text="你好，我是pero，很高兴见到你！",
        reply=event.get("reply"),
    )


# 示例：注册处理status类型事件的方法
@MessageAdapter.register_handler("status", "ok")
async def handle_friend_status(event: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"Handling status message: {event}")
