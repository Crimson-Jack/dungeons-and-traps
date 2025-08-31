import heapq

class UniquePriorityQueue:
    def __init__(self):
        self.heap = []
        self.entry_finder = {}

    def add(self, item, priority):
        if item not in self.entry_finder:
            heapq.heappush(self.heap, (priority, item))
            self.entry_finder[item] = priority
        elif priority < self.entry_finder[item]:
            heapq.heappush(self.heap, (priority, item))
            self.entry_finder[item] = priority

    def pop(self):
        while self.heap:
            priority, item = heapq.heappop(self.heap)
            if self.entry_finder.get(item) == priority:
                del self.entry_finder[item]
                return item, priority
        raise KeyError("Pop from an empty priority queue")

    def is_empty(self):
        return len(self.entry_finder) == 0

    def get_items(self):
        return self.entry_finder.keys()