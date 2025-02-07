from pero.logger import get_log
from pero.type import EventType, MessageType

_log = get_log()

a = {
    "self_id": 183734182,
    "user_id": 1400621898,
    "time": 1738935110,
    "message_id": 1643469028,
    "message_seq": 1643469028,
    "real_id": 1643469028,
    "message_type": "private",
    "sender": {"user_id": 1400621898, "nickname": "Texasx3d", "card": ""},
    "raw_message": "4",
    "font": 14,
    "sub_type": "friend",
    "message": [{"type": "text", "data": {"text": "4"}}],
    "message_format": "array",
    "post_type": "message",
    "target_id": 1400621898,
}


def parse_events(message):
    """根据post_type确认上报事件"""
    try:
        post_type = message.get("post_type")
        if post_type == "message":
            return EventType.EVENT_MESSAGE
        elif post_type == "notice":
            return EventType.EVENT_NOTICE
        elif post_type == "request":
            return EventType.EVENT_REQUEST
        elif post_type == "meta_event":
            return EventType.EVENT_META
    except Exception as e:
        _log.error(f"parse_events error: {e}")
        raise e


def parse_types(message):
    """根据{event}_type确认消息类型"""
    try:
        event = message.get("post_type")
        message_type = message.get(f"{event}_type")
        if event == "message":
            if message_type == "group":
                return MessageType.MESSAGE_GROUP
            elif message_type == "private":
                return MessageType.MESSAGE_PRIVATE
            # TODO
        elif event == "notice":
            # TODO
            pass
        elif event == "request":
            # TODO
            pass
    except Exception as e:
        _log.error(f"parse_types error: {e}")
        raise e


def parse(message):
    return (
        EventType.EVENT_MESSAGE,
        MessageType.MESSAGE_TEXT,
    )
