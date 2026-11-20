import pytest

from src.enums.search_path_algorithm import SearchPathAlgorithm
from src.search_path_algorithms.breadth_first_search import BreadthFirstSearch
from src.search_path_algorithms.greedy_best_first_search import GreedyBestFirstSearch
from src.search_path_algorithms.search_path_algorithm_factory import SearchPathAlgorithmFactory


class TestSearchPathAlgorithmFactory:
    @pytest.mark.parametrize(('search_path_algorithm', 'expected_class'), [
        (SearchPathAlgorithm.BREADTH_FIRST_SEARCH, BreadthFirstSearch),
        (SearchPathAlgorithm.GREEDY_BEST_FIRST_SEARCH, GreedyBestFirstSearch),
    ])
    def test_creates_algorithm_of_given_name(self, search_path_algorithm, expected_class):
        algorithm = SearchPathAlgorithmFactory.create(search_path_algorithm)

        assert type(algorithm) is expected_class

    def test_creates_new_instance_on_every_call(self):
        first_algorithm = SearchPathAlgorithmFactory.create(SearchPathAlgorithm.BREADTH_FIRST_SEARCH)
        second_algorithm = SearchPathAlgorithmFactory.create(SearchPathAlgorithm.BREADTH_FIRST_SEARCH)

        assert first_algorithm is not second_algorithm

    def test_unknown_algorithm_raises_value_error(self):
        with pytest.raises(ValueError, match='Unknown algorithm name'):
            SearchPathAlgorithmFactory.create('unknown-algorithm')
