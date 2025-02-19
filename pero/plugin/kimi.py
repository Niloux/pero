from openai import OpenAI

from pero.core.api import PERO_API as pero
from pero.core.message_adapter import MessageAdapter
from pero.core.message_parser import Message
from pero.plugin.plugin_manager import PluginBase, plugin, plugin_manager
from pero.utils.hot_config import hot_config
from pero.utils.logger import logger


class BaseChatPlugin(PluginBase):
    def __init__(self, model_name: str):
        self.config = hot_config
        self.model_name = model_name
        self._update_config()

    def _update_config(self):
        model_config = self.config.get("model", {}).get(self.model_name, {})
        self.client = OpenAI(api_key=model_config["api_key"], base_url=model_config["base_url"])
        self.system_content = model_config["system_content"]
        self.model = model_config["model"]

    def on_load(self):
        """插件加载时初始化OpenAI客户端"""
        logger.info(f"{self.__class__.__name__} plugin loaded successfully")

    def on_unload(self):
        """插件卸载时清理资源"""
        self.client = None
        logger.info(f"{self.__class__.__name__} plugin unloaded")

    async def chat(self, message: Message):
        """处理群消息"""
        try:
            # 获取任务追踪器
            task = plugin_manager.track_task(self.__class__.__name__)

            try:
                logger.info(f"收到消息: {message.content}")
                if not message.content:
                    return

                # 获取文本内容
                text = message.get_text()

                # 调用API获取回复
                result = await self._get_chat_response(text)
                logger.info(f"回复消息: {result}")

                # 发送群消息
                return await pero.post_message(message=message, text=result)
            finally:
                # 标记任务完成
                plugin_manager.complete_task(task)

        except Exception as e:
            logger.error(f"Error in {self.__class__.__name__} plugin: {e}")
            raise

    async def _get_chat_response(self, text: str) -> str:
        """调用ChatGPT API获取回复"""
        self._update_config()  # 每次调用API之前更新配置
        completion = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": self.system_content},
                {"role": "user", "content": text},
            ],
            temperature=0.3,
        )
        return completion.choices[0].message.content


@plugin(name="kimi", version="1.0", dependencies=[])  # 如果有依赖其他插件，在这里添加
class KimiChatPlugin(BaseChatPlugin):
    def __init__(self):
        super().__init__(model_name="kimi")

    @MessageAdapter.register("group", ["text", "at"], "kimi")
    async def chat(self, message: Message):
        return await super().chat(message)
