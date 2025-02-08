import json

from pero.logger import get_log
from pero.type import EventType, Message, MessageType

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

b = {
    "self_id": 183734182,
    "user_id": 1400621898,
    "time": 1738980075,
    "message_id": 448304138,
    "message_seq": 448304138,
    "real_id": 448304138,
    "message_type": "group",
    "sender": {
        "user_id": 1400621898,
        "nickname": "Texasx3d",
        "card": "",
        "role": "owner",
    },
    "raw_message": "1",
    "font": 14,
    "sub_type": "normal",
    "message": [{"type": "text", "data": {"text": "1"}}],
    "message_format": "array",
    "post_type": "message",
    "group_id": 472609637,
}

c = {
    "self_id": 183734182,
    "user_id": 1400621898,
    "time": 1738980373,
    "message_id": 511993897,
    "message_seq": 511993897,
    "real_id": 511993897,
    "message_type": "group",
    "sender": {
        "user_id": 1400621898,
        "nickname": "Texasx3d",
        "card": "",
        "role": "owner",
    },
    "raw_message": "[CQ:reply,id=751482848][CQ:at,qq=183734182]1",
    "font": 14,
    "sub_type": "normal",
    "message": [
        {"type": "reply", "data": {"id": "751482848"}},
        {"type": "at", "data": {"qq": "183734182"}},
        {"type": "text", "data": {"text": "1"}},
    ],
    "message_format": "array",
    "post_type": "message",
    "group_id": 472609637,
}


def parse_event_msg(message):
    sub_type = message.get("sub_type")
    if sub_type == "friend":
        return Message.FRIEND
    elif sub_type == "group":
        return Message.GROUP
    elif sub_type == "group_self":
        return Message.GROUP_SELF
    elif sub_type == "other":
        return Message.OTHER
    elif sub_type == "normal":
        return Message.NORMAL
    elif sub_type == "notice":
        return Message.NOTICE
    elif sub_type == "anonymous":
        return Message.ANONYMOUS
    else:
        _log.warning(f"Unknown sub_type: {sub_type}")
        raise Exception(f"Unknown sub_type: {sub_type}")


def parse_event(message: dict) -> EventType:
    event = message.get("post_type")
    if event in ["message", "message_sent"]:
        event = parse_event_msg(message)
    elif event == "meta_event":
        pass
    elif event == "request":
        pass
    elif event == "notice":
        pass
    else:
        _log.warning(f"Unknown event: {event}")
        raise Exception(f"Unknown event: {event}")

    return event


def parse(message: str) -> tuple[EventType, MessageType]:
    message = json.loads(message)
    event = parse_event(message)
    return (
        event,
        MessageType.TEXT,
    )
