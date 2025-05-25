import asyncio
from typing import AsyncIterator, Any

async def data_stream(size: int) -> AsyncIterator[Any]:
    for i in range(size):
        await asyncio.sleep(0.1)
        yield i

async def process_stream(stream: AsyncIterator[Any]) -> None:
    total = 0
    count = 0
    async for item in stream:
        total += item
        count += 1
        print(f"Processed item: {item}, Running total: {total}, Count: {count}")

if __name__ == "__main__":
    print("Test 1: Basic Stream Processing")
    asyncio.run(process_stream(data_stream(5)))