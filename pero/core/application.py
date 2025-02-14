import asyncio
import signal
from contextlib import AsyncExitStack
from typing import Optional, Set

from pero.cmd.command_manager import command_manager
from pero.core.dispatcher import EventHandler
from pero.core.event_parser import EventParser
from pero.core.task_manager import TaskManager
from pero.core.websocket import WebSocketClient
from pero.plugin_system.plugin_manager import plugin_manager
from pero.utils.config import config
from pero.utils.logger import logger


class Application:
    """应用程序主类"""

    def __init__(self):
        self.plugin_manager = plugin_manager
        self.command_manager = command_manager
        self.event_adapter = EventHandler()
        self.event_parser = EventParser()
        self.task_manager: Optional[TaskManager] = None
        self.websocket: Optional[WebSocketClient] = None
        self.running_tasks: Set[asyncio.Task] = set()
        self.exit_stack = AsyncExitStack()

    async def initialize(self):
        """初始化应用程序组件"""
        logger.info("Initializing application...")

        # 加载配置
        await self._load_config()

        # 初始化WebSocket客户端
        uri = config.get("ws_uri")
        self.websocket = await self.exit_stack.enter_async_context(WebSocketClient(uri))

        # 初始化任务管理器
        self.task_manager = TaskManager(self.event_adapter, self.event_parser)

        # 加载插件
        await self._load_plugins()

        # 加载命令
        await self._load_commands()

        logger.info("Application initialized successfully")

    async def _load_config(self):
        """加载配置文件"""
        try:
            # 这里可以添加配置验证逻辑
            required_configs = ["ws_uri", "plugin_dir", "cmd_dir"]
            for key in required_configs:
                if not config.get(key):
                    raise ValueError(f"Missing required config: {key}")
        except Exception as e:
            logger.error(f"Failed to load config: {e}")
            raise

    async def _load_plugins(self):
        """加载插件"""
        try:
            plugin_dir = config.get("plugin_dir", "plugins")
            self.plugin_manager.add_plugin_dir(plugin_dir)
            self.plugin_manager.discover_plugins()
            self.plugin_manager.load_plugins()
            # 启动插件目录监控
            self.plugin_manager.watch_plugin_dirs()
            logger.info(f"Plugins loaded from {plugin_dir}")
        except Exception as e:
            logger.error(f"Failed to load plugins: {e}")
            raise

    async def _load_commands(self):
        """加载命令"""
        try:
            cmd_dir = config.get("cmd_dir", "pero/cmd")
            self.command_manager.load_commands(cmd_dir)
            logger.info(f"Commands loaded from {cmd_dir}")
        except Exception as e:
            logger.error(f"Failed to load commands: {e}")
            raise

    def _create_tasks(self) -> Set[asyncio.Task]:
        """创建需要运行的异步任务"""
        tasks = {
            asyncio.create_task(self.websocket.receive_messages(), name="websocket_receive"),
            asyncio.create_task(self.websocket.post_messages(), name="websocket_post"),
            asyncio.create_task(self.task_manager.start(), name="task_manager"),
        }

        for task in tasks:
            task.add_done_callback(self.running_tasks.remove)
            self.running_tasks.add(task)

        return tasks

    async def _shutdown(self):
        """优雅关闭应用程序"""
        logger.info("Shutting down application...")

        # 取消所有运行中的任务
        for task in self.running_tasks:
            task.cancel()

        # 等待任务完成
        if self.running_tasks:
            await asyncio.gather(*self.running_tasks, return_exceptions=True)

        # 关闭插件管理器
        await self.plugin_manager.shutdown()

        # 关闭其他资源
        await self.exit_stack.aclose()

        logger.info("Application shutdown complete")

    async def run(self):
        """运行应用程序"""
        try:
            # 初始化应用
            await self.initialize()

            # 设置信号处理
            loop = asyncio.get_running_loop()
            for sig in (signal.SIGTERM, signal.SIGINT):
                loop.add_signal_handler(sig, lambda s=sig: asyncio.create_task(self._handle_signal(s)))

            # 创建并运行任务
            tasks = self._create_tasks()
            await asyncio.gather(*tasks)

        except asyncio.CancelledError:
            logger.info("Application cancelled")
        except Exception as e:
            logger.error(f"Application error: {e}")
            raise
        finally:
            await self._shutdown()

    async def _handle_signal(self, sig: signal.Signals):
        """处理系统信号"""
        logger.info(f"Received signal: {sig.name}")
        await self._shutdown()
