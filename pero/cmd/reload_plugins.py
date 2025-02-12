import traceback

from pero.cmd.command_manager import register_command
from pero.cmd.commander import Command
from pero.logger import get_log
from pero.plugin_loader import PluginReloader

_log = get_log()


@register_command("reload")
class ReloadCommand(Command):
    def __init__(self, command, text):
        super().__init__(command, text)

    """重载命令实现"""

    async def execute(self) -> str:
        """处理重载命令"""
        try:

            if self.command == "reload":
                # 处理重载命令
                if self.text.strip() == "":
                    try:
                        loaded_plugins = await PluginReloader.reload_plugins()
                        response = (
                            f"插件重载成功！已重载插件: {', '.join(loaded_plugins)}"
                        )
                        return response
                    except Exception as e:
                        error_msg = f"插件重载失败: {str(e)}"
                        _log.error(error_msg)
                        _log.error(traceback.format_exc())
                        return error_msg
                else:
                    response = "命令参数无效！请不要在`/reload`命令后添加任何内容喵~"
                    return response
        except ValueError:
            # 如果解析失败，返回错误消息
            error_msg = f"无法解析命令: {self.text}"
            _log.error(error_msg)
            return error_msg
