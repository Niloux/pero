import asyncio
import threading


class HybridLock:
    """混合锁，支持同步和异步代码"""

    def __init__(self):
        self._lock = threading.Lock()
        self._async_lock = asyncio.Lock()

    def acquire(self):
        self._lock.acquire()

    def release(self):
        self._lock.release()

    async def acquire_async(self):
        await self._async_lock.acquire()

    def release_async(self):
        self._async_lock.release()

    def __enter__(self):
        self.acquire()

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.release()

    async def __aenter__(self):
        await self.acquire_async()

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        self.release_async()
