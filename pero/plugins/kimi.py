from typing import Dict

from openai import OpenAI

from pero.api import PERO_API
from pero.message_adapter import MessageAdapter
from pero.plugin_system import PluginBase, plugin, plugin_manager
from pero.utils.config import config
from pero.utils.logger import logger


@plugin(
    name="kimi_chat", version="1.0", dependencies=[]  # 如果有依赖其他插件，在这里添加
)
class KimiChatPlugin(PluginBase):
    def __init__(self):
        self.client = None
        self.api_key = None

    def on_load(self):
        """插件加载时初始化OpenAI客户端"""
        self.api_key = config.kimi_api
        self.client = OpenAI(
            api_key=self.api_key,
            base_url="https://api.moonshot.cn/v1",
        )
        logger.info("KimiChat plugin loaded successfully")

    def on_unload(self):
        """插件卸载时清理资源"""
        self.client = None
        logger.info("KimiChat plugin unloaded")

    @MessageAdapter.register("group", ["text", "at"], "kimi_chat")
    async def chat(self, event: Dict):
        """处理群消息"""
        try:
            # 获取任务追踪器
            task = plugin_manager.track_task("kimi_chat")

            try:
                logger.info(f"kimi收到消息: {event}")
                # 提取文本消息
                text = self._extract_text(event)
                if not text:
                    return

                # 调用API获取回复
                result = await self._get_chat_response(text)
                logger.info(f"kimi回复消息{result}")

                # 发送群消息
                return await PERO_API.post_group_msg(
                    group_id=event.get("target"), text=result, reply=event.get("reply")
                )
            finally:
                # 标记任务完成
                plugin_manager.complete_task(task)

        except Exception as e:
            logger.error(f"Error in KimiChat plugin: {e}")
            raise

    def _extract_text(self, event: Dict) -> str:
        """从事件中提取文本内容"""
        for content in event.get("content", []):
            if content.get("type") == "text":
                return content.get("data", {}).get("text", "")
        return ""

    async def _get_chat_response(self, text: str) -> str:
        """调用ChatGPT API获取回复"""
        completion = self.client.chat.completions.create(
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
        return completion.choices[0].message.content
