import asyncio
from typing import Any, Callable, Dict, List

from pero.cmd.command_manager import command_manager
from pero.plugin_system import plugin_manager
from pero.utils.logger import logger


class MessageAdapter:
    handlers = {
        "private": {},
        "group": {},
    }

    @classmethod
    def register(cls, source_type: str, message_types: List[str], plugin_name: str):
        def decorator(handler: Callable):
            key = tuple(sorted(message_types))
            if key not in cls.handlers[source_type]:
                cls.handlers[source_type][key] = []
            cls.handlers[source_type][key].append((plugin_name, handler))
            logger.info(
                f"Registered {source_type} message handler for types: {message_types} by plugin: {plugin_name}"
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

        # 插件消息任务
        for plugin_name, handler in handlers:
            plugin_instance = plugin_manager.get_plugin(plugin_name)
            if plugin_instance:
                results.append(await handler(plugin_instance, event))
            else:
                logger.error(f"Plugin instance for {plugin_name} not found.")

        # cmd指令
        results.extend(
            await asyncio.gather(
                command_manager.execute(event),
            )
        )

        return results


# @MessageAdapter.register("group", ["text"])
# async def handle_group_text_message(event: Dict[str, Any]) -> Dict[str, Any]:
#     from pero.api import PERO_API

#     logger.info(f"处理group--[text] {event}")
#     return await PERO_API.post_group_msg(
#         group_id=event.get("target"),
#         text="这是一个群消息。",
#         reply=event.get("reply"),
#     )

# @MessageAdapter.register("group", ["text", "at"])
# async def handle_group_text_and_at_message(event: Dict[str, Any]) -> Dict[str, Any]:
#     from pero.api import PERO_API

#     logger.info(f"处理group--[text, at] {event}")
#     return await PERO_API.post_group_msg(
#         group_id=event.get("target"),
#         text="这是一个at群消息。",
#         reply=event.get("reply"),
#     )
