import importlib
import sys
from pathlib import Path


def load_plugins(plugin_dir="plugins"):
    # 获取当前目录路径
    current_dir = Path(__file__).parent
    print(f"当前目录路径: {current_dir}")
    plugin_path = current_dir.parent / plugin_dir
    print(f"插件目录路径: {plugin_path}")

    # 确保插件目录在 sys.path 中
    if str(current_dir) not in sys.path:
        sys.path.append(str(current_dir))  # 将当前目录添加到 sys.path

    for module_file in plugin_path.glob("*/handler.py"):
        print(f"找到的文件: {module_file}")
        module_name = f"{plugin_dir}.{module_file.parent.name}.handler"
        try:
            importlib.import_module(module_name)  # 导入插件模块
            print(f"已加载插件: {module_file.parent.name}")
        except ModuleNotFoundError:
            print(f"无法找到插件: {module_file.parent.name}")
