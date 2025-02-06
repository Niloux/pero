from pero.message import GroupMessage, PrivateMessage
from pero.api import BotAPI
from pero.logger import get_log
from pero.plugins_base import PluginBase

_log = get_log()


class Test1(PluginBase):
    def __init__(self, api: BotAPI):
        super().__init__(api)

    async def on_group_message(self, msg: GroupMessage):
        _log.info(f"Test Plugin: Received Group Message: {msg}")

    async def on_private_message(self, msg: PrivateMessage):
        if msg.raw_message == "hello":
            await self.api.send_private_msg(
                user_id=msg.user_id, reply=msg.message_id, message="hello"
            )

    async def on_notice(self, msg):
        _log.info(f"Test Plugin: Received Notice: {msg}")

    async def on_request(self, msg):
        _log.info(f"Test Plugin: Received Request: {msg}")
