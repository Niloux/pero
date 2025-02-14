from typing import Any, Dict, Optional

from pero.utils.logger import logger


class EventParser:
    @staticmethod
    async def parse_event(msg: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        event_type = msg.get("post_type")
        parse_method = getattr(EventParser, f"_parse_{event_type}", None)

        if parse_method:
            return await parse_method(msg)
        else:
            if msg.get("status"):
                return await EventParser._parse_status(msg)
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
        source_type = event.get("message_type")  # "private" 或 "group"
        sender_type = event.get("sub_type")  # "friend" 或 "other"

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
            "source_type": source_type,
            "sender_type": sender_type,
            "message_type": message_types,
            "content": content,
            "target": target,
            "reply": reply,
        }
