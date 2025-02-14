import importlib
import sys
from pathlib import Path

from pero.utils.logger import logger


def load_plugins(plugin_dir="plugins"):
    """加载所有插件"""
    # 获取当前目录路径
    current_dir = Path(__file__).parent
    plugin_path = current_dir.parent / plugin_dir

    # 确保插件目录在 sys.path 中
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))

    # 加载插件
    loaded_plugins = []
    for module_file in plugin_path.glob("*/handler.py"):
        module_name = f"{plugin_dir}.{module_file.parent.name}.handler"
        try:
            importlib.import_module(module_name)  # 导入插件模块
            loaded_plugins.append(module_file.parent.name)
            logger.info(f"已加载插件: {module_file.parent.name}")
        except ModuleNotFoundError:
            logger.error(f"插件未找到: {module_file.parent.name}")
        except Exception as e:
            logger.error(f"加载插件 {module_file.parent.name} 时出错: {e}")

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
                    module = sys.modules[name]
                    # 这里假设每个插件都有一个 `deregister` 方法用于清理注册的函数
                    if hasattr(module, "deregister"):
                        module.deregister()
                    del sys.modules[name]  # 卸载插件模块
                    logger.info(f"已卸载插件模块: {name}")
                except KeyError:
                    logger.warning(f"插件模块 {name} 卸载失败")
                except Exception as e:
                    logger.error(f"卸载插件模块 {name} 时出错: {e}")

        # 确保重新加载父模块
        parent_modules = set(
            module_name.rsplit(".", 1)[0]
            for module_name in list(sys.modules.keys())
            if module_name.startswith(f"{plugin_dir}.")
        )
        for parent_module in parent_modules:
            if parent_module in sys.modules:
                del sys.modules[parent_module]
                logger.info(f"已卸载父插件模块: {parent_module}")

        # 重新加载插件
        if str(current_dir) not in sys.path:
            sys.path.append(str(current_dir))

        for module_file in plugin_path.glob("*/handler.py"):
            module_name = f"{plugin_dir}.{module_file.parent.name}.handler"
            parent_module_name = f"{plugin_dir}.{module_file.parent.name}"
            try:
                # 确保父模块被加载
                if parent_module_name not in sys.modules:
                    importlib.import_module(parent_module_name)
                module = importlib.import_module(module_name)
                importlib.reload(module)  # 强制重新加载模块
                reloaded_plugins.append(module_file.parent.name)
                logger.info(f"已重新加载插件: {module_file.parent.name}")
            except Exception as e:
                logger.error(f"重新加载插件 {module_file.parent.name} 失败: {e}")

        return reloaded_plugins
