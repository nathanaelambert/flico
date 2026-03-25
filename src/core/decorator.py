from functools import wraps
import hashlib

def memoize(func):
    cache = {} 
    
    @wraps(func)
    def wrapper(*args, **kwargs):
        key = (args, frozenset(kwargs.items()))
        if key not in cache:
            cache[key] = func(*args, **kwargs)
        return cache[key]
    
    wrapper.cache_clear = lambda: cache.clear()
    return wrapper