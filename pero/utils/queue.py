from asyncio import Queue

# 从napcat收取消息，下发任务
recv_queue = Queue()
# 获取任务响应，回应napcat
post_queue = Queue()


"""
有需求了再进行功能扩充，例如消息优先级、限流、持久化等。
不过等到了那个时候就会换其他成熟的消息队列了......
"""
