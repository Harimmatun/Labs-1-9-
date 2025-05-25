import asyncio
from typing import Any, Callable, List

async def async_map_callback(arr: List[Any], callback: Callable[[Any], Any], done: Callable[[List[Any]], None]) -> None:
    result = []
    for item in arr:
        result.append(await callback(item))
    done(result)

async def async_map_promise(arr: List[Any], callback: Callable[[Any], Any]) -> List[Any]:
    return await asyncio.gather(*(callback(item) for item in arr))

async def async_map_promise_cancellable(arr: List[Any], callback: Callable[[Any], Any], cancel_event: asyncio.Event) -> List[Any]:
    tasks = [asyncio.create_task(callback(item)) for item in arr]
    try:
        await asyncio.wait_for(asyncio.gather(*tasks), timeout=None if cancel_event.is_set() else 0.5)
        return [await task for task in tasks]
    except asyncio.CancelledError:
        for task in tasks:
            task.cancel()
        raise
    except asyncio.TimeoutError:
        for task in tasks:
            task.cancel()
        raise asyncio.CancelledError("Operation cancelled due to timeout")

async def example_callback(item: Any) -> Any:
    await asyncio.sleep(1)
    return item * 2

def done_callback(result: List[Any]) -> None:
    print(f"Callback result: {result}")

async def async_await_example():
    print("Async/Await Example")
    result = await async_map_promise([1, 2, 3], example_callback)
    print(f"Async/Await result: {result}")

async def cancellable_example():
    print("Cancellable Example")
    cancel_event = asyncio.Event()
    try:
        result = await async_map_promise_cancellable([1, 2, 3], example_callback, cancel_event)
        print(f"Cancellable result: {result}")
    except asyncio.CancelledError as e:
        print(f"Cancelled: {e}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("Test 1: Callback-based async map")
    loop.run_until_complete(async_map_callback([1, 2, 3], example_callback, done_callback))
    print("\nTest 2: Promise-based async map")
    result = loop.run_until_complete(async_map_promise([1, 2, 3], example_callback))
    print(f"Promise result: {result}")
    print("\nTest 3: Async/Await and Cancellable async map")
    loop.run_until_complete(async_await_example())
    loop.run_until_complete(cancellable_example())