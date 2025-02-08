import asyncio
import traceback

from pero.config import Config
from pero.logger import get_log
from pero.plugin_loader import load_plugins
from pero.router import router
from pero.websocket import WebSocketClient

_log = get_log()
CONFIG = Config("config.yaml")


async def main():
    uri = CONFIG.ws_uri

    try:
        # 创建 WebSocket 客户端
        async with WebSocketClient(uri) as client:
            # 创建BotAPI实例
            # api = BotAPI(client)
            # 加载所有插件
            load_plugins()
            while client.is_connected:
                try:
                    # 接收消息
                    msg = await client.receive()
                    # 解析消息类型, 处理消息
                    router.handle(msg)

                except Exception as e:
                    _log.error(f"Error during message handling: {e}")
                    _log.error("Detailed traceback:")
                    _log.error(traceback.format_exc())
    except Exception as e:
        _log.error(f"Error during WebSocket connection: {e}")


# 运行客户端
if __name__ == "__main__":
    asyncio.run(main())
