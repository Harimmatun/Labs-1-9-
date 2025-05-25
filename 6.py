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

async def process_stream_cancellable(stream: AsyncIterator[Any], processor: Callable[[Any], Any], cancel_event: asyncio.Event) -> None:
    total = 0
    count = 0
    try:
        async for item in stream:
            if cancel_event.is_set():
                raise asyncio.CancelledError("Stream processing cancelled")
            processed_item = await processor(item)
            total += processed_item
            count += 1
            avg = total / count if count > 0 else 0
            print(f"Processed item: {processed_item}, Running total: {total}, Average: {avg:.2f}, Count: {count}")
    except asyncio.CancelledError as e:
        print(f"Cancelled: {e}")
        raise

async def example_processor(item: Any) -> Any:
    await asyncio.sleep(0.05)
    return item * 2

async def cancellable_example():
    cancel_event = asyncio.Event()
    asyncio.get_event_loop().call_later(0.3, cancel_event.set)
    try:
        await process_stream_cancellable(data_stream(10), example_processor, cancel_event)
    except asyncio.CancelledError:
        print("Cancellable stream processing was stopped gracefully")
    print("Cancellable example completed")

if __name__ == "__main__":
    print("Test 3: Stream Processing with Cancellation")
    asyncio.run(process_stream(data_stream(5), example_processor))
    print("\nTest 4: Cancellable Stream Processing")
    asyncio.run(cancellable_example())