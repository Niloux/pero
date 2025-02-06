import asyncio
import traceback

from pero.websocket import WebSocketClient
from pero.logger import get_log
from pero.config import Config
from pero.plugin_manager import PluginManager
from pero.handler import Handler
from pero.api import BotAPI
from pero.message import GroupMessage, PrivateMessage

_log = get_log()
CONFIG = Config("config.yaml")
handler = Handler()
# 创建plugins_manager实例
plugin_manager = PluginManager(plugin_dir="plugins")


# 注册所有消息类型
@handler.group_event()
async def on_group_message(msg: GroupMessage):
    await plugin_manager.handle_group_message(msg)


@handler.private_event()
async def on_private_message(msg: PrivateMessage):
    await plugin_manager.handle_private_message(msg)


@handler.notice_event
async def on_notice(msg):
    await plugin_manager.handle_notice(msg)


@handler.request_event
async def on_request(msg):
    await plugin_manager.handle_request(msg)


async def main():
    uri = CONFIG.ws_uri

    try:
        # 创建 WebSocket 客户端
        async with WebSocketClient(uri) as client:
            # 创建BotAPI实例
            api = BotAPI(client)
            # 加载所有插件
            plugin_manager.load_plugins(api)
            while client.is_connected:
                try:
                    # 接收消息
                    msg = await client.receive()
                    await handler.handle_msg(msg)
                except Exception as e:
                    _log.error(f"Error during message handling: {e}")
                    _log.error("Detailed traceback:")
                    _log.error(traceback.format_exc())
    except Exception as e:
        _log.error(f"Error during WebSocket connection: {e}")


# 运行客户端
if __name__ == "__main__":
    asyncio.run(main())
