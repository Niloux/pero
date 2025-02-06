from pero.message import GroupMessage, PrivateMessage
from pero.logger import get_log

import json

_log = get_log()


class Handler:
    def __init__(self):
        self._group_event_handler = None
        self._private_event_handler = None
        self._notice_event_handler = None
        self._request_event_handler = None

    def group_event(self, types=None):
        def decorator(func):
            self._group_event_handler = (func, types)
            return func

        return decorator

    def private_event(self, types=None):
        def decorator(func):
            self._private_event_handler = (func, types)
            return func

        return decorator

    def notice_event(self, func):
        self._notice_event_handler = func
        return func

    def request_event(self, func):
        self._request_event_handler = func
        return func

    async def handle_group_event(self, msg: dict):
        if self._group_event_handler:
            func, types = self._group_event_handler
            if types is None or any(i["type"] in types for i in msg["message"]):
                msg = GroupMessage(msg)
                await func(msg)

    async def handle_private_event(self, msg: dict):
        if self._private_event_handler:
            func, types = self._private_event_handler
            if types is None or any(i["type"] in types for i in msg["message"]):
                msg = PrivateMessage(msg)
                await func(msg)

    async def handle_notice_event(self, msg: dict):
        if self._notice_event_handler:
            await self._notice_event_handler(msg)

    async def handle_request_event(self, msg: dict):
        if self._request_event_handler:
            await self._request_event_handler(msg)

    async def handle_post_msg(self, msg):
        _log.info(f"收到消息：{msg}")
        if msg["post_type"] == "message" or msg["post_type"] == "message_sent":
            if msg["message_type"] == "group":
                return await self.handle_group_event(msg)
            elif msg["message_type"] == "private":
                return await self.handle_private_event(msg)
            else:
                _log.error("这个报错说明message_type不属于group,private\n" + str(msg))
        elif msg["post_type"] == "notice":
            return await self.handle_notice_event(msg)
        elif msg["post_type"] == "request":
            return await self.handle_request_event(msg)
        elif msg["post_type"] == "meta_event":
            if msg["meta_event_type"] == "lifecycle":
                _log.info(f"机器人 {msg.get('self_id')} 成功启动")
            else:
                pass
        else:
            _log.error("这是一个错误，请反馈给开发者\n" + str(msg))

    async def handle_recv_msg(self, msg):
        _log.info(f"收到消息：{msg}")
        pass
        # TODO:处理收到的消息

    async def handle_msg(self, msg):
        msg = json.loads(msg)
        if "status" not in msg:
            return await self.handle_post_msg(msg)
        else:
            return await self.handle_recv_msg(msg)
