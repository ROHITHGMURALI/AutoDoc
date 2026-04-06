import asyncio
import threading
import time
from collections import deque

from langchain_core.rate_limiters import BaseRateLimiter


class MinuteRateLimiter(BaseRateLimiter):
    """
    Hard-cap rate limiter: allows up to `max_requests` calls within any
    rolling `window_seconds` window. Once the cap is reached, blocks until
    enough time has elapsed for the oldest request to fall outside the window.

    Implements the LangChain BaseRateLimiter protocol (acquire / aacquire).
    """

    def __init__(self, max_requests: int = 49, window_seconds: int = 60):
        self.max_requests = max_requests
        self.window_seconds = window_seconds
        self._timestamps: deque = deque()
        self._lock = threading.Lock()

    def _compute_wait(self) -> float:
        """Return seconds to sleep (0 if a slot is available)."""
        now = time.monotonic()
        while self._timestamps and now - self._timestamps[0] >= self.window_seconds:
            self._timestamps.popleft()
        if len(self._timestamps) < self.max_requests:
            return 0.0
        return self._timestamps[0] + self.window_seconds - now

    def acquire(self, *, blocking: bool = True) -> bool:
        while True:
            with self._lock:
                wait = self._compute_wait()
                if wait <= 0:
                    self._timestamps.append(time.monotonic())
                    return True
                if not blocking:
                    return False
            print(
                f"Rate limit reached ({self.max_requests} req/{self.window_seconds}s). "
                f"Waiting {wait:.1f}s..."
            )
            time.sleep(wait)

    async def aacquire(self, *, blocking: bool = True) -> bool:
        while True:
            with self._lock:
                wait = self._compute_wait()
                if wait <= 0:
                    self._timestamps.append(time.monotonic())
                    return True
                if not blocking:
                    return False
            print(
                f"Rate limit reached ({self.max_requests} req/{self.window_seconds}s). "
                f"Waiting {wait:.1f}s..."
            )
            await asyncio.sleep(wait)
