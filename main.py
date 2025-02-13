import asyncio
import traceback

from pero.api import BotAPI
from pero.config import CONFIG
from pero.logger import get_log
from pero.parser import EventParser
from pero.plugin_loader import load_plugins
from pero.router import EventDispatcher
from pero.websocket import WebSocketClient

_log = get_log()


async def main():
    uri = CONFIG.ws_uri

    try:
        # 创建 WebSocket 客户端
        async with WebSocketClient(uri) as client:
            # 创建 BotAPI 实例
            api = BotAPI(client)
            # 加载所有插件
            await load_plugins()

            while client.is_connected:
                try:
                    # 接收消息
                    msg = await client.receive()

                    # 将解析事件和处理事件封装为异步任务并发执行
                    asyncio.create_task(_parse_and_dispatch_event(msg, api))

                except Exception as e:
                    _log.error(f"Error during message handling: {e}")
                    _log.error(traceback.format_exc())
    except Exception as e:
        _log.error(f"Error during WebSocket connection: {e}")


async def _parse_and_dispatch_event(msg: str, api: BotAPI):
    """解析事件并处理事件"""
    try:
        # 解析事件
        event = await EventParser.parse_event(msg)

        # 处理事件
        await EventDispatcher.dispatch(event, api)

    except Exception as e:
        _log.error(f"Error during event processing: {e}")
        _log.error(traceback.format_exc())


# 运行客户端
if __name__ == "__main__":
    asyncio.run(main())
