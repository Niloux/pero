from typing import Dict

from openai import OpenAI

from pero.api import BotAPI
from pero.config import CONFIG
from pero.logger import get_log
from pero.router import MessageAdapter

api_key = CONFIG.kimi_api

client = OpenAI(
    api_key=api_key,
    base_url="https://api.moonshot.cn/v1",
)


_log = get_log()


@MessageAdapter.register_message(
    message_type="at", source_type="group", sender_type="normal"
)
async def kimi_text(event: Dict, api: BotAPI):
    # 找出text消息
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
    await api.post_group_msg(
        group_id=event.get("target"), text=result, reply=event.get("reply")
    )
