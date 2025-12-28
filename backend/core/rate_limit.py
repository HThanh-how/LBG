from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from fastapi import Request
from typing import Optional
import redis
from functools import wraps

from core.config import settings

limiter = Limiter(key_func=get_remote_address)

if settings.REDIS_URL:
    try:
        redis_client = redis.from_url(settings.REDIS_URL, decode_responses=True)
        limiter.storage = redis_client
    except Exception:
        pass


def get_client_ip(request: Request) -> str:
    if request.client:
        return request.client.host
    return "unknown"


def rate_limit(
    calls: int = 60,
    period: int = 60,
    per: Optional[str] = None,
):
    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            return await func(*args, **kwargs)
        wrapper._rate_limit = {"calls": calls, "period": period, "per": per}
        return wrapper
    return decorator


def setup_rate_limiting(app):
    app.state.limiter = limiter
    app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

