from typing import Dict

from openai import OpenAI

from pero.core.message_adapter import MessageAdapter
from pero.plugin.plugin_manager import PluginBase, plugin, plugin_manager
from pero.utils.api import PERO_API
from pero.utils.config import config
from pero.utils.logger import logger


class BaseChatPlugin(PluginBase):
    def __init__(self, api_base_url: str, api_key: str):
        self.client = OpenAI(api_key=api_key, base_url=api_base_url)
        self.api_key = api_key

    def on_load(self):
        """插件加载时初始化OpenAI客户端"""
        logger.info(f"{self.__class__.__name__} plugin loaded successfully")

    def on_unload(self):
        """插件卸载时清理资源"""
        self.client = None
        logger.info(f"{self.__class__.__name__} plugin unloaded")

    async def chat(self, event: Dict):
        """处理群消息"""
        try:
            # 获取任务追踪器
            task = plugin_manager.track_task(self.__class__.__name__)

            try:
                logger.info(f"收到消息: {event}")
                # 提取文本消息
                text = self._extract_text(event)
                if not text:
                    return

                # 调用API获取回复
                result = await self._get_chat_response(text)
                logger.info(f"回复消息: {result}")

                # 发送群消息
                return await PERO_API.post_msg(event, text=result, reply=event.get("reply"))
            finally:
                # 标记任务完成
                plugin_manager.complete_task(task)

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__} plugin: {e}")
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


@plugin(name="kimi_chat", version="1.0", dependencies=[])  # 如果有依赖其他插件，在这里添加
class KimiChatPlugin(BaseChatPlugin):
    def __init__(self):
        super().__init__(api_base_url="https://api.moonshot.cn/v1", api_key=config.kimi_api)

    @MessageAdapter.register("group", ["text", "at"], "kimi_chat")
    # @MessageAdapter.register("private", ["text"], "kimi_chat")
    async def chat(self, event: Dict):
        return await super().chat(event)
