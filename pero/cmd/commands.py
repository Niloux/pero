from pero.cmd.command_base import Command
from pero.cmd.command_registry import CommandRegistry

# from pero.plugin_loader import PluginReloader


class BaseCommand(Command, metaclass=CommandRegistry):
    command_name = None


class HelloCommand(BaseCommand):
    command_name = "hello"

    async def execute(self) -> str:
        return "Hello, world!"


class ByeCommand(BaseCommand):
    command_name = "bye"

    async def execute(self) -> str:
        return "Goodbye, world!"


# class Reload(BaseCommand):
#     command_name = "reload"

#     async def execute(self) -> str:
#         """处理重载命令"""
#         try:
#             if self.text.strip() == "":
#                 try:
#                     loaded_plugins = await PluginReloader.reload_plugins()
#                     response = f"插件重载成功！已重载插件: {', '.join(loaded_plugins)}"
#                     return response
#                 except Exception as e:
#                     error_msg = f"插件重载失败: {str(e)}"
#                     logger.error(error_msg)
#                     logger.error(traceback.format_exc())
#                     return error_msg
#             else:
#                 response = "命令参数无效！请不要在`/reload`命令后添加任何内容喵~"
#                 return response
#         except ValueError:
#             # 如果解析失败，返回错误消息
#             error_msg = f"无法解析命令: {self.text}"
#             logger.error(error_msg)
#             return error_msg
