import json
import pickle
from functools import wraps
from flask import current_app
from app import redis_client


def cached(timeout=300, key_prefix="default"):
    """Decorator to cache function results in Redis"""

    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            cache_key = f"{key_prefix}:{f.__name__}:{str(args)}:{str(kwargs)}"

            try:
                cached_value = redis_client.get(cache_key)
                if cached_value:
                    return pickle.loads(cached_value)
            except Exception:
                pass

            result = f(*args, **kwargs)

            try:
                redis_client.setex(cache_key, timeout, pickle.dumps(result))
            except Exception:
                pass

            return result

        return decorated_function

    return decorator


def user_cached(timeout=300, key_prefix="user"):
    """Decorator to cache function results per user"""

    def decorator(f):
        @wraps(f)
        def decorated_function(user_id, *args, **kwargs):
            cache_key = f"{key_prefix}:{user_id}:{f.__name__}:{str(args)}:{str(kwargs)}"

            try:
                cached_value = redis_client.get(cache_key)
                if cached_value:
                    return pickle.loads(cached_value)
            except Exception:
                pass

            result = f(user_id, *args, **kwargs)

            try:
                redis_client.setex(cache_key, timeout, pickle.dumps(result))
            except Exception:
                pass

            return result

        return decorated_function

    return decorator


def delete_cache(pattern="*"):
    """Delete all keys matching pattern"""
    try:
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    except Exception:
        pass


def delete_user_cache(user_id, key_prefix="user"):
    """Delete all cached data for a user"""
    try:
        pattern = f"{key_prefix}:{user_id}:*"
        for key in redis_client.scan_iter(match=pattern):
            redis_client.delete(key)
    except Exception:
        pass


def cache_set(key, value, timeout=300):
    """Set a value in cache"""
    try:
        redis_client.setex(key, timeout, pickle.dumps(value))
    except Exception:
        pass


def cache_get(key, default=None):
    """Get a value from cache"""
    try:
        value = redis_client.get(key)
        if value:
            return pickle.loads(value)
    except Exception:
        pass
    return default


def cache_delete(key):
    """Delete a specific key from cache"""
    try:
        redis_client.delete(key)
    except Exception:
        pass


# Like/Comment fast operations using Redis


class LikeCache:
    """Ultra-fast like operations using Redis"""

    @staticmethod
    def get_like_key(post_id):
        return f"post:{post_id}:likes"

    @staticmethod
    def get_user_like_key(user_id, post_id):
        return f"user:{user_id}:liked:{post_id}"

    @staticmethod
    def is_liked(user_id, post_id):
        """Check if user liked post - O(1) operation"""
        try:
            return redis_client.sismember(LikeCache.get_like_key(post_id), str(user_id))
        except Exception:
            return False

    @staticmethod
    def like(user_id, post_id):
        """Add like - O(1) operation"""
        try:
            redis_client.sadd(LikeCache.get_like_key(post_id), str(user_id))
            redis_client.setex(
                LikeCache.get_user_like_key(user_id, post_id), 86400, "1"
            )
        except Exception:
            pass

    @staticmethod
    def unlike(user_id, post_id):
        """Remove like - O(1) operation"""
        try:
            redis_client.srem(LikeCache.get_like_key(post_id), str(user_id))
            redis_client.delete(LikeCache.get_user_like_key(user_id, post_id))
        except Exception:
            pass

    @staticmethod
    def get_count(post_id):
        """Get like count - O(1) operation"""
        try:
            return redis_client.scard(LikeCache.get_like_key(post_id))
        except Exception:
            return 0

    @staticmethod
    def set_count(post_id, count):
        """Set initial like count from DB"""
        try:
            redis_client.setex(f"post:{post_id}:like_count", 3600, str(count))
        except Exception:
            pass

    @staticmethod
    def increment_count(post_id):
        """Increment like count"""
        try:
            key = f"post:{post_id}:like_count"
            if redis_client.exists(key):
                redis_client.incr(key)
        except Exception:
            pass

    @staticmethod
    def decrement_count(post_id):
        """Decrement like count"""
        try:
            key = f"post:{post_id}:like_count"
            if redis_client.exists(key):
                redis_client.decr(key)
        except Exception:
            pass


class CommentCache:
    """Ultra-fast comment count caching"""

    @staticmethod
    def get_key(post_id):
        return f"post:{post_id}:comments"

    @staticmethod
    def increment(post_id):
        """Increment comment count"""
        try:
            redis_client.incr(CommentCache.get_key(post_id))
        except Exception:
            pass

    @staticmethod
    def get_count(post_id):
        """Get cached comment count"""
        try:
            count = redis_client.get(CommentCache.get_key(post_id))
            return int(count) if count else None
        except Exception:
            return None

    @staticmethod
    def set_count(post_id, count):
        """Set comment count from DB"""
        try:
            redis_client.setex(CommentCache.get_key(post_id), 3600, str(count))
        except Exception:
            pass
