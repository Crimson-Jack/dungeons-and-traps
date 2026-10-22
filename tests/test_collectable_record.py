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

    def test_add_sums_values_of_other_record(self):
        record = CollectableRecord()
        record.count, record.collected, record.score = 5, 4, 40
        other_record = CollectableRecord()
        other_record.count, other_record.collected, other_record.score = 3, 2, 20

        record.add(other_record)

        assert (record.count, record.collected, record.score) == (8, 6, 60)
        assert (other_record.count, other_record.collected, other_record.score) == (3, 2, 20)
