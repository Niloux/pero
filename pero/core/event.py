"""解析event事件，将不同类型的event解析并派送给不同的adapter"""

from typing import Any, Dict

from pero.core.command import CommandParser
from pero.core.common import _Message
from pero.core.message_types import At, Image, Text


class EventParser:
    def __init__(self):
        pass

    @classmethod
    async def parse(cls, msg: Dict[str, Any]) -> Any:
        event_type = msg.get("post_type")
        if event_type == "message":
            await cls._parse_message(msg)
        elif event_type == "notice":
            await cls._parse_notice(msg)
        elif event_type == "request":
            await cls._parse_request(msg)
        elif event_type == "meta_event":
            await cls._parse_meta_event(msg)
        elif event_type == "status":
            await cls._parse_status(msg)

    @classmethod
    async def _parse_message(cls, msg: Dict[str, Any]) -> _Message:
        _message = _Message()

        # 解析消息内容
        contents = msg.get("message", [])
        for i in contents:
            if i.get("type") == "text":
                _message.content.append(Text.from_dict(i))
                _message.content_types.append("text")
            elif i.get("type") == "at":
                _message.content.append(At.from_dict(i))
                _message.content_types.append("at")
            elif i.get("type") == "image":
                _message.content.append(Image.from_dict(i))
                _message.content_types.append("image")
            # TODO: 其他类型后续再扩充

        # 解析消息元信息
        _message.type = msg.get("message_type")
        _message.sub_type = msg.get("sub_type")
        _message.sender = msg.get("sender")
        _message.id = msg.get("message_id")
        _message.target = msg.get("user_id") if _message.type == "private" else msg.get("group_id")

        # 解析命令
        text_parts = _message.get_text()
        commands = await CommandParser.parse(text_parts)
        _message.commands.extend(filter(None, commands))

        if _message.commands:
            _message.has_cmd = True

        return _message

    @classmethod
    async def _parse_notice(cls, msg: Dict[str, Any]) -> Any:
        pass

    @classmethod
    async def _parse_request(cls, msg: Dict[str, Any]) -> Any:
        pass

    @classmethod
    async def _parse_meta_event(cls, msg: Dict[str, Any]) -> Any:
        pass

    @classmethod
    async def _parse_status(cls, msg: Dict[str, Any]) -> Any:
        pass
