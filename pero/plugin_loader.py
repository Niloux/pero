import importlib
import sys
from pathlib import Path

from pero.logger import get_log

_log = get_log()


async def load_plugins(plugin_dir="plugins"):
    """加载所有插件"""
    # 获取当前目录路径
    current_dir = Path(__file__).parent
    plugin_path = current_dir.parent / plugin_dir

    # 确保插件目录在 sys.path 中
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))
        _log.info(f"将当前目录添加到 sys.path: {current_dir}")

    # 加载插件
    loaded_plugins = []
    for module_file in plugin_path.glob("*/handler.py"):
        module_name = f"{plugin_dir}.{module_file.parent.name}.handler"
        try:
            importlib.import_module(module_name)  # 导入插件模块
            loaded_plugins.append(module_file.parent.name)
            _log.info(f"已加载插件: {module_file.parent.name}")
        except ModuleNotFoundError:
            _log.error(f"插件未找到: {module_file.parent.name}")
        except Exception as e:
            _log.error(f"加载插件 {module_file.parent.name} 时出错: {e}")

    return loaded_plugins


class PluginReloader:
    @staticmethod
    async def reload_plugins(plugin_dir="plugins"):
        """重新加载所有插件"""
        current_dir = Path(__file__).parent
        plugin_path = current_dir.parent / plugin_dir

        # 清理已加载的插件模块
        reloaded_plugins = []
        for name in list(sys.modules.keys()):
            if name.startswith(f"{plugin_dir}."):
                try:
                    del sys.modules[name]  # 卸载插件模块
                    _log.info(f"已卸载插件模块: {name}")
                except KeyError:
                    _log.warning(f"插件模块 {name} 卸载失败")

        # 重新加载插件
        if str(current_dir) not in sys.path:
            sys.path.append(str(current_dir))

        for module_file in plugin_path.glob("*/handler.py"):
            module_name = f"{plugin_dir}.{module_file.parent.name}.handler"
            try:
                module = importlib.import_module(module_name)
                importlib.reload(module)  # 强制重新加载模块
                reloaded_plugins.append(module_file.parent.name)
                _log.info(f"已重新加载插件: {module_file.parent.name}")
            except Exception as e:
                _log.error(f"重新加载插件 {module_file.parent.name} 失败: {e}")

        return reloaded_plugins
