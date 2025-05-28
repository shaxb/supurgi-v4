import redis
import json
import asyncio
from loguru import logger
from typing import Dict, Any

# Global Redis connection
_redis_client = None

def initialize_redis(host: str = "localhost", port: int = 6379, db: int = 0) -> bool:
    """
    Initialize Redis connection.
    """
    global _redis_client
    try:
        _redis_client = redis.Redis(
            host=host, 
            port=port, 
            db=db, 
            decode_responses=True,  # Automatically decode responses to strings
            socket_connect_timeout=5,
            socket_timeout=5
        )
        # Test connection
        _redis_client.ping()
        logger.info(f"Redis connection established: {host}:{port}")
        return True
    except Exception as e:
        logger.error(f"Failed to connect to Redis: {e}")
        _redis_client = None
        return False

def shutdown_redis():
    """
    Close Redis connection.
    """
    global _redis_client
    if _redis_client:
        _redis_client.close()
        logger.info("Redis connection closed.")
        _redis_client = None

def is_redis_connected() -> bool:
    """
    Check if Redis is connected.
    """
    global _redis_client
    if not _redis_client:
        return False
    try:
        _redis_client.ping()
        return True
    except:
        return False

def publish_tick_data(symbol: str, tick_data: Dict[str, Any]) -> bool:
    """
    Publish tick data to Redis pub/sub channel.
    """
    global _redis_client
    if not _redis_client:
        logger.warning("Redis not connected. Cannot publish tick data.")
        return False
    
    try:
        channel = f"market_data:ticks:{symbol}"
        message = json.dumps(tick_data)
        _redis_client.publish(channel, message)
        logger.debug(f"Published tick for {symbol} to Redis channel: {channel}")
        return True
    except Exception as e:
        logger.error(f"Failed to publish tick data for {symbol}: {e}")
        return False

def get_redis_client():
    """
    Get the Redis client instance.
    """
    return _redis_client