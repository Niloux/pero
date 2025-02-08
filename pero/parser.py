from pero.logger import get_log
from pero.type import EventType, Message, MessageType

_log = get_log()


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
    # message = json.loads(message)
    # event = parse_event(message)
    return (
        EventType.MESSAGE.FRIEND,
        MessageType.TEXT,
    )
