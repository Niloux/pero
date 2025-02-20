"""发布订阅框架"""

import asyncio
from collections import defaultdict
from typing import Any, Callable, Dict, List, Optional, Tuple, TypeVar

from pero.core.common import Message, MessagePriority
from pero.utils.logger import logger

T = TypeVar("T")


class PubSubError(Exception):
    """基础异常类"""

    pass


class SubscriptionError(PubSubError):
    """订阅相关错误"""

    pass


class PublishError(PubSubError):
    """发布相关错误"""

    pass


class PubSub:
    _instance = None

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super(PubSub, cls).__new__(cls)
        return cls._instance

    def __init__(self, max_subscribers: int = 100):
        """
        初始化发布订阅系统

        Args:
            max_subscribers: 每个消息类型的最大订阅者数量
        """
        if not hasattr(self, "_initialized"):
            self._subscribers: Dict[str, List[Tuple[Callable[[Message], None], MessagePriority]]] = defaultdict(list)
            self._callback_index: Dict[Callable[[Message], None], str] = {}  # 反向索引
            self._max_subscribers = max_subscribers
            self._locks: Dict[str, asyncio.Lock] = defaultdict(asyncio.Lock)  # 每个 topic 一个独立的锁
            self._initialized = True

    @classmethod
    def get_instance(cls) -> "PubSub":
        if cls._instance is None:
            cls._instance = PubSub()
        return cls._instance

    async def publish(self, topic: str, data: Any, priority: MessagePriority = MessagePriority.NORMAL) -> None:
        """
        发布消息

        Args:
            topic: 消息类型
            data: 消息数据
            priority: 消息优先级

        Raises:
            PublishError: 发布过程中出现错误
        """
        try:
            message = Message(topic=topic, data=data, priority=priority)
            logger.info(f"Publishing message: {message}")

            # 使用 topic 对应的锁
            async with self._locks[topic]:
                if topic in self._subscribers:
                    # 根据优先级对订阅者进行排序
                    subscribers = sorted(self._subscribers[topic], key=lambda x: x[1].value, reverse=True)

                    for callback, priority in subscribers:
                        try:
                            await asyncio.create_task(callback(message))
                        except Exception as e:
                            logger.error(f"Error delivering message to subscriber: {e}")

        except Exception as e:
            raise PublishError(f"Failed to publish message: {e}")

    def subscribe(
        self, topic: str, callback: Callable[[Message], None], priority: MessagePriority = MessagePriority.NORMAL
    ) -> None:
        """
        订阅消息

        Args:
            topic: 消息类型
            callback: 回调函数
            priority: 订阅者优先级

        Raises:
            SubscriptionError: 订阅过程中出现错误
        """
        try:
            if len(self._subscribers[topic]) >= self._max_subscribers:
                raise SubscriptionError(f"Maximum subscribers ({self._max_subscribers}) reached for {topic}")

            # 存储回调函数和优先级
            self._subscribers[topic].append((callback, priority))
            # 反向索引更新
            self._callback_index[callback] = topic
            logger.info(f"New subscription added for {topic}")

        except Exception as e:
            raise SubscriptionError(f"Failed to subscribe: {e}")

    def unsubscribe(self, callback: Callable[[Message], None]) -> None:
        """
        取消订阅

        Args:
            callback: 回调函数

        Raises:
            SubscriptionError: 取消订阅过程中出现错误
        """
        try:
            if callback in self._callback_index:
                topic = self._callback_index.pop(callback)
                # 删除该订阅者
                self._subscribers[topic] = [(cb, pri) for cb, pri in self._subscribers[topic] if cb != callback]
                # 如果该 topic 没有订阅者了，则删除这个话题
                if not self._subscribers[topic]:
                    del self._subscribers[topic]
                logger.info(f"Subscription removed for {topic}")
            else:
                logger.warning("Callback not found in any topic subscriptions.")

        except Exception as e:
            raise SubscriptionError(f"Failed to unsubscribe: {e}")

    def get_subscriber_count(self, topic: str) -> int:
        """获取特定话题的订阅者数量"""
        return len(self._subscribers.get(topic, []))

    def clear_subscribers(self, topic: Optional[str] = None) -> None:
        """清除所有订阅者或指定类型的订阅者"""
        if topic:
            self._subscribers.pop(topic, None)
        else:
            self._subscribers.clear()
