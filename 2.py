from typing import Callable, Any, Tuple
import functools
from collections import OrderedDict
import time

class Memoizer:
    def __init__(self, func: Callable[..., Any], max_cache_size: int = None, 
                 eviction_policy: str = 'LRU', expiry_time: float = None, 
                 custom_eviction: Callable[[dict, dict], None] = None):
        self.func = func
        self.max_cache_size = max_cache_size
        self.eviction_policy = eviction_policy.lower() if isinstance(eviction_policy, str) else 'custom'
        self.expiry_time = expiry_time
        self.custom_eviction = custom_eviction
        self.cache = OrderedDict() if self.eviction_policy == 'lru' else {}
        self.access_counts = {} if self.eviction_policy == 'lfu' else {}
        self.timestamps = {} if self.expiry_time is not None else {}
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs) -> Any:
        key = self._make_key(args, kwargs)
        current_time = time.time()
        if self.expiry_time is not None:
            self._remove_expired(current_time)
        if key in self.cache:
            if self.eviction_policy == 'lru':
                self.cache.move_to_end(key)
            elif self.eviction_policy == 'lfu':
                self.access_counts[key] = self.access_counts.get(key, 0) + 1
            if self.expiry_time is not None:
                self.timestamps[key] = current_time
            return self.cache[key]
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        if self.eviction_policy == 'lfu':
            self.access_counts[key] = self.access_counts.get(key, 0) + 1
        if self.expiry_time is not None:
            self.timestamps[key] = current_time
        if self.max_cache_size is not None and len(self.cache) > self.max_cache_size:
            if self.eviction_policy == 'lru':
                self.cache.popitem(last=False)
            elif self.eviction_policy == 'lfu':
                least_freq_key = min(self.access_counts, key=self.access_counts.get)
                del self.cache[least_freq_key]
                del self.access_counts[least_freq_key]
            elif self.eviction_policy == 'custom' and self.custom_eviction:
                self.custom_eviction(self.cache, self.access_counts)
        return result
    
    def _make_key(self, args: Tuple, kwargs: dict) -> Tuple:
        kwargs_items = sorted(kwargs.items())
        return (args, tuple(kwargs_items))
    
    def _remove_expired(self, current_time: float) -> None:
        expired_keys = [k for k, t in self.timestamps.items() if current_time - t > self.expiry_time]
        for key in expired_keys:
            del self.cache[key]
            if key in self.access_counts:
                del self.access_counts[key]
            del self.timestamps[key]
    
    def cache_stats(self) -> dict:
        return {
            'size': len(self.cache),
            'max_size': self.max_cache_size,
            'policy': self.eviction_policy,
            'expiry_time': self.expiry_time
        }

if __name__ == "__main__":
    def slow_fib(n: int) -> int:
        if n <= 1:
            return n
        return slow_fib(n-1) + slow_fib(n-2)
    def custom_eviction(cache: dict, access_counts: dict) -> None:
        if cache:
            min_key = min(cache, key=lambda k: cache[k])
            del cache[min_key]
            if min_key in access_counts:
                del access_counts[min_key]
    
    print("Test 4: Memoized Fibonacci with time-based expiry and custom eviction")
    memoized_fib = Memoizer(slow_fib, max_cache_size=3, expiry_time=2.0, custom_eviction=custom_eviction)
    print(f"Fib(10) = {memoized_fib(10)}")  
    print(f"Cache stats: {memoized_fib.cache_stats()}")
    time.sleep(3) 
    print(f"Fib(10) = {memoized_fib(10)}")  
    print(f"Cache stats: {memoized_fib.cache_stats()}")
    memoized_fib = Memoizer(slow_fib, max_cache_size=3, eviction_policy='custom', custom_eviction=custom_eviction)
    print(f"Fib(5) = {memoized_fib(5)}")  
    print(f"Fib(6) = {memoized_fib(6)}")  
    print(f"Fib(7) = {memoized_fib(7)}")   
    print(f"Fib(8) = {memoized_fib(8)}")   
    print(f"Cache stats: {memoized_fib.cache_stats()}")