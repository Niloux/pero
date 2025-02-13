from typing import Dict

from openai import OpenAI

from pero.api import PERO_API
from pero.message_adapter import MessageAdapter
from pero.utils.config import config
from pero.utils.logger import logger

api_key = config.kimi_api

client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1",
)


@MessageAdapter.register_handler("message", "at")
async def kimi_text(event: Dict):
    # 找出text消息
    if event.get("sender_type") != "private":
        return await PERO_API.post_group_msg(
            group_id=event.get("target"),
            text="私人测试功能喵～",
            reply=event.get("reply"),
        )
    logger.info(f"kimi收到消息: {event}")
    for content in event.get("content"):
        if content.get("type") == "text":
            text = content.get("data").get("text")
            break
    completion = client.chat.completions.create(
        model="moonshot-v1-8k",
        messages=[
            {
                "role": "system",
                "content": "你是 Pero，由 Texasx3d 提供的人工智能助手，你更擅长中文和英文的对话。你是群友的好帮手！你很可爱！非常非常可爱！",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )

    result = completion.choices[0].message.content
    logger.info(f"kimi回复消息{result}")
    return await PERO_API.post_private_msg(
        user_id=event.get("target"), text=result, reply=event.get("reply")
    )
