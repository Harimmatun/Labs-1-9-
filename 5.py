import asyncio
from typing import Any, Callable, List

async def async_map_callback(arr: List[Any], callback: Callable[[Any], Any], done: Callable[[List[Any]], None]) -> None:
    result = []
    for item in arr:
        result.append(await callback(item))
    done(result)

async def example_callback(item: Any) -> Any:
    await asyncio.sleep(1)
    return item * 2

def done_callback(result: List[Any]) -> None:
    print(f"Callback result: {result}")

if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    print("Test 1: Callback-based async map")
    loop.run_until_complete(async_map_callback([1, 2, 3], example_callback, done_callback))