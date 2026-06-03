"""
Predict-result cache backed by Redis DB 2.

DB 0 — Celery broker
DB 1 — Celery result backend
DB 2 — Predict cache  ← this module

All public functions degrade gracefully: if Redis is unavailable they
return None / no-op so the API continues serving without caching.
"""

import hashlib
import json
import logging

import redis

from core.config import settings

logger = logging.getLogger("kca.predict.cache")

_PREFIX = "predict:"


def _client() -> redis.Redis:
    return redis.from_url(settings.REDIS_CACHE_URL, decode_responses=True)


def make_key(payload: dict) -> str:
    """Deterministic 16-char hex key from the full sorted payload."""
    canonical = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return _PREFIX + hashlib.sha256(canonical.encode()).hexdigest()[:16]


def get(key: str) -> dict | None:
    try:
        value = _client().get(key)
        return json.loads(value) if value else None
    except Exception as exc:
        logger.warning("cache GET failed (%s) — skipping cache", exc)
        return None


def set(key: str, value: dict) -> None:
    try:
        _client().setex(key, settings.PREDICT_CACHE_TTL, json.dumps(value))
    except Exception as exc:
        logger.warning("cache SET failed (%s) — result not cached", exc)


def flush() -> int:
    """Delete all predict cache entries. Call after a successful model retrain."""
    try:
        r = _client()
        keys = r.keys(f"{_PREFIX}*")
        count = r.delete(*keys) if keys else 0
        logger.info("predict cache flushed — %d entries removed", count)
        return count
    except Exception as exc:
        logger.warning("cache FLUSH failed (%s)", exc)
        return 0
