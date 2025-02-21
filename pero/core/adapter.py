"""事件适配器，从解析的事件中提取出topic然后发布"""

from pero.core.common import _Message
from pero.core.pubsub import PubSub


class Adapter:
    def __init__(self):
        self.pubsub = PubSub().get_instance()
        self.cmd_topic = "/cmd/"
        self.private_chat_topic = "/private_chat/"
        self.group_chat_topic = "/group_chat/"

    async def extract(self, message: _Message) -> str:
        """将event_message按照功能规划转换为命令指令和聊天指令"""
        """命令指令和聊天指令不共存"""
        """命令指令优先"""
        # 命令指令
        if message.has_cmd:
            return self.cmd_topic + message.command[0]
        # 聊天指令，type为group且要有at或type为private, sub_type为friend
        else:
            if message.type == "private" and message.sub_type == "friend":
                return self.private_chat_topic
            elif message.type == "group" and "at" in message.content_types:
                return self.group_chat_topic

    async def publish(self, topic: str, message: _Message):
        """发布消息到对应的topic"""
        await self.pubsub.publish(topic, message)

    async def run(self, message: _Message):
        """运行适配器"""
        topic = await self.extract(message)
        await self.publish(topic, message)
