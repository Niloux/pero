import asyncio
from typing import Dict, Tuple


class DictQueue(asyncio.Queue):
    async def put(self, item: Dict) -> None:
        """向队列添加元素，并确保元素是 Dict 类型"""
        if not isinstance(item, dict):
            raise TypeError(f"Expected dict for recv_queue, got {type(item)}")
        await super().put(item)

    async def get(self) -> Dict:
        """从队列获取元素"""
        item = await super().get()
        return item


class TupleQueue(asyncio.Queue):
    async def put(self, item: Tuple[str, Dict]) -> None:
        """向队列添加元素，并确保元素是 (str, dict) 类型的元组"""
        if not (
            isinstance(item, tuple)
            and len(item) == 2
            and isinstance(item[0], str)
            and isinstance(item[1], dict)
        ):
            raise TypeError(
                f"Expected tuple (str, dict) for post_queue, got {type(item)}"
            )
        await super().put(item)

    async def get(self) -> Tuple[str, Dict]:
        """从队列获取元素"""
        item = await super().get()
        return item


# 从napcat收取消息，下发任务
recv_queue = DictQueue()
# 获取任务响应，回应napcat
post_queue = TupleQueue()

"""
有需求了再进行功能扩充，例如消息优先级、限流、持久化等。
不过等到了那个时候就会换其他成熟的消息队列了......
"""
