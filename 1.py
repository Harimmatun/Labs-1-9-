import time
import random
from typing import Iterator, TypeVar

T = TypeVar('T')

def fibonacci_generator() -> Iterator[int]:
    a, b = 0, 1
    while True:
        yield a
        a, b = b, a + b

def consume_with_timeout(iterator: Iterator[T], timeout_seconds: float) -> None:
    start_time = time.time()
    count = 0
    total = 0
    try:
        while time.time() - start_time < timeout_seconds:
            value = next(iterator)
            count += 1
            if isinstance(value, (int, float)):
                total += value
                avg = total / count if count > 0 else 0
                print(f"Value: {value}, Current total: {total}, Average: {avg:.2f}")
            else:
                print(f"Value: {value}")
            time.sleep(0.01)
    except StopIteration:
        print("Iterator exhausted before timeout")
    print(f"\nProcessing complete. Items processed: {count}")
    if count > 0 and isinstance(value, (int, float)):
        print(f"Final total: {total}, Final average: {avg:.2f}")

if __name__ == "__main__":
    print("Test 1: Running Fibonacci generator for 2 seconds")
    fib_iter = fibonacci_generator()
    consume_with_timeout(fib_iter, 2.0)
    
    print("\nTest 2: Running Fibonacci generator for 0.5 seconds")
    fib_iter = fibonacci_generator()
    consume_with_timeout(fib_iter, 0.5)
