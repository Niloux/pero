from typing import Dict

from pero.logger import get_log

_log = get_log()


class EventParser:
    @staticmethod
    async def parse_event(msg: Dict):
        event_type = msg.get("post_type")
        if event_type == "message" or event_type == "message_sent":
            return EventParser._parse_message(msg)
        elif event_type == "meta_event":
            return EventParser._parse_meta(msg)
        else:
            # TODO
            _log.error(f"未配置解析: {msg}")
            return None

    @classmethod
    def _parse_meta(self, event: Dict) -> Dict:
        """解析meta事件"""
        return {
            "event": "meta_event",
            "meta_type": event.get("meta_event_type"),
            "interval": event.get("interval"),
            "status": event.get("status"),
        }

    @classmethod
    def _parse_message(self, event: Dict) -> Dict:
        """
        解析消息事件，根据消息的类型、来源、发送者等信息，转化为统一结构。
        """
        # 基本字段解析
        source_type = event.get("message_type")  # "private" 或 "group"
        sender_type = event.get("sub_type")  # "friend" 或 "other"

        # 提取消息类型列表
        message_types = []
        for msg in event.get("message", []):
            msg_type = msg.get("type")
            if msg_type:
                message_types.append(msg_type)

        # 提取消息内容
        content = event.get("message", [])

        # 获取目标来源
        target = (
            event.get("target_id") if event.get("target_id") else event.get("group_id")
        )
        reply = event.get("message_id")

        # 构建最终统一结构
        return {
            "event": "message",
            "source_type": source_type,
            "sender_type": sender_type,
            "message_types": message_types,
            "content": content,
            "target": target,
            "reply": reply,
        }


# 示例解析
if __name__ == "__main__":
    # 示例消息体
    from text import a, b, c

    events = [a, b, c]

    for event in events:
        parsed_event = EventParser.parse_message(event)
        print(parsed_event)
