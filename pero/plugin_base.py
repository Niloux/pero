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
