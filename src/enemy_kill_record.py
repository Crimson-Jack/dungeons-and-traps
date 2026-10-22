class EnemyKillRecord:
    def __init__(self):
        self.count = 0
        self.killed = 0
        self.score = 0

    def add(self, other: 'EnemyKillRecord') -> None:
        """Add the values of another record to this one."""
        self.count += other.count
        self.killed += other.killed
        self.score += other.score
