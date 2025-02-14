import asyncio
from typing import Any, Callable, Dict, List

from pero.message_adapter import MessageAdapter
from pero.utils.logger import logger


class EventAdapter:
    handlers = {
        "request": {},
        "notice": {},
        "message": {},
        "meta_event": {},
        "status": {},
    }

    @classmethod
    def register_handler(cls, handler_type: str, event_type: str):
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
            results.extend(await MessageAdapter.handle_event(event))
        else:
            # TODO后续根据事件的需要可能会增添meta_event_adapter, notice_adapter, request_adapter等
            if isinstance(event_type, list):
                for type in event_type:
                    handlers = cls.handlers[handler_type].get(type, [])
                    results.extend(
                        await asyncio.gather(*[handler(event) for handler in handlers])
                    )
            else:
                handlers = cls.handlers[handler_type].get(event_type, [])
                results.extend(
                    await asyncio.gather(*[handler(event) for handler in handlers])
                )

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


# Example: Registering a handler for status events
@EventAdapter.register_handler("status", "ok")
async def handle_status(event: Dict[str, Any]) -> Dict[str, Any]:
    logger.info(f"napcat回应状态: {event}")
