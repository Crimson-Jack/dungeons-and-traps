from src.enemy_kill_record import EnemyKillRecord
from src.enums.enemy_type import EnemyType


class LevelKillStats:
    def __init__(self):
        self._stats: dict[EnemyType, EnemyKillRecord] = {}
        for enemy_type in EnemyType:
            self._stats[enemy_type] = EnemyKillRecord()

    def record_spawn(self, enemy_type: EnemyType) -> None:
        self._stats[enemy_type].count += 1

    def record_kill(self, enemy_type: EnemyType, score: int) -> None:
        self._stats[enemy_type].killed += 1
        self._stats[enemy_type].score += score

    def reset(self) -> None:
        for record in self._stats.values():
            record.count = 0
            record.killed = 0
            record.score = 0

    def get_record(self, enemy_type: EnemyType) -> EnemyKillRecord:
        return self._stats[enemy_type]

    def get_spider_records(self) -> dict[EnemyType, EnemyKillRecord]:
        result = {}
        for enemy_type, record in self._stats.items():
            if enemy_type.is_spider():
                result[enemy_type] = record
        return result

    def get_monster_records(self) -> dict[EnemyType, EnemyKillRecord]:
        result = {}
        for enemy_type, record in self._stats.items():
            if enemy_type.is_monster():
                result[enemy_type] = record
        return result

    def get_bat_records(self) -> dict[EnemyType, EnemyKillRecord]:
        result = {}
        for enemy_type, record in self._stats.items():
            if enemy_type.is_bat():
                result[enemy_type] = record
        return result

    def get_spider_total_count(self) -> int:
        total = 0
        for record in self.get_spider_records().values():
            total += record.count
        return total

    def get_spider_total_kills(self) -> int:
        total = 0
        for record in self.get_spider_records().values():
            total += record.killed
        return total

    def get_spider_total_score(self) -> int:
        total = 0
        for record in self.get_spider_records().values():
            total += record.score
        return total

    def get_monster_total_count(self) -> int:
        total = 0
        for record in self.get_monster_records().values():
            total += record.count
        return total

    def get_monster_total_kills(self) -> int:
        total = 0
        for record in self.get_monster_records().values():
            total += record.killed
        return total

    def get_monster_total_score(self) -> int:
        total = 0
        for record in self.get_monster_records().values():
            total += record.score
        return total

    def get_bat_total_count(self) -> int:
        total = 0
        for record in self.get_bat_records().values():
            total += record.count
        return total

    def get_bat_total_kills(self) -> int:
        total = 0
        for record in self.get_bat_records().values():
            total += record.killed
        return total

    def get_bat_total_score(self) -> int:
        total = 0
        for record in self.get_bat_records().values():
            total += record.score
        return total

    def total_count(self) -> int:
        total = 0
        for record in self._stats.values():
            total += record.count
        return total

    def total_kills(self) -> int:
        total = 0
        for record in self._stats.values():
            total += record.killed
        return total

    def total_score(self) -> int:
        total = 0
        for record in self._stats.values():
            total += record.score
        return total

    def all_enemies_defeated(self) -> bool:
        return self.total_count() > 0 and self.total_kills() == self.total_count()
