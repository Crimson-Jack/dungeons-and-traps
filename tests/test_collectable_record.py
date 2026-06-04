from src.collectable_record import CollectableRecord


class TestCollectableRecord:
    def test_initial_count_is_zero(self):
        record = CollectableRecord()
        assert record.count == 0

    def test_initial_collected_is_zero(self):
        record = CollectableRecord()
        assert record.collected == 0

    def test_initial_score_is_zero(self):
        record = CollectableRecord()
        assert record.score == 0
