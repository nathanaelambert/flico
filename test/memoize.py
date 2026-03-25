#!/usr/bin/env python3
"""
Performance test for memoized get_flickr() and get_engine() functions.
Run: python test_memoization.py
"""

import time
from functools import wraps
import os
from typing import Literal

# Your memoize decorator (from previous response)
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

# Mock versions of your functions for testing (without real API/DB)
@memoize
def get_flickr():
    """Simulates expensive Flickr API setup."""
    print("Creating Flickr API instance... (expensive)")
    time.sleep(0.1)  # Simulate expensive operation
    return {"api_key": "fake_key", "secret": "fake_secret"}

@memoize
def get_engine(user: Literal["trainer", "crawler", "server", "dev"]):
    """Simulates expensive DB engine creation."""
    print(f"Creating engine for {user}... (expensive)")
    time.sleep(0.15)  # Simulate expensive DB connection
    return f"Engine(user={user})"

def benchmark_function(func, *args, iterations=1000, name="Function"):
    """Benchmark a function with repeated calls."""
    print(f"\n{'='*60}")
    print(f"Benchmarking {name}")
    print(f"{'='*60}")
    
    # First call (cache miss)
    print("\nFirst call (cache miss):")
    start = time.perf_counter()
    result1 = func(*args)
    first_time = time.perf_counter() - start
    print(f"Time: {first_time:.4f}s")
    
    # Repeated calls (cache hit)
    print(f"\n{iterations} repeated calls (cache hits):")
    start = time.perf_counter()
    for _ in range(iterations):
        result2 = func(*args)
    repeated_time = time.perf_counter() - start
    avg_per_call = repeated_time / iterations
    
    print(f"Total time: {repeated_time:.4f}s")
    print(f"Average per call: {avg_per_call:.6f}s ({avg_per_call*1000:.3f}ms)")
    
    # Verify same object returned
    print(f"\nSame object? {result1 is result2}")
    print(f"Objects equal? {result1 == result2}")
    
    return first_time, repeated_time, avg_per_call

def main():
    print("Memoization Performance Test")
    print("Note: Using mock functions with artificial delays\n")
    
    # Test get_flickr() - singleton
    first_flickr, total_flickr, avg_flickr = benchmark_function(
        get_flickr, name="get_flickr() (singleton)"
    )
    
    # Test get_engine() - per-user cache
    first_trainer, total_trainer, avg_trainer = benchmark_function(
        get_engine, "trainer", name="get_engine('trainer')"
    )
    
    first_crawler, total_crawler, avg_crawler = benchmark_function(
        get_engine, "crawler", name="get_engine('crawler')"
    )
    
    # Test cache clear and reuse
    print("\n" + "="*60)
    print("CACHE CLEAR TEST")
    print("="*60)
    
    get_flickr.cache_clear()
    get_engine.cache_clear()
    
    print("\nAfter cache clear - first calls again:")
    benchmark_function(get_flickr, name="get_flickr() (after clear)")
    benchmark_function(get_engine, "trainer", name="get_engine('trainer') (after clear)")
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"get_flickr():     1st={first_flickr:.4f}s, avg={avg_flickr:.1f}μs/call")
    print(f"get_engine():     1st={first_trainer:.4f}s, avg={avg_trainer:.1f}μs/call")
    print(f"Improvement:     {1000*avg_flickr/first_flickr:.0f}x faster on repeat calls!")

if __name__ == "__main__":
    main()