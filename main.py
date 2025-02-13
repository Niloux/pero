import asyncio

from pero.cmd.command_manager import command_manager
from pero.message_adapter import MessageAdapter
from pero.plugin_loader import load_plugins
from pero.task_manager import TaskManager
from pero.utils.config import config
from pero.utils.logger import logger
from pero.websocket import WebSocketClient


async def main():
    uri = config.get("ws_uri")
    async with WebSocketClient(uri) as client:
        # 加载插件和cmd
        load_plugins()
        command_manager.load_commands("pero/cmd")

        # 等待接收、发送任务和任务管理器的启动完成
        dispatcher = MessageAdapter()
        task_manager = TaskManager(dispatcher)
        await asyncio.gather(
            client.receive_task, client.post_task, task_manager.start()
        )


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Process interrupted by user.")
