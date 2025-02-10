from typing import Dict

from openai import OpenAI

from pero.api import BotAPI
from pero.config import Config
from pero.logger import get_log
from pero.router import MessageAdapter

config = Config("config.yaml")
api_key = config.kimi_api

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
                "content": "你是 Kimi，由 Moonshot AI 提供的人工智能助手，你更擅长中文和英文的对话。你会为用户提供安全，有帮助，准确的回答。同时，你会拒绝一切涉及恐怖主义，种族歧视，黄色暴力等问题的回答。Moonshot AI 为专有名词，不可翻译成其他语言。",
            },
            {"role": "user", "content": text},
        ],
        temperature=0.3,
    )

    result = completion.choices[0].message.content
    await api.post_group_msg(
        group_id=event.get("target"), text=result, reply=event.get("reply")
    )
