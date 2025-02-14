import asyncio
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

from pero.cmd.command_manager import command_manager
from pero.plugin_system import plugin_manager
from pero.utils.logger import logger


class MessageAdapter:
    handlers: Dict[str, Dict[Tuple[str], List[Tuple[str, Callable]]]] = {
        "private": {},
        "group": {},
    }

    @classmethod
    def register(
        cls, source_type: str, message_types: List[str], plugin_name: str
    ) -> Callable:
        def decorator(handler: Callable) -> Callable:
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
    async def handle_event(
        cls, event: Dict[str, Any]
    ) -> List[Union[Tuple[str, Dict], None]]:
        source_type: str = event.get("source_type", "")
        event_types: Any = event.get("message_type", [])
        results: List[Union[Tuple[str, Dict], None]] = []

        if isinstance(event_types, list):
            event_types = sorted(event_types)
        else:
            event_types = [event_types]

        key: Tuple[str] = tuple(event_types)
        handlers: List[Tuple[str, Callable]] = cls.handlers.get(source_type, {}).get(
            key, []
        )

        # 插件消息任务
        for plugin_name, handler in handlers:
            plugin_instance: Optional[Any] = plugin_manager.get_plugin(plugin_name)
            if plugin_instance:
                try:
                    result = await handler(plugin_instance, event)
                    results.append(cls._ensure_valid_result(result))
                except Exception as e:
                    logger.error(f"Error handling event with plugin {plugin_name}: {e}")
            else:
                logger.error(f"Plugin instance for {plugin_name} not found.")

        # cmd指令
        try:
            cmd_results = await asyncio.gather(
                command_manager.execute(event),
            )
            results.extend(cls._ensure_valid_result(result) for result in cmd_results)
        except Exception as e:
            logger.error(f"Error executing command manager: {e}")

        return results

    @staticmethod
    def _ensure_valid_result(result: Any) -> Union[Tuple[str, Dict], None]:
        """确保结果是 (字符串, 字典) 或 None"""
        if result is None:
            return result
        elif (
            isinstance(result, tuple)
            and len(result) == 2
            and isinstance(result[0], str)
            and isinstance(result[1], dict)
        ):
            return result
        logger.warning(
            f"Unexpected result type: {type(result)}. Expected (str, dict) or None."
        )
        return None
