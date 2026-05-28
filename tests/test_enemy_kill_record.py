from src.enemy_kill_record import EnemyKillRecord


class TestEnemyKillRecord:
    def test_initial_count_is_zero(self):
        record = EnemyKillRecord()
        assert record.count == 0

    def test_initial_killed_is_zero(self):
        record = EnemyKillRecord()
        assert record.killed == 0

    def test_initial_score_is_zero(self):
        record = EnemyKillRecord()
        assert record.score == 0
