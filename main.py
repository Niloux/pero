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
            # 创建BotAPI实例
            api = BotAPI(client)
            # 加载所有插件
            await load_plugins()
            while client.is_connected:
                try:
                    # 接收消息
                    msg = await client.receive()
                    # 解析事件
                    event = await EventParser.parse_event(msg)
                    # 处理事件
                    await EventDispatcher.dispatch(event, api)

                except Exception as e:
                    _log.error(f"Error during message handling: {e}")
                    _log.error(traceback.format_exc())
    except Exception as e:
        _log.error(f"Error during WebSocket connection: {e}")


# 运行客户端
if __name__ == "__main__":
    asyncio.run(main())
