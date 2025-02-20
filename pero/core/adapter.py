"""事件适配器，从解析的事件中提取出topic然后发布"""

from typing import List

from pero.core.common import _Message
from pero.core.pubsub import PubSub


class Adapter:
    def __init__(self):
        self.pubsub = PubSub().get_instance()

    async def extract(self, message: _Message) -> List[str]:
        """将event_message按照功能规划转换为命令指令和聊天指令"""
        """命令指令和聊天指令不共存"""
        """命令指令优先"""
        topics = []
        # 命令指令
        if message.has_cmd:
            for name, _ in message.commands:
                topics.append("/cmd/" + name)
                return topics
        # 聊天指令，source为group且要有at或source为private, sender为friend
        else:
            # TODO: 未完成
            pass
