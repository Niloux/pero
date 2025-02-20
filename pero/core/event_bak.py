import asyncio
from typing import Any, Callable, Dict, List, Optional

from pero.core.message_adapter import MessageAdapter
from pero.utils.logger import logger


class EventHandler:
    handlers = {
        "request": {},
        "notice": {},
        "message": {},
        "meta_event": {},
        "status": {},
    }

    @classmethod
    def register(cls, handler_type: str, event_type: str):
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

        if handler_type == "message":
            results.extend(await MessageAdapter.handle_message(event))
        else:
            # TODO后续根据事件的需要可能会增添meta_event_adapter, notice_adapter, request_adapter等
            if isinstance(event_type, list):
                for type in event_type:
                    handlers = cls.handlers[handler_type].get(type, [])
                    results.extend(await asyncio.gather(*[handler(event) for handler in handlers]))
            else:
                handlers = cls.handlers[handler_type].get(event_type, [])
                results.extend(await asyncio.gather(*[handler(event) for handler in handlers]))

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


class EventParser:
    @classmethod
    async def parse_event(cls, msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        event_type = msg.get("post_type")
        parse_method = getattr(EventParser, f"_parse_{event_type}", None)

        if parse_method:
            return await parse_method(msg)
        else:
            if msg.get("status"):
                return await cls._parse_status(msg)
            # 处理未知事件和napcat响应状态信息
            logger.warning(f"Unsupported event type: {event_type}")
            return None

    @classmethod
    async def _parse_status(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """解析napcat响应状态信息"""
        status = event.get("status")
        reply = event.get("message_id")
        wording = event.get("wording")
        return {
            "event": "status",
            "status_type": status,
            "reply": reply,
            "wording": wording,
        }

    @classmethod
    async def _parse_request(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """解析request事件"""
        # 示例解析逻辑
        return {
            "event": "request",
            "request_type": event.get("request_type"),
            "user_id": event.get("user_id"),
            "comment": event.get("comment"),
        }

    @classmethod
    async def _parse_notice(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """解析notice事件"""
        # 示例解析逻辑
        return {
            "event": "notice",
            "notice_type": event.get("notice_type"),
            "user_id": event.get("user_id"),
            "group_id": event.get("group_id"),
        }

    @classmethod
    async def _parse_meta_event(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """解析meta事件"""
        return {
            "event": "meta_event",
            "meta_event_type": event.get("meta_event_type"),
            "interval": event.get("interval"),
            "status": event.get("status"),
        }

    @classmethod
    async def _parse_message(cls, event: Dict[str, Any]) -> Dict[str, Any]:
        """
        解析消息事件，根据消息的类型、来源、发送者等信息，转化为统一结构。
        """
        # 基本字段解析
        source = event.get("message_type")  # "private" 或 "group"
        sender = event.get("sub_type")  # "friend" 或 "other"

        # 提取消息类型列表
        message_types = [msg.get("type") for msg in event.get("message", []) if msg.get("type")]

        # 提取消息内容
        content = event.get("message", [])

        # 获取目标来源
        target = event.get("target_id") or event.get("group_id")
        reply = event.get("message_id")

        # 构建最终统一结构
        return {
            "event": "message",
            "source": source,
            "sender": sender,
            "message_type": message_types,
            "content": content,
            "target": target,
            "reply": reply,
        }


# Example: Registering a handler for status events
@EventHandler.register("status", "ok")
async def handle_status(event: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"napcat回应状态: {event}")
