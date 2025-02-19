import asyncio
from datetime import timedelta

from pero.core.api import PERO_API as pero


# 插件基类
class PluginBase:
    """插件基类，提供基本的生命周期方法"""

    def on_load(self):
        """插件加载时调用"""
        pass

    def on_unload(self):
        """插件卸载时调用"""
        pass

    def on_enable(self):
        """插件启用时调用"""
        pass

    def on_disable(self):
        """插件禁用时调用"""
        pass


# 命令基类
class CommandBase(PluginBase):
    """命令基类，提供统一的调用方法, 可以被子类重写"""

    async def execute(self, message, result):
        """执行命令"""
        return await pero.post_message(message=message, text=result)


# 定时任务基类
# TODO:依赖心跳包触发任务执行
class ScheduleBase(PluginBase):
    """定时任务基类，提供基本的生命周期方法和调度功能"""

    def __init__(self):
        self._task = None
        self._interval = None

    def set_interval(self, interval: timedelta):
        """设置任务执行间隔时间"""
        self._interval = interval

    async def _run(self):
        """任务运行的内部方法"""
        while True:
            try:
                await self.execute()
            except Exception as e:
                self.on_error(e)
            await asyncio.sleep(self._interval.total_seconds())

    def on_load(self):
        """插件加载时调用"""
        super().on_load()
        if self._interval:
            self._task = asyncio.create_task(self._run())

    def on_unload(self):
        """插件卸载时调用"""
        super().on_unload()
        if self._task:
            self._task.cancel()

    def on_enable(self):
        """插件启用时调用"""
        super().on_enable()
        if self._interval and not self._task:
            self._task = asyncio.create_task(self._run())

    def on_disable(self):
        """插件禁用时调用"""
        super().on_disable()
        if self._task:
            self._task.cancel()
            self._task = None

    async def execute(self):
        """执行任务的方法，子类需要实现此方法"""
        raise NotImplementedError("Subclasses must implement this method")

    def on_error(self, exception):
        """处理任务执行中的异常，子类可以重写此方法"""
        print(f"Error occurred during task execution: {exception}")
