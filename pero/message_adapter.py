import asyncio
from typing import Any, Callable, Dict, List

from pero.cmd.command_manager import command_manager
from pero.utils.logger import logger


class MessageAdapter:
    handlers = {
        "private": {},
        "group": {},
    }

    @classmethod
    def register(cls, source_type: str, required_event_types: List[str]):
        def decorator(handler: Callable):
            key = tuple(sorted(required_event_types))
            if key not in cls.handlers[source_type]:
                cls.handlers[source_type][key] = []
            cls.handlers[source_type][key].append(handler)
            logger.debug(
                f"Registered {source_type} handler for event types: {required_event_types}"
            )
            return handler

        return decorator

    @classmethod
    async def handle_event(cls, event: Dict[str, Any]) -> List[Dict[str, Any]]:
        source_type = event.get("source_type")
        event_types = event.get("message_type")
        results = []

        if isinstance(event_types, list):
            event_types = sorted(event_types)
        else:
            event_types = [event_types]

        key = tuple(event_types)
        handlers = cls.handlers[source_type].get(key, [])

        # 将cmd指令添加在这里
        results.extend(
            [
                task_result
                for task_result in await asyncio.gather(
                    *[handler(event) for handler in handlers],
                    command_manager.execute(event),
                )
                if task_result is not None
            ]
        )

        return results


@MessageAdapter.register("group", ["text"])
async def handle_group_text_and_at_message(event: Dict[str, Any]) -> Dict[str, Any]:
    from pero.api import PERO_API

    logger.debug(f"Handling group message with text and at: {event}")
    return await PERO_API.post_group_msg(
        group_id=event.get("target"),
        text="这是一个群消息。",
        reply=event.get("reply"),
    )
