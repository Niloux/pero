import asyncio
from typing import Any, Dict

from pero.core.dispatcher import EventHandler
from pero.core.event_parser import EventParser
from pero.utils.logger import logger
from pero.utils.queue import post_queue, recv_queue


class TaskManager:
    def __init__(self, dispatch: EventHandler, parser: EventParser):
        self.dispatch = dispatch
        self.parser = parser

    async def start(self):
        while True:
            event = await recv_queue.get()
            asyncio.create_task(self.handle_event(event))

    async def handle_event(self, event: Dict[str, Any]):
        parsed_event = await self.parser.parse_event(event)
        if parsed_event:
            logger.debug(f"Parsed event: {parsed_event}")
            results = await self.dispatch.handle_event(parsed_event)

        for result in results:
            # 状态信息响应为None，不放入队列
            if result:
                await post_queue.put(result)
                logger.debug(f"Posted result to queue: {result}")
