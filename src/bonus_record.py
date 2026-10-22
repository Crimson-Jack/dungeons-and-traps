class BonusRecord:
    def __init__(self):
        self.awarded = 0
        self.score = 0

    def add(self, other: 'BonusRecord') -> None:
        """Add the values of another record to this one."""
        self.awarded += other.awarded
        self.score += other.score
