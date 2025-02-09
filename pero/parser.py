from typing import Dict


class MessageParser:
    @staticmethod
    async def parse_message(event: Dict) -> Dict:
        """
        解析消息事件，根据消息的类型、来源、发送者等信息，转化为统一结构。
        """
        # 基本字段解析
        source_type = event.get("message_type")  # "private" 或 "group"
        sender_type = event.get("sub_type")  # "friend" 或 "other"

        # 提取消息类型列表
        message_types = []
        for msg in event.get("message", []):
            msg_type = msg.get("type")
            if msg_type:
                message_types.append(msg_type)

        # 提取消息内容
        content = event.get("message", [])

        # 构建最终统一结构
        return {
            "event": "message",
            "source_type": source_type,
            "sender_type": sender_type,
            "message_types": message_types,
            "content": content,
        }


# 示例解析
if __name__ == "__main__":
    # 示例消息体
    from text import a, b, c

    events = [a, b, c]

    for event in events:
        parsed_event = MessageParser.parse_message(event)
        print(parsed_event)
