import asyncio
import traceback
from typing import Optional

from pero.api import BotAPI, WebSocketClient
from pero.config import CONFIG
from pero.logger import get_log
from pero.parser import EventParser
from pero.plugin_loader import load_plugins
from pero.router import EventDispatcher

_log = get_log()


class BotClient:
    def __init__(self, url: str, max_concurrent_messages: int = 100):
        self.url = url
        self.client: Optional[WebSocketClient] = None
        self.api: Optional[BotAPI] = None
        self.is_running = False
        self._message_semaphore = asyncio.Semaphore(max_concurrent_messages)
        self._message_queue = asyncio.Queue()
        self._tasks = set()

    async def _process_message(self, msg: str):
        """处理单个消息"""
        try:
            async with self._message_semaphore:
                _log.info(f"***收到消息: {msg}")
                event = await EventParser.parse_event(msg)
                if event:
                    await EventDispatcher.dispatch(event, self.api)
                else:
                    _log.warning(f"解析事件失败或事件为空: {msg}")
        except Exception as e:
            _log.error(f"Error processing message: {e}")
            _log.error(traceback.format_exc())

    async def _message_consumer(self):
        """消息消费者，从队列中获取并处理消息"""
        while self.is_running:
            try:
                msg = await self._message_queue.get()
                task = asyncio.create_task(self._process_message(msg))
                self._tasks.add(task)
                task.add_done_callback(self._tasks.discard)
            except Exception as e:
                _log.error(f"Error in message consumer: {e}")
                _log.error(traceback.format_exc())

    async def _message_receiver(self):
        """消息接收器，从 WebSocket 接收消息并放入队列"""
        while self.is_running and self.client.is_connected:
            try:
                msg = await self.client.receive()
                await self._message_queue.put(msg)
            except Exception as e:
                _log.error(f"Error receiving message: {e}")
                _log.error(traceback.format_exc())
                # 如果接收消息出错，可能需要重新连接
                await self._reconnect()

    async def _reconnect(self):
        """重新连接 WebSocket"""
        try:
            if self.client:
                await self.client.close()
            await self._connect()
        except Exception as e:
            _log.error(f"Error reconnecting: {e}")
            _log.error(traceback.format_exc())
            # 等待一段时间后重试
            await asyncio.sleep(5)

    async def _connect(self):
        """建立 WebSocket 连接"""
        self.client = await WebSocketClient(self.url).__aenter__()
        self.api = BotAPI(self.client)

    async def start(self):
        """启动客户端"""
        try:
            self.is_running = True
            await self._connect()
            await load_plugins()

            # 启动消息消费者
            consumer_task = asyncio.create_task(self._message_consumer())
            # 启动消息接收器
            receiver_task = asyncio.create_task(self._message_receiver())

            # 等待任务完成或发生错误
            await asyncio.gather(consumer_task, receiver_task)

        except Exception as e:
            _log.error(f"Error during client operation: {e}")
            _log.error(traceback.format_exc())
        finally:
            self.is_running = False
            # 清理所有正在运行的任务
            for task in self._tasks:
                task.cancel()
            if self.client:
                await self.client.close()


async def main():
    """主函数"""
    client = BotClient(CONFIG.ws_url)
    while True:
        try:
            await client.start()
        except Exception as e:
            _log.error(f"Client crashed, restarting: {e}")
            _log.error(traceback.format_exc())
            await asyncio.sleep(5)  # 等待一段时间后重试


if __name__ == "__main__":
    asyncio.run(main())
