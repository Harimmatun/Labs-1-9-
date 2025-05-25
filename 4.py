import heapq
from typing import Any, Tuple

class BiPriorityQueue:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []
        self.entry_count = 0
        self.removed = set()

    def enqueue(self, item: Any, priority: float) -> None:
        heapq.heappush(self.min_heap, (priority, self.entry_count, item))
        heapq.heappush(self.max_heap, (-priority, self.entry_count, item))
        self.entry_count += 1

    def dequeue_highest(self) -> Any:
        while self.max_heap:
            neg_priority, entry_id, item = heapq.heappop(self.max_heap)
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                return item
        raise IndexError("Queue is empty")

    def dequeue_lowest(self) -> Any:
        while self.min_heap:
            priority, entry_id, item = heapq.heappop(self.min_heap)
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                return item
        raise IndexError("Queue is empty")

    def peek_highest(self) -> Any:
        while self.max_heap:
            neg_priority, entry_id, item = self.max_heap[0]
            if entry_id not in self.removed:
                return item
            heapq.heappop(self.max_heap)
        raise IndexError("Queue is empty")

    def peek_lowest(self) -> Any:
        while self.min_heap:
            priority, entry_id, item = self.min_heap[0]
            if entry_id not in self.removed:
                return item
            heapq.heappop(self.min_heap)
        raise IndexError("Queue is empty")

    def is_empty(self) -> bool:
        return len(self.min_heap) == 0 or all(entry[1] in self.removed for entry in self.min_heap)

if __name__ == "__main__":
    pq = BiPriorityQueue()
    print("Test 1: Basic Priority Queue Operations")
    pq.enqueue("Task A", 3)
    pq.enqueue("Task B", 1)
    pq.enqueue("Task C", 2)
    print(f"Highest priority: {pq.dequeue_highest()}")
    print(f"Lowest priority: {pq.dequeue_lowest()}")
    print(f"Peek highest: {pq.peek_highest()}")
    print(f"Peek lowest: {pq.peek_lowest()}")