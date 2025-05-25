import asyncio
from typing import AsyncIterator, Any, Callable

async def data_stream(size: int) -> AsyncIterator[Any]:
    for i in range(size):
        await asyncio.sleep(0.1)
        yield i

async def process_stream(stream: AsyncIterator[Any], processor: Callable[[Any], Any]) -> None:
    total = 0
    count = 0
    async for item in stream:
        processed_item = await processor(item)
        total += processed_item
        count += 1
        avg = total / count if count > 0 else 0
        print(f"Processed item: {processed_item}, Running total: {total}, Average: {avg:.2f}, Count: {count}")

async def example_processor(item: Any) -> Any:
    await asyncio.sleep(0.05)
    return item * 2

if __name__ == "__main__":
    print("Test 2: Stream Processing with Custom Processor")
    asyncio.run(process_stream(data_stream(5), example_processor))