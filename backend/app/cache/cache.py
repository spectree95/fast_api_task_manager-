from redis import Redis, RedisError
import json


class RedisCacheBackend: 
    
    def __init__(self, redis_url: str, cache_ttl_seconds: int | None = None ):
        self.redis = Redis.from_url(redis_url, socket_connect_timeout=0.3, socket_timeout=0.3) if redis_url else None
        self.cache_ttl_seconds = cache_ttl_seconds
        
    def set(self, key: str, value):
        if self.redis is None:
            return
        try:
            self.redis.set(name=key, value=json.dumps(value), ex=self.cache_ttl_seconds)
        except RedisError:
            pass  # Cache availability must not prevent database operations.
        
        
    def get(self, key: str):
        if self.redis is None:
            return None
        try:
            value = self.redis.get(name=key)
            if value is not None:
                return json.loads(value)
        except (RedisError, ValueError, TypeError):
            return None


    def delete(self, key: str):
        if self.redis is None:
            return
        try:
            self.redis.delete(key)
        except RedisError:
            pass

    def delete_prefix(self, prefix: str):
        if self.redis is None:
            return
        try:
            for key in self.redis.scan_iter(match=f"{prefix}*", count=100):
                self.redis.delete(key)
        except RedisError:
            pass
