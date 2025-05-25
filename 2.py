from typing import Callable, Any, Tuple
import functools

class Memoizer:
    def __init__(self, func: Callable[..., Any]):
        self.func = func
        self.cache = {}
        functools.update_wrapper(self, func)
    
    def __call__(self, *args, **kwargs) -> Any:
        key = self._make_key(args, kwargs)
        if key in self.cache:
            return self.cache[key]
        result = self.func(*args, **kwargs)
        self.cache[key] = result
        return result
    
    def _make_key(self, args: Tuple, kwargs: dict) -> Tuple:
        kwargs_items = sorted(kwargs.items())
        return (args, tuple(kwargs_items))

if __name__ == "__main__":
    def slow_fib(n: int) -> int:
        if n <= 1:
            return n
        return slow_fib(n-1) + slow_fib(n-2)
    
    memoized_fib = Memoizer(slow_fib)
    print("Test 1: Memoized Fibonacci")
    print(f"Fib(10) = {memoized_fib(10)}")  
    print(f"Fib(10) = {memoized_fib(10)}")  