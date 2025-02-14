import asyncio
from typing import Any, Dict, Set

from pero.core.dispatcher import EventHandler
from pero.core.event_parser import EventParser
from pero.utils.logger import logger
from pero.utils.queue import post_queue, recv_queue


class TaskManager:
    def __init__(self, dispatch: EventHandler, parser: EventParser):
        self.dispatch = dispatch
        self.parser = parser
        self.running_tasks: Set[asyncio.Task] = set()

    async def start(self):
        while True:
            event = await recv_queue.get()
            task = asyncio.create_task(self.handle_event(event))
            task.add_done_callback(self.running_tasks.discard)
            self.running_tasks.add(task)

    async def handle_event(self, event: Dict[str, Any]):
        try:
            parsed_event = await self.parser.parse_event(event)
            if parsed_event:
                logger.debug(f"Parsed event: {parsed_event}")
                results = await self.dispatch.handle_event(parsed_event)

                for result in results:
                    if result:
                        await post_queue.put(result)
                        logger.debug(f"Posted result to queue: {result}")
        except Exception as e:
            logger.error(f"Error handling event: {e}")

    async def shutdown(self):
        logger.info("Shutting down TaskManager...")

        for task in self.running_tasks:
            task.cancel()

        if self.running_tasks:
            await asyncio.gather(*self.running_tasks, return_exceptions=True)

        logger.info("TaskManager shutdown complete")
