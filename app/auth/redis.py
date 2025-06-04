import redis
from app.config import settings
from typing import Optional
import json

# Redis client
redis_client = redis.from_url(settings.redis_url, decode_responses=True)

async def store_refresh_token(user_id: str, refresh_token: str, expires_in: int) -> None:
    """Store refresh token in Redis with expiration"""
    key = f"refresh_token:{user_id}"
    await redis_client.setex(key, expires_in, refresh_token)

async def get_refresh_token(user_id: str) -> Optional[str]:
    """Get refresh token from Redis"""
    key = f"refresh_token:{user_id}"
    return await redis_client.get(key)

async def delete_refresh_token(user_id: str) -> None:
    """Delete refresh token from Redis"""
    key = f"refresh_token:{user_id}"
    await redis_client.delete(key)

async def add_token_to_blacklist(jti: str, expires_in: int) -> None:
    """Add token to blacklist with expiration"""
    key = f"blacklist:{jti}"
    await redis_client.setex(key, expires_in, "true")

async def is_token_blacklisted(jti: str) -> bool:
    """Check if token is blacklisted"""
    key = f"blacklist:{jti}"
    result = await redis_client.get(key)
    return result is not None