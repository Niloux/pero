from pero.core.message_adapter import MessageAdapter
from pero.core.message_parser import Message
from pero.plugin.plugin_base import CommandBase
from pero.plugin.plugin_manager import plugin


@plugin(name="admin", version="1.0", dependencies=[])
class Admin(CommandBase):
    @MessageAdapter.register("group", ["cmd", "hello"], "admin")
    async def execute_hello(self, message: Message) -> str:
        return await super().execute(message, "hello world")

    @MessageAdapter.register("group", ["cmd", "world"], "admin")
    async def execute_world(self, message: Message) -> str:
        return await super().execute(message, "world hello")
