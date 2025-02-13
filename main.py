import asyncio

from pero.message_adapter import MessageAdapter
from pero.plugin_loader import load_plugins
from pero.task_manager import TaskManager
from pero.utils.config import config
from pero.utils.logger import logger
from pero.websocket import WebSocketClient


async def main():
    uri = config.get("ws_uri")
    async with WebSocketClient(uri) as client:
        # 加载插件
        await load_plugins()

        dispatcher = MessageAdapter()
        task_manager = TaskManager(dispatcher)

        # 等待接收、发送任务和任务管理器的启动完成
        await asyncio.gather(
            client.receive_task, client.post_task, task_manager.start()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
