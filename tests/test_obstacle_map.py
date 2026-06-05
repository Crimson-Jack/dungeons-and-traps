from src.obstacle_map import ObstacleMap


class TestObstacleMapWithNoLayers:
    def test_none_argument_produces_empty_items(self):
        obstacle_map = ObstacleMap(None)
        assert obstacle_map.items == []

    def test_empty_list_produces_empty_items(self):
        obstacle_map = ObstacleMap([])
        assert obstacle_map.items == []

    def test_list_of_none_layers_produces_empty_items(self):
        obstacle_map = ObstacleMap([None, None, None])
        assert obstacle_map.items == []


class TestObstacleMapWithSingleLayer:
    def test_items_match_single_layer(self):
        layer = [[0, 1], [1, 0]]
        obstacle_map = ObstacleMap([layer])
        assert obstacle_map.items == [[0, 1], [1, 0]]

    def test_all_zeros_layer_produces_all_zeros(self):
        layer = [[0, 0], [0, 0]]
        obstacle_map = ObstacleMap([layer])
        assert obstacle_map.items == [[0, 0], [0, 0]]

    def test_all_ones_layer_produces_all_ones(self):
        layer = [[1, 1], [1, 1]]
        obstacle_map = ObstacleMap([layer])
        assert obstacle_map.items == [[1, 1], [1, 1]]

    def test_none_layer_mixed_with_valid_layer_is_skipped(self):
        layer = [[1, 0], [0, 1]]
        obstacle_map = ObstacleMap([None, layer])
        assert obstacle_map.items == [[1, 0], [0, 1]]


class TestObstacleMapWithMultipleLayers:
    def test_two_layers_are_merged_with_logical_or(self):
        layer_one = [[1, 0], [0, 0]]
        layer_two = [[0, 0], [0, 1]]
        obstacle_map = ObstacleMap([layer_one, layer_two])
        assert obstacle_map.items == [[1, 0], [0, 1]]

    def test_overlapping_blocked_cells_remain_blocked(self):
        layer_one = [[1, 0], [0, 0]]
        layer_two = [[1, 0], [0, 0]]
        obstacle_map = ObstacleMap([layer_one, layer_two])
        assert obstacle_map.items == [[1, 0], [0, 0]]

    def test_three_layers_merged_correctly(self):
        layer_one = [[1, 0], [0, 0]]
        layer_two = [[0, 1], [0, 0]]
        layer_three = [[0, 0], [1, 0]]
        obstacle_map = ObstacleMap([layer_one, layer_two, layer_three])
        assert obstacle_map.items == [[1, 1], [1, 0]]

    def test_none_layer_between_valid_layers_is_skipped(self):
        layer_one = [[1, 0], [0, 0]]
        layer_two = [[0, 0], [0, 1]]
        obstacle_map = ObstacleMap([layer_one, None, layer_two])
        assert obstacle_map.items == [[1, 0], [0, 1]]
