import datetime
import json as Json
from typing import Dict

import websockets

from pero.logger import get_log

_log = get_log()


class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.is_connected = False

    async def __aenter__(self):
        """进入异步上下文管理器"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_value, traceback):
        """退出异步上下文管理器"""
        await self.close()

    async def connect(self):
        """建立 WebSocket 连接"""
        try:
            self.websocket = await websockets.connect(self.uri)
            self.is_connected = True
            _log.info(f"Connected to {self.uri}")
            await self._handle_lifecycle_event()
        except Exception as e:
            _log.error(f"Failed to connect to {self.uri}: {e}")
            self.is_connected = False

    async def _handle_lifecycle_event(self):
        """处理生命周期事件"""
        if not self.websocket:
            return

        response = await self.websocket.recv()
        _log.info(f"Received Lifecycle Event: {response}")

        # 在这里可以处理连接建立后的其他生命周期事件
        # 如：验证连接是否成功、获取认证信息等

    async def send(self, msg: Dict[str, str]):
        """发送消息到 WebSocket 服务端"""
        if not self.websocket:
            _log.error("WebSocket not connected.")
            return
        try:
            await self.websocket.send(Json.dumps(msg))
            _log.info(f"Sent: {msg}")
        except Exception as e:
            _log.error(f"Error sending message: {e}")

    async def receive(self) -> str:
        """接收 WebSocket 消息"""
        if not self.websocket:
            _log.error("WebSocket not connected.")
            return ""
        try:
            response = await self.websocket.recv()
            _log.debug(f"Received: {response}")
            return response
        except Exception as e:
            _log.error(f"Error receiving message: {e}")
            return ""

    async def close(self):
        """关闭 WebSocket 连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            _log.info("WebSocket connection closed.")

    async def post(self, action, params=None, json=None):
        """发送 POST 请求

        Args:
            action (str): 请求的动作类型。
            params (dict, optional): 请求的参数。默认为 None。
            json (dict, optional): 请求的 JSON 数据。默认为 None。

        Returns:
            None
        """
        if not self.websocket:
            _log.error("WebSocket not connected.")
            return

        try:
            payload = {
                "action": action.replace("/", ""),
                "params": params if params is not None else json,
                "echo": int(datetime.datetime.now().timestamp()),
            }

            _log.debug(f"Sent: {action=}, {payload=}")
            await self.send(payload)
            # response = Json.loads(await self.websocket.recv())
            # _log.debug(f"Recv: {response=}")
            # return response
            return None
        except Json.JSONDecodeError as e:
            _log.error(f"JSON encoding error: {e}")
            raise e
        except Exception as e:
            _log.error(f"Error sending message: {e}")
            raise e
