from src.bonus_record import BonusRecord
from src.collectable_record import CollectableRecord
from src.enemy_kill_record import EnemyKillRecord
from src.enums.enemy_type import EnemyType


class LevelStats:
    def __init__(self):
        self._enemy_stats: dict[EnemyType, EnemyKillRecord] = {
            enemy_type: EnemyKillRecord() for enemy_type in EnemyType
        }
        self._diamond_record = CollectableRecord()
        self._key_record = CollectableRecord()
        self._bonus_record = BonusRecord()

    # Enemy

    def record_enemy_spawn(self, enemy_type: EnemyType) -> None:
        self._enemy_stats[enemy_type].record_spawn()

    def record_enemy_kill(self, enemy_type: EnemyType, score: int) -> None:
        self._enemy_stats[enemy_type].record_kill(score)

    def get_enemy_record(self, enemy_type: EnemyType) -> EnemyKillRecord:
        return self._enemy_stats[enemy_type]

    def get_enemy_spider_records(self) -> dict[EnemyType, EnemyKillRecord]:
        return {enemy_type: record for enemy_type, record in self._enemy_stats.items() if enemy_type.is_spider()}

    def get_enemy_monster_records(self) -> dict[EnemyType, EnemyKillRecord]:
        return {enemy_type: record for enemy_type, record in self._enemy_stats.items() if enemy_type.is_monster()}

    def get_enemy_bat_records(self) -> dict[EnemyType, EnemyKillRecord]:
        return {enemy_type: record for enemy_type, record in self._enemy_stats.items() if enemy_type.is_bat()}

    def total_enemy_count(self) -> int:
        return sum(record.count for record in self._enemy_stats.values())

    def total_enemy_kills(self) -> int:
        return sum(record.killed for record in self._enemy_stats.values())

    def total_enemy_score(self) -> int:
        return sum(record.score for record in self._enemy_stats.values())

    def get_enemy_spider_total_count(self) -> int:
        return sum(record.count for record in self.get_enemy_spider_records().values())

    def get_enemy_spider_total_kills(self) -> int:
        return sum(record.killed for record in self.get_enemy_spider_records().values())

    def get_enemy_spider_total_score(self) -> int:
        return sum(record.score for record in self.get_enemy_spider_records().values())

    def get_enemy_monster_total_count(self) -> int:
        return sum(record.count for record in self.get_enemy_monster_records().values())

    def get_enemy_monster_total_kills(self) -> int:
        return sum(record.killed for record in self.get_enemy_monster_records().values())

    def get_enemy_monster_total_score(self) -> int:
        return sum(record.score for record in self.get_enemy_monster_records().values())

    def get_enemy_bat_total_count(self) -> int:
        return sum(record.count for record in self.get_enemy_bat_records().values())

    def get_enemy_bat_total_kills(self) -> int:
        return sum(record.killed for record in self.get_enemy_bat_records().values())

    def get_enemy_bat_total_score(self) -> int:
        return sum(record.score for record in self.get_enemy_bat_records().values())

    def all_enemies_defeated(self) -> bool:
        return self.total_enemy_count() > 0 and self.total_enemy_kills() == self.total_enemy_count()

    # Diamonds

    def record_diamond_placed(self) -> None:
        self._diamond_record.record_placed()

    def record_diamond_collected(self, score: int) -> None:
        self._diamond_record.record_collected(score)

    def get_diamond_record(self) -> CollectableRecord:
        return self._diamond_record

    # Keys

    def record_key_placed(self) -> None:
        self._key_record.record_placed()

    def record_key_collected(self, score: int) -> None:
        self._key_record.record_collected(score)

    def get_key_record(self) -> CollectableRecord:
        return self._key_record

    # Bonus

    def record_bonus_awarded(self, score: int) -> None:
        self._bonus_record.record_award(score)

    def get_bonus_record(self) -> BonusRecord:
        return self._bonus_record

    # Reset

    def reset(self) -> None:
        for record in self._enemy_stats.values():
            record.reset()
        self._diamond_record.reset()
        self._key_record.reset()
        self._bonus_record.reset()
