import asyncio
import importlib
import inspect
import json
import os
import pkgutil
import sys
import threading
import time
from concurrent.futures import ThreadPoolExecutor
from dataclasses import dataclass
from typing import Dict, List, Optional, Set

from pero.plugin_base import PluginBase
from pero.utils.hybrid_lock import HybridLock
from pero.utils.logger import logger


@dataclass
class PluginMeta:
    """插件元数据"""

    name: str
    version: str
    dependencies: List[str]
    module_path: str
    enabled: bool = True


class PluginTask:
    """插件任务封装"""

    def __init__(self, plugin_name: str):
        self.plugin_name = plugin_name
        self.start_time = time.time()
        self.completed = threading.Event()

    def mark_completed(self):
        self.completed.set()


class PluginManager:
    """插件管理器 - 使用单例模式"""

    _instance: Optional["PluginManager"] = None
    _lock = threading.Lock()

    def __new__(cls):
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = super().__new__(cls)
                    cls._instance._initialized = False
        return cls._instance

    def __init__(self):
        if self._initialized:
            return

        self._plugins: Dict[str, object] = {}  # 已加载的插件实例
        self._plugin_meta: Dict[str, PluginMeta] = {}  # 插件元数据
        self._active_tasks: Set[PluginTask] = set()  # 当前活跃的任务
        self._tasks_lock = HybridLock()
        self._reload_lock = HybridLock()
        self._executor = ThreadPoolExecutor()
        self._plugin_dirs: List[str] = []  # 插件目录列表
        self._file_observers: List[object] = []  # 文件监控器列表

        self._initialized = True

    @classmethod
    def get_instance(cls) -> "PluginManager":
        """获取插件管理器实例"""
        if cls._instance is None:
            cls._instance = PluginManager()
        return cls._instance

    def track_task(self, plugin_name: str) -> PluginTask:
        """跟踪插件任务"""
        task = PluginTask(plugin_name)
        with self._tasks_lock:
            self._active_tasks.add(task)
        return task

    def complete_task(self, task: PluginTask):
        """标记任务完成"""
        task.mark_completed()
        with self._tasks_lock:
            self._active_tasks.remove(task)

    def _resolve_dependencies(self) -> List[str]:
        """解析插件依赖关系,返回正确的加载顺序"""
        visited = set()
        load_order = []

        def visit(name):
            if name in visited:
                return
            visited.add(name)
            # 先加载依赖
            for dep in self._plugin_meta[name].dependencies:
                visit(dep)
            load_order.append(name)

        for name in self._plugin_meta:
            visit(name)
        return load_order

    def add_plugin_dir(self, plugin_dir: str):
        """添加插件目录"""
        abs_path = os.path.abspath(plugin_dir)
        if os.path.exists(abs_path) and abs_path not in self._plugin_dirs:
            self._plugin_dirs.append(abs_path)

    def discover_plugins(self):
        """自动发现并注册插件"""
        for plugin_dir in self._plugin_dirs:
            self._discover_in_dir(plugin_dir)

    def _discover_in_dir(self, plugin_dir: str):
        """在指定目录中发现插件"""
        # 确保目录在Python路径中
        if plugin_dir not in sys.path:
            sys.path.append(plugin_dir)

        # 遍历目录中的所有Python模块
        for finder, name, _ in pkgutil.iter_modules([plugin_dir]):
            try:
                # 动态导入模块
                module = importlib.import_module(name)

                # 查找模块中的插件类
                for item_name, item in inspect.getmembers(module):
                    if (
                        inspect.isclass(item)
                        and hasattr(item, "_is_plugin")
                        and item._meta.name not in self._plugin_meta
                    ):
                        logger.info(f"Discovered plugin: {item._meta.name}")
                        self.register_plugin(item._meta)

            except Exception as e:
                logger.error(f"Error discovering plugin {name}: {e}")

    async def _wait_plugin_tasks(self, plugin_name: str):
        """等待指定插件的所有任务完成"""
        while True:
            async with self._tasks_lock:
                active_tasks = {
                    task
                    for task in self._active_tasks
                    if task.plugin_name == plugin_name
                }
                if not active_tasks:
                    break
            # 等待所有任务的完成事件
            for task in active_tasks:
                await asyncio.wrap_future(self._executor.submit(task.completed.wait))

    def register_plugin(self, meta: PluginMeta):
        """注册插件元数据"""
        self._plugin_meta[meta.name] = meta

    def get_plugin(self, name: str) -> object:
        """获取插件实例"""
        return self._plugins.get(name)

    async def shutdown(self):
        """关闭插件管理器，清理资源"""
        logger.info("Shutting down plugin manager...")

        try:
            # 停止所有文件监控器
            for observer in self._file_observers:
                observer.stop()
                observer.join()
            self._file_observers.clear()

            # 等待所有活跃任务完成
            async with self._tasks_lock:
                active_tasks = list(self._active_tasks)
                if active_tasks:
                    logger.info(
                        f"Waiting for {len(active_tasks)} active tasks to complete..."
                    )
                    for task in active_tasks:
                        await asyncio.wait_for(
                            asyncio.wrap_future(
                                self._executor.submit(task.completed.wait)
                            ),
                            timeout=5.0,
                        )

            # 卸载所有插件
            for plugin_name, plugin in list(self._plugins.items()):
                try:
                    if hasattr(plugin, "on_unload"):
                        plugin.on_unload()
                    logger.info(f"Unloaded plugin: {plugin_name}")
                except Exception as e:
                    logger.error(f"Error unloading plugin {plugin_name}: {e}")

            # 清理插件列表
            self._plugins.clear()
            self._plugin_meta.clear()

            # 关闭线程池
            self._executor.shutdown(wait=True)

            logger.info("Plugin manager shutdown complete")

        except Exception as e:
            logger.error(f"Error during plugin manager shutdown: {e}")
            raise

    def watch_plugin_dirs(self):
        """监控插件目录变化"""

        def watch_directory():
            import watchdog.events
            import watchdog.observers

            class PluginHandler(watchdog.events.FileSystemEventHandler):
                def on_modified(self, event):
                    if event.src_path.endswith(".py"):
                        logger.info(f"Detected changes in {event.src_path}")
                        module_name = os.path.splitext(
                            os.path.basename(event.src_path)
                        )[0]
                        plugin_manager._reload_module(module_name)

            observer = watchdog.observers.Observer()
            for plugin_dir in self._plugin_dirs:
                observer.schedule(PluginHandler(), plugin_dir, recursive=False)
            observer.start()
            self._file_observers.append(observer)
            return observer

        self._executor.submit(watch_directory)

    def _reload_module(self, module_name: str):
        """重新加载模块及其包含的插件"""
        try:
            module = importlib.import_module(module_name)
            importlib.reload(module)

            # 重新加载模块中的所有插件
            for item_name, item in inspect.getmembers(module):
                if (
                    inspect.isclass(item)
                    and hasattr(item, "_is_plugin")
                    and item._meta.name in self._plugins
                ):
                    asyncio.run(self.reload_plugin(item._meta.name))

        except Exception as e:
            logger.error(f"Error reloading module {module_name}: {e}")

    def _load_plugin(self, plugin_name: str):
        """加载单个插件"""
        meta = self._plugin_meta[plugin_name]
        if not meta.enabled:
            return

        module = importlib.import_module(meta.module_path)
        # 查找标记了插件装饰器的类
        for name, obj in inspect.getmembers(module):
            if inspect.isclass(obj) and hasattr(obj, "_is_plugin"):
                instance = obj()
                self._plugins[plugin_name] = instance
                if hasattr(instance, "on_load"):
                    instance.on_load()
                break

    def load_plugins(self):
        """初始加载所有插件"""
        # 解析依赖关系,确定加载顺序
        load_order = self._resolve_dependencies()

        for plugin_name in load_order:
            try:
                self._load_plugin(plugin_name)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_name}: {e}")

    async def reload_plugin(self, plugin_name: str):
        """热重载插件"""
        async with self._reload_lock:
            # 等待该插件的所有任务完成
            await self._wait_plugin_tasks(plugin_name)

            # 调用插件的清理方法
            old_instance = self._plugins.get(plugin_name)
            if old_instance and hasattr(old_instance, "on_unload"):
                old_instance.on_unload()

            # 重新加载插件
            importlib.reload(
                importlib.import_module(self._plugin_meta[plugin_name].module_path)
            )
            self._load_plugin(plugin_name)


# 插件装饰器
def plugin(name: str, version: str, dependencies: List[str] = None):
    def decorator(cls):
        # 确保插件类继承自PluginBase
        if not issubclass(cls, PluginBase):
            cls.__bases__ = (PluginBase,) + cls.__bases__

        cls._is_plugin = True
        cls._meta = PluginMeta(
            name=name,
            version=version,
            dependencies=dependencies or [],
            module_path=cls.__module__,
        )
        return cls

    return decorator


# 示例配置类
class PluginConfig:
    """插件配置管理"""

    def __init__(self, config_dir: str):
        self.config_dir = config_dir
        os.makedirs(config_dir, exist_ok=True)

    def load_config(self, plugin_name: str) -> dict:
        """加载插件配置"""
        config_path = os.path.join(self.config_dir, f"{plugin_name}.json")
        if os.path.exists(config_path):
            with open(config_path, "r") as f:
                return json.load(f)
        return {}

    def save_config(self, plugin_name: str, config: dict):
        """保存插件配置"""
        config_path = os.path.join(self.config_dir, f"{plugin_name}.json")
        with open(config_path, "w") as f:
            json.dump(config, f, indent=4)


plugin_manager = PluginManager.get_instance()
