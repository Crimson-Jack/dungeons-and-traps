from src.bonus_record import BonusRecord


class TestBonusRecord:
    def test_initial_awarded_is_zero(self):
        record = BonusRecord()
        assert record.awarded == 0

    def test_initial_score_is_zero(self):
        record = BonusRecord()
        assert record.score == 0
