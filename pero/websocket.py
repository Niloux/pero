import asyncio
import datetime
import json
from typing import Dict

import websockets

from pero.utils.logger import logger
from pero.utils.queue import post_queue, recv_queue


class WebSocketClient:
    def __init__(self, uri: str):
        self.uri = uri
        self.websocket = None
        self.is_connected = False
        self.send_lock = asyncio.Lock()
        self.receive_lock = asyncio.Lock()

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
            logger.info(f"Connected to {self.uri}")

            # 启动处理接收和发送消息的任务
            self.receive_task = asyncio.create_task(self._receive_messages())
            self.post_task = asyncio.create_task(self._post_messages())

            await self._handle_lifecycle_event()
        except Exception as e:
            logger.error(f"Failed to connect to {self.uri}: {e}")
            self.is_connected = False

    async def _handle_lifecycle_event(self):
        """处理生命周期事件"""
        if not self.websocket:
            return

        response = await self.websocket.recv()
        logger.info(f"Received Lifecycle Event: {response}")

        # 在这里可以处理连接建立后的其他生命周期事件
        # 如：验证连接是否成功、获取认证信息等

    async def send(self, msg: Dict[str, str]):
        """发送消息到 WebSocket 服务端"""
        async with self.send_lock:
            if not self.websocket:
                logger.error("WebSocket not connected.")
                return
            try:
                await self.websocket.send(json.dumps(msg))
                logger.debug(f"Sent: {msg}")
            except Exception as e:
                logger.error(f"Error sending message: {e}")

    async def receive(self) -> Dict:
        """接收 WebSocket 消息"""
        async with self.receive_lock:
            if not self.websocket:
                logger.error("WebSocket not connected.")
                return ""
            try:
                response = await self.websocket.recv()
                response = json.loads(response)
                logger.debug(f"Received: {response}")
                return response
            except websockets.exceptions.ConnectionClosedOK:
                logger.info("WebSocket connection closed normally.")
                self.is_connected = False
                return ""
            except Exception as e:
                logger.error(f"Error receiving message: {e}")
                return ""

    async def close(self):
        """关闭 WebSocket 连接"""
        if self.websocket:
            await self.websocket.close()
            self.is_connected = False
            logger.info("WebSocket connection closed.")
        if hasattr(self, "receive_task"):
            self.receive_task.cancel()
            try:
                await self.receive_task
            except asyncio.CancelledError:
                logger.info("Receive task cancelled.")
        if hasattr(self, "post_task"):
            self.post_task.cancel()
            try:
                await self.post_task
            except asyncio.CancelledError:
                logger.info("Post task cancelled.")

    async def post(self, action, params=None):
        """发送 POST 请求

        Args:
            action (str): 请求的动作类型。
            params (dict, optional): 请求的参数。默认为 None。
            json (dict, optional): 请求的 JSON 数据。默认为 None。

        Returns:
            None
        """
        if not self.websocket:
            logger.error("WebSocket not connected.")
            return

        try:
            payload = {
                "action": action.replace("/", ""),
                "params": params,
                "echo": int(datetime.datetime.now().timestamp()),
            }

            logger.debug(f"Sent: {action=}, {payload=}")
            await self.send(payload)
            return
        except json.JSONDecodeError as e:
            logger.error(f"JSON encoding error: {e}")
            raise e
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            raise e

    async def _receive_messages(self):
        """不断接收 WebSocket 消息并放入 recv_queue"""
        while self.is_connected:
            try:
                message = await self.receive()
                if message:
                    await recv_queue.put(message)
            except Exception as e:
                logger.error(f"Error receiving message: {e}")

    async def _post_messages(self):
        """不断从 post_queue 中取出消息并进行 post"""
        while self.is_connected:
            try:
                action, params = await post_queue.get()
                await self.post(action, params)
            except Exception as e:
                logger.error(f"Error posting message: {e}")
