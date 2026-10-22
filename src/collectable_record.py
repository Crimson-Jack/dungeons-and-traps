class CollectableRecord:
    def __init__(self):
        self.count = 0
        self.collected = 0
        self.score = 0

    def add(self, other: 'CollectableRecord') -> None:
        """Add the values of another record to this one."""
        self.count += other.count
        self.collected += other.collected
        self.score += other.score
