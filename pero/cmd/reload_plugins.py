import traceback
from typing import Dict

from pero.api import BotAPI
from pero.logger import get_log
from pero.plugin_loader import PluginReloader

_log = get_log()


async def reload_plugins(event: Dict, api: BotAPI):
    """处理重载命令"""
    # TODO:封装方法快速解析event["content"]中的消息类型和消息内容
    # 找出cmd指令
    for content in event.get("content"):
        if content.get("type") == "text":
            text = content.get("data").get("text")
            break
    if text == "/reload":
        try:
            loaded_plugins = await PluginReloader.reload_plugins()
            response = f"插件重载成功！已重载插件: {', '.join(loaded_plugins)}"
            # 回显消息
            # TODO:回显消息可以进一步封装
            if event.get("source_type") == "private":
                await api.post_private_msg(user_id=event.get("target"), text=response)
            elif event.get("source_type") == "group":
                await api.post_group_msg(group_id=event.get("target"), text=response)
        except Exception as e:
            error_msg = f"插件重载失败: {str(e)}"
            if event.get("source_type") == "private":
                await api.post_private_msg(user_id=event.get("target"), text=error_msg)
            elif event.get("source_type") == "group":
                await api.post_group_msg(group_id=event.get("target"), text=error_msg)
            _log.error(error_msg)
            _log.error(traceback.format_exc())
        return True
    return False
