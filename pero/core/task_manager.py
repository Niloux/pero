import asyncio
import time
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
from typing import Any, Dict, Optional

from pero.core.adapter import Adapter
from pero.core.event import EventParser
from pero.utils.logger import logger
from pero.utils.queue import recv_queue


class TaskPriority(Enum):
    LOW = 0
    NORMAL = 1
    HIGH = 2


@dataclass
class TaskInfo:
    task: asyncio.Task
    priority: TaskPriority
    created_at: datetime
    event_type: str
    retries: int = 0
    max_retries: int = 3
    timeout: Optional[float] = None


class TaskManager:
    def __init__(
        self,
        adapter: Adapter,
        parser: EventParser,
        max_concurrent_tasks: int = 100,
        default_timeout: float = 60.0,
    ):
        self.adapter = adapter
        self.parser = parser
        self.max_concurrent_tasks = max_concurrent_tasks
        self.default_timeout = default_timeout
        self.running_tasks: Dict[asyncio.Task, TaskInfo] = {}
        self.task_semaphore = asyncio.Semaphore(max_concurrent_tasks)
        self.shutting_down = False

        # Performance metrics
        self.total_processed = 0
        self.failed_tasks = 0
        self.avg_processing_time = 0

    async def start(self):
        try:
            await asyncio.gather(
                self.process_events(),
                self.monitor_tasks(),
            )
        except Exception as e:
            logger.error(f"Error in TaskManager: {e}")
            raise

    async def process_events(self):
        while not self.shutting_down:
            event = await recv_queue.get()
            await self.task_semaphore.acquire()

            priority = self._determine_priority(event)
            task = asyncio.create_task(self._publish_with_timeout(event))
            task_info = TaskInfo(
                task=task,
                priority=priority,
                created_at=datetime.now(),
                event_type=event.get("type", "unknown"),
                timeout=event.get("timeout", self.default_timeout),
            )

            self.running_tasks[task] = task_info
            task.add_done_callback(self._task_done_callback)

    def _determine_priority(self, event: Dict[str, Any]) -> TaskPriority:
        return TaskPriority[event.get("priority", "NORMAL").upper()]

    async def _publish_with_timeout(self, event: Dict[str, Any]):
        start_time = time.time()
        task_info = self.running_tasks[asyncio.current_task()]

        try:
            return await asyncio.wait_for(self.publish(event), timeout=task_info.timeout)
        except asyncio.TimeoutError:
            if task_info.retries < task_info.max_retries:
                task_info.retries += 1
                logger.warning(f"Task timeout, retrying ({task_info.retries}/{task_info.max_retries})")
                return await self._publish_with_timeout(event)
            else:
                raise
        finally:
            self._update_metrics(time.time() - start_time)

    async def publish(self, event: Dict[str, Any]):
        try:
            parsed_msg = await self.parser.parse(event)
            if parsed_msg:
                logger.debug(f"{parsed_msg=}")
                await self.adapter.run(parsed_msg)

        except Exception as e:
            logger.error(f"Error handling event: {e}")
            raise

    async def monitor_tasks(self):
        while not self.shutting_down:
            await asyncio.sleep(5)
            current_time = datetime.now()

            for task, info in list(self.running_tasks.items()):
                if (current_time - info.created_at).total_seconds() > info.timeout:
                    logger.warning(
                        f"Task running too long: {(current_time - info.created_at).total_seconds()}s > {info.timeout}s"
                    )

            # Log statistics
            logger.info(f"Active tasks: {len(self.running_tasks)}")
            logger.info(f"Total processed: {self.total_processed}")
            logger.info(f"Failed tasks: {self.failed_tasks}")
            logger.info(f"Average processing time: {self.avg_processing_time:.2f}s")

    def _task_done_callback(self, task: asyncio.Task):
        try:
            task.result()
        except Exception as e:
            self.failed_tasks += 1
            logger.error(f"Task failed: {e}")

        if task in self.running_tasks:
            del self.running_tasks[task]
        self.task_semaphore.release()

    def _update_metrics(self, processing_time: float):
        self.total_processed += 1
        self.avg_processing_time = (
            self.avg_processing_time * (self.total_processed - 1) + processing_time
        ) / self.total_processed

    async def shutdown(self, timeout: float = 30.0):
        logger.info("Initiating TaskManager shutdown...")
        self.shutting_down = True

        if self.running_tasks:
            try:
                await asyncio.wait_for(
                    asyncio.gather(*[task.task for task in self.running_tasks.values()], return_exceptions=True),
                    timeout=timeout,
                )
            except asyncio.TimeoutError:
                logger.warning("Shutdown timeout reached, cancelling remaining tasks...")
                for task in self.running_tasks:
                    task.cancel()

        logger.info(f"TaskManager shutdown complete. Processed {self.total_processed} tasks total.")
