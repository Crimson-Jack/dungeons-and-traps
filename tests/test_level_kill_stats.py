from src.enums.enemy_type import EnemyType
from src.level_kill_stats import LevelKillStats


class TestLevelKillStatsRecordSpawn:
    def test_increases_count_for_enemy_type(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.get_record(EnemyType.SPIDER_SMALL).count == 1

    def test_accumulates_count_for_same_enemy_type(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.get_record(EnemyType.SPIDER_SMALL).count == 2

    def test_does_not_affect_killed(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.get_record(EnemyType.SPIDER_SMALL).killed == 0

    def test_does_not_affect_score(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.get_record(EnemyType.SPIDER_SMALL).score == 0

    def test_tracks_different_enemy_types_independently(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.MONSTER_BLUE)
        assert stats.get_record(EnemyType.SPIDER_SMALL).count == 1
        assert stats.get_record(EnemyType.MONSTER_BLUE).count == 1


class TestLevelKillStatsRecordKill:
    def test_increases_killed_for_enemy_type(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.get_record(EnemyType.SPIDER_SMALL).killed == 1

    def test_increases_score_for_enemy_type(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.get_record(EnemyType.SPIDER_SMALL).score == 50

    def test_accumulates_killed_for_same_enemy_type(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.get_record(EnemyType.SPIDER_SMALL).killed == 2

    def test_accumulates_score_for_same_enemy_type(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.get_record(EnemyType.SPIDER_SMALL).score == 100

    def test_does_not_affect_count(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.get_record(EnemyType.SPIDER_SMALL).count == 0

    def test_tracks_different_enemy_types_independently(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.MONSTER_BLUE, 300)
        assert stats.get_record(EnemyType.SPIDER_SMALL).killed == 1
        assert stats.get_record(EnemyType.MONSTER_BLUE).killed == 1


class TestLevelKillStatsReset:
    def test_resets_count_to_zero(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.reset()
        assert stats.get_record(EnemyType.SPIDER_SMALL).count == 0

    def test_resets_killed_to_zero(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.reset()
        assert stats.get_record(EnemyType.SPIDER_SMALL).killed == 0

    def test_resets_score_to_zero(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.reset()
        assert stats.get_record(EnemyType.SPIDER_SMALL).score == 0


class TestLevelKillStatsTotals:
    def test_total_count_sums_spawned_for_all_enemy_types(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.MONSTER_BLUE)
        assert stats.total_count() == 3

    def test_total_count_is_zero_initially(self):
        stats = LevelKillStats()
        assert stats.total_count() == 0

    def test_total_kills_sums_killed_for_all_enemy_types(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.MONSTER_BLUE, 300)
        assert stats.total_kills() == 3

    def test_total_score_sums_all_enemy_types(self):
        stats = LevelKillStats()
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.MONSTER_BLUE, 300)
        assert stats.total_score() == 400

    def test_total_kills_is_zero_initially(self):
        stats = LevelKillStats()
        assert stats.total_kills() == 0

    def test_total_score_is_zero_initially(self):
        stats = LevelKillStats()
        assert stats.total_score() == 0

    def test_total_kills_does_not_count_spawned_only_enemies(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.total_kills() == 0


class TestLevelKillStatsAllEnemiesDefeated:
    def test_returns_true_when_all_spawned_enemies_killed(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.MONSTER_BLUE)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        stats.record_kill(EnemyType.MONSTER_BLUE, 300)
        assert stats.all_enemies_defeated() is True

    def test_returns_false_when_not_all_enemies_killed(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        stats.record_spawn(EnemyType.MONSTER_BLUE)
        stats.record_kill(EnemyType.SPIDER_SMALL, 50)
        assert stats.all_enemies_defeated() is False

    def test_returns_false_when_no_enemies_spawned(self):
        stats = LevelKillStats()
        assert stats.all_enemies_defeated() is False

    def test_returns_false_when_no_enemies_killed(self):
        stats = LevelKillStats()
        stats.record_spawn(EnemyType.SPIDER_SMALL)
        assert stats.all_enemies_defeated() is False


class TestLevelKillStatsGroupRecords:
    def test_get_spider_records_returns_only_spider_types(self):
        stats = LevelKillStats()
        spider_records = stats.get_spider_records()
        for enemy_type in spider_records:
            assert enemy_type.is_spider()

    def test_get_monster_records_returns_only_monster_types(self):
        stats = LevelKillStats()
        monster_records = stats.get_monster_records()
        for enemy_type in monster_records:
            assert enemy_type.is_monster()

    def test_get_bat_records_returns_only_bat_types(self):
        stats = LevelKillStats()
        bat_records = stats.get_bat_records()
        for enemy_type in bat_records:
            assert enemy_type.is_bat()

    def test_get_spider_records_contains_all_spider_types(self):
        stats = LevelKillStats()
        assert len(stats.get_spider_records()) == 3

    def test_get_monster_records_contains_all_monster_types(self):
        stats = LevelKillStats()
        assert len(stats.get_monster_records()) == 6

    def test_get_bat_records_contains_all_bat_types(self):
        stats = LevelKillStats()
        assert len(stats.get_bat_records()) == 1
