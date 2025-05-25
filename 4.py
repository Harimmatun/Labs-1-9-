import heapq
from typing import Any, Tuple
from collections import deque

class BiPriorityQueue:
    def __init__(self):
        self.min_heap = []
        self.max_heap = []
        self.entry_count = 0
        self.removed = set()
        self.order_deque = deque()

    def enqueue(self, item: Any, priority: float) -> None:
        entry = (priority, self.entry_count, item)
        heapq.heappush(self.min_heap, entry)
        heapq.heappush(self.max_heap, (-priority, self.entry_count, item))
        self.order_deque.append((self.entry_count, item))
        self.entry_count += 1

    def dequeue(self, mode: str = 'highest') -> Any:
        mode = mode.lower()
        if mode == 'highest':
            return self._dequeue_highest()
        elif mode == 'lowest':
            return self._dequeue_lowest()
        elif mode == 'oldest':
            return self._dequeue_oldest()
        elif mode == 'newest':
            return self._dequeue_newest()
        raise ValueError("Mode must be 'highest', 'lowest', 'oldest', or 'newest'")

    def peek(self, mode: str = 'highest') -> Any:
        mode = mode.lower()
        if mode == 'highest':
            return self._peek_highest()
        elif mode == 'lowest':
            return self._peek_lowest()
        elif mode == 'oldest':
            return self._peek_oldest()
        elif mode == 'newest':
            return self._peek_newest()
        raise ValueError("Mode must be 'highest', 'lowest', 'oldest', or 'newest'")

    def _dequeue_highest(self) -> Any:
        while self.max_heap:
            neg_priority, entry_id, item = heapq.heappop(self.max_heap)
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                self._remove_from_deque(entry_id)
                return item
        raise IndexError("Queue is empty")

    def _dequeue_lowest(self) -> Any:
        while self.min_heap:
            priority, entry_id, item = heapq.heappop(self.min_heap)
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                self._remove_from_deque(entry_id)
                return item
        raise IndexError("Queue is empty")

    def _dequeue_oldest(self) -> Any:
        while self.order_deque:
            entry_id, item = self.order_deque.popleft()
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                return item
        raise IndexError("Queue is empty")

    def _dequeue_newest(self) -> Any:
        while self.order_deque:
            entry_id, item = self.order_deque.pop()
            if entry_id not in self.removed:
                self.removed.add(entry_id)
                return item
        raise IndexError("Queue is empty")

    def _peek_highest(self) -> Any:
        while self.max_heap:
            neg_priority, entry_id, item = self.max_heap[0]
            if entry_id not in self.removed:
                return item
            heapq.heappop(self.max_heap)
        raise IndexError("Queue is empty")

    def _peek_lowest(self) -> Any:
        while self.min_heap:
            priority, entry_id, item = self.min_heap[0]
            if entry_id not in self.removed:
                return item
            heapq.heappop(self.min_heap)
        raise IndexError("Queue is empty")

    def _peek_oldest(self) -> Any:
        while self.order_deque:
            entry_id, item = self.order_deque[0]
            if entry_id not in self.removed:
                return item
            self.order_deque.popleft()
        raise IndexError("Queue is empty")

    def _peek_newest(self) -> Any:
        while self.order_deque:
            entry_id, item = self.order_deque[-1]
            if entry_id not in self.removed:
                return item
            self.order_deque.pop()
        raise IndexError("Queue is empty")

    def _remove_from_deque(self, entry_id: int) -> None:
        while self.order_deque and self.order_deque[0][0] in self.removed:
            self.order_deque.popleft()
        while self.order_deque and self.order_deque[-1][0] in self.removed:
            self.order_deque.pop()

    def is_empty(self) -> bool:
        return len(self.order_deque) == 0 or all(entry[1] in self.removed for entry in self.order_deque)

    def stats(self) -> dict:
        return {
            'size': len(self.order_deque) - len(self.removed),
            'removed_entries': len(self.removed),
            'total_entries_added': self.entry_count
        }

if __name__ == "__main__":
    pq = BiPriorityQueue()
    print("Test 3: Unified Interface and Statistics")
    pq.enqueue("Task A", 3)
    pq.enqueue("Task B", 1)
    pq.enqueue("Task C", 2)
    print(f"Stats: {pq.stats()}")
    print(f"Dequeue highest: {pq.dequeue('highest')}") 
    print(f"Dequeue lowest: {pq.dequeue('lowest')}")   
    print(f"Dequeue oldest: {pq.dequeue('oldest')}")  
    pq.enqueue("Task D", 4)
    pq.enqueue("Task E", 2)
    print(f"Dequeue newest: {pq.dequeue('newest')}")   
    print(f"Peek oldest: {pq.peek('oldest')}")       
    print(f"Stats: {pq.stats()}")