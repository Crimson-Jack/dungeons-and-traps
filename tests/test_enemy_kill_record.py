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

    def test_add_sums_values_of_other_record(self):
        record = EnemyKillRecord()
        record.count, record.killed, record.score = 4, 3, 60
        other_record = EnemyKillRecord()
        other_record.count, other_record.killed, other_record.score = 2, 1, 20

        record.add(other_record)

        assert (record.count, record.killed, record.score) == (6, 4, 80)
        assert (other_record.count, other_record.killed, other_record.score) == (2, 1, 20)
