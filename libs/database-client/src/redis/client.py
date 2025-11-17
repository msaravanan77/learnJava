"""
Redis Client for Caching and Message Queue
"""

import redis.asyncio as aioredis
import json
from typing import Any, Optional, List
from datetime import timedelta


class RedisClient:
    """Async Redis client for caching and pub/sub"""

    def __init__(self, host: str = "localhost", port: int = 6379, db: int = 0, password: Optional[str] = None):
        self.host = host
        self.port = port
        self.db = db
        self.password = password
        self.client: Optional[aioredis.Redis] = None

    async def connect(self):
        """Connect to Redis"""
        self.client = await aioredis.from_url(
            f"redis://{self.host}:{self.port}/{self.db}",
            password=self.password,
            encoding="utf-8",
            decode_responses=True
        )

    async def close(self):
        """Close Redis connection"""
        if self.client:
            await self.client.close()

    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        value = await self.client.get(key)
        if value:
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def set(
        self,
        key: str,
        value: Any,
        ttl: Optional[int] = None
    ) -> bool:
        """
        Set value in cache

        Args:
            key: Cache key
            value: Value to cache (will be JSON serialized)
            ttl: Time to live in seconds

        Returns:
            True if successful
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")

        # Serialize value to JSON
        serialized = json.dumps(value) if not isinstance(value, str) else value

        if ttl:
            return await self.client.setex(key, ttl, serialized)
        else:
            return await self.client.set(key, serialized)

    async def delete(self, key: str) -> int:
        """Delete key from cache"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        return await self.client.delete(key)

    async def exists(self, key: str) -> bool:
        """Check if key exists"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        return await self.client.exists(key) > 0

    async def increment(self, key: str, amount: int = 1) -> int:
        """Increment counter"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        return await self.client.incrby(key, amount)

    async def expire(self, key: str, seconds: int) -> bool:
        """Set expiration on key"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        return await self.client.expire(key, seconds)

    # List operations for message queue
    async def push_to_queue(self, queue_name: str, item: Any) -> int:
        """Push item to queue (right push)"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        serialized = json.dumps(item)
        return await self.client.rpush(queue_name, serialized)

    async def pop_from_queue(self, queue_name: str, timeout: int = 0) -> Optional[Any]:
        """
        Pop item from queue (blocking left pop)

        Args:
            queue_name: Queue name
            timeout: Blocking timeout in seconds (0 = block forever)

        Returns:
            Deserialized item or None if timeout
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")

        result = await self.client.blpop(queue_name, timeout=timeout)
        if result:
            _, value = result
            try:
                return json.loads(value)
            except json.JSONDecodeError:
                return value
        return None

    async def get_queue_length(self, queue_name: str) -> int:
        """Get length of queue"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        return await self.client.llen(queue_name)

    # Pub/Sub operations
    async def publish(self, channel: str, message: Any) -> int:
        """Publish message to channel"""
        if not self.client:
            raise RuntimeError("Redis client not connected")

        serialized = json.dumps(message) if not isinstance(message, str) else message
        return await self.client.publish(channel, serialized)

    async def subscribe(self, channel: str):
        """
        Subscribe to channel

        Returns:
            Async iterator of messages
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")

        pubsub = self.client.pubsub()
        await pubsub.subscribe(channel)

        try:
            async for message in pubsub.listen():
                if message['type'] == 'message':
                    data = message['data']
                    try:
                        yield json.loads(data)
                    except json.JSONDecodeError:
                        yield data
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.close()

    # Rate limiting
    async def check_rate_limit(
        self,
        key: str,
        max_requests: int,
        window_seconds: int
    ) -> bool:
        """
        Check rate limit using sliding window

        Args:
            key: Rate limit key (e.g., user_id)
            max_requests: Maximum requests allowed
            window_seconds: Time window in seconds

        Returns:
            True if within limit, False if exceeded
        """
        if not self.client:
            raise RuntimeError("Redis client not connected")

        current = await self.increment(key)

        if current == 1:
            await self.expire(key, window_seconds)

        return current <= max_requests


if __name__ == "__main__":
    import asyncio

    async def test():
        client = RedisClient()
        await client.connect()

        # Test caching
        await client.set("test_key", {"data": "value"}, ttl=60)
        value = await client.get("test_key")
        print(f"Cached value: {value}")

        # Test queue
        await client.push_to_queue("test_queue", {"task": "index_file", "file": "main.py"})
        item = await client.pop_from_queue("test_queue")
        print(f"Queue item: {item}")

        # Test rate limiting
        allowed = await client.check_rate_limit("user123", max_requests=10, window_seconds=60)
        print(f"Rate limit check: {allowed}")

        await client.close()

    asyncio.run(test())
