import traceback
from typing import Dict

from pero.api import BotAPI
from pero.logger import get_log
from pero.plugin_loader import PluginReloader

_log = get_log()


async def send_response(event: Dict, api: BotAPI, message: str):
    """发送回显消息"""
    if event.get("source_type") == "private":
        await api.post_private_msg(user_id=event.get("target"), text=message)
    elif event.get("source_type") == "group":
        await api.post_group_msg(group_id=event.get("target"), text=message)


def extract_text_from_event(event: Dict) -> str:
    """从event中提取text消息"""
    for content in event.get("content", []):
        if content.get("type") == "text":
            return content.get("data", {}).get("text", "")
    return ""


async def reload_plugins(event: Dict, api: BotAPI) -> bool:
    """处理重载命令"""
    text = extract_text_from_event(event)

    if text == "/reload":
        try:
            loaded_plugins = await PluginReloader.reload_plugins()
            response = f"插件重载成功！已重载插件: {', '.join(loaded_plugins)}"
            await send_response(event, api, response)
        except Exception as e:
            error_msg = f"插件重载失败: {str(e)}"
            await send_response(event, api, error_msg)
            _log.error(error_msg)
            _log.error(traceback.format_exc())
        return True
    return False
