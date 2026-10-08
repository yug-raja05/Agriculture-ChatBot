import time
import logging
import asyncio
import hashlib
import json
from typing import Any, Callable, Dict, Optional, List
from app.core.database import db_manager

logger = logging.getLogger(__name__)

class ServiceCacheException(Exception):
    pass

async def execute_with_retry_and_cache(
    cache_key_dict: Dict[str, Any],
    collection_name: str,
    api_call_func: Callable[[], Any],
    cache_ttl_seconds: int = 86400,  # 24 hours default
    max_retries: int = 3,
    initial_delay: float = 1.0
) -> Any:
    """
    Executes an API call with automatic retries and exponential backoff.
    If the call succeeds, updates the MongoDB cache.
    If the call fails after retries, attempts to fall back to the MongoDB cache.
    If no cache exists, raises ServiceCacheException.
    """
    # 1. Generate a deterministic query key hash
    key_str = json.dumps(cache_key_dict, sort_keys=True)
    key_hash = hashlib.sha256(key_str.encode("utf-8")).hexdigest()
    
    db = db_manager.db
    
    # 2. Try the live API call with retries
    delay = initial_delay
    last_error = None
    
    for attempt in range(1, max_retries + 1):
        try:
            logger.info(f"Attempting API call for {collection_name} (Attempt {attempt}/{max_retries})...")
            # If the api_call_func is a coroutine, await it; otherwise call it synchronously
            if asyncio.iscoroutinefunction(api_call_func):
                result = await api_call_func()
            else:
                result = api_call_func()
                
            # If successful, cache the result and return it
            if db is not None:
                try:
                    await db[collection_name].update_one(
                        {"_id": key_hash},
                        {
                            "$set": {
                                "query_params": cache_key_dict,
                                "result": result,
                                "cached_at": time.time(),
                                "expires_at": time.time() + cache_ttl_seconds
                            }
                        },
                        upsert=True
                    )
                    logger.info(f"Cached fresh API response in MongoDB collection '{collection_name}' under key {key_hash[:8]}")
                except Exception as cache_err:
                    logger.error(f"Failed to write cache to MongoDB: {cache_err}")
            
            return result
            
        except Exception as e:
            last_error = e
            logger.warning(f"API call failed on attempt {attempt} for {collection_name}: {e}")
            
            # Fast-fail for authentication errors
            if hasattr(e, "code") and e.code in (401, 403):
                logger.error("Authentication failed (401/403). Skipping retries.")
                break
                
            if attempt < max_retries:
                await asyncio.sleep(delay)
                delay *= 2  # Exponential backoff
                
    # 3. If API fails, attempt cache fallback
    logger.error(f"API calls exhausted. Attempting cache fallback for key {key_hash[:8]} in collection {collection_name}...")
    if db is not None:
        try:
            cache_entry = await db[collection_name].find_one({"_id": key_hash})
            if cache_entry:
                cached_at = cache_entry.get("cached_at", 0)
                age = time.time() - cached_at
                logger.info(f"Fallback SUCCESS: Retrieved cached value from '{collection_name}' (Age: {age:.1f}s)")
                res = cache_entry["result"]
                if isinstance(res, dict):
                    res["_from_cache"] = True
                    res["cache_age_seconds"] = age
                return res
        except Exception as db_err:
            logger.error(f"Error querying cache database: {db_err}")
            
    # 4. No cache available and API failed
    error_msg = f"API service failed and no cached data is available for parameters: {cache_key_dict}. Last error: {last_error}"
    logger.critical(error_msg)
    raise ServiceCacheException(error_msg)
