import traceback
from typing import Dict

from pero.api import BotAPI
from pero.logger import get_log
from pero.plugin_loader import PluginReloader
from pero.utils.command import Parser, extract_text, send_response

_log = get_log()


async def reload_plugins(event: Dict, api: BotAPI) -> bool:
    """处理重载命令"""
    text = extract_text(event)

    # 解析命令
    try:
        command, command_text = Parser.parse(text)

        if command == "reload":
            # 处理重载命令
            if command_text.strip() == "":
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
            else:
                response = "命令参数无效！请不要在`/reload`命令后添加任何内容喵~"
                await send_response(event, api, response)
                return True
    except ValueError:
        # 如果解析失败，返回错误消息
        _log.error(f"无法解析命令: {text}")
        return False

    return False
