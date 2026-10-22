from src.bonus_record import BonusRecord


class TestBonusRecord:
    def test_initial_awarded_is_zero(self):
        record = BonusRecord()
        assert record.awarded == 0

    def test_initial_score_is_zero(self):
        record = BonusRecord()
        assert record.score == 0

    def test_add_sums_values_of_other_record(self):
        record = BonusRecord()
        record.awarded, record.score = 1, 500
        other_record = BonusRecord()
        other_record.awarded, other_record.score = 1, 300

        record.add(other_record)

        assert (record.awarded, record.score) == (2, 800)
        assert (other_record.awarded, other_record.score) == (1, 300)
