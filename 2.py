from typing import Callable, Any, Tuple
import functools
from collections import OrderedDict

class Memoizer:
    def __init__(self, func: Callable[..., Any], max_cache_size: int = None):
        self.func = func
        self.max_cache_size = max_cache_size
        self.cache = OrderedDict()
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs) -> Any:
        key = self._make_key(args, kwargs)
        if key in self.cache:
            self.cache.move_to_end(key)
            return self.cache[key]
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        if self.max_cache_size is not None and len(self.cache) > self.max_cache_size:
            self.cache.popitem(last=False)
        return result
    
    def _make_key(self, args: Tuple, kwargs: dict) -> Tuple:
        kwargs_items = sorted(kwargs.items())
        return (args, tuple(kwargs_items))

if __name__ == "__main__":
    def slow_fib(n: int) -> int:
        if n <= 1:
            return n
        return slow_fib(n-1) + slow_fib(n-2)
    
    memoized_fib = Memoizer(slow_fib, max_cache_size=3)
    print("Test 2: Memoized Fibonacci with LRU cache (size=3)")
    print(f"Fib(10) = {memoized_fib(10)}") 
    print(f"Fib(11) = {memoized_fib(11)}") 
    print(f"Fib(12) = {memoized_fib(12)}")  
    print(f"Fib(10) = {memoized_fib(10)}")  
    print(f"Fib(13) = {memoized_fib(13)}")  
    print(f"Fib(11) = {memoized_fib(11)}") 