import pytest

from src.color_set import ColorSet

RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


def create_color_set():
    return ColorSet((
        ((0, 25), RED),
        ((25, 50), GREEN),
        ((50, 100), BLUE)
    ))


class TestColorSetGetColor:
    def test_percent_inside_range_returns_its_color(self):
        assert create_color_set().get_color(40) == GREEN

    def test_percent_on_shared_border_returns_color_of_first_range(self):
        assert create_color_set().get_color(25) == RED

    def test_percent_below_all_ranges_returns_color_of_first_range(self):
        assert create_color_set().get_color(-10) == RED

    def test_percent_above_all_ranges_returns_color_of_last_range(self):
        assert create_color_set().get_color(120) == BLUE

    def test_percent_in_gap_between_ranges_returns_color_of_range_below(self):
        color_set = ColorSet((
            ((0, 20), RED),
            ((40, 100), BLUE)
        ))
        assert color_set.get_color(30) == RED

    def test_default_colors_are_used_when_none_are_given(self):
        assert ColorSet().get_color(50) == ColorSet.COLORS[0][1]


class TestColorSetConstruction:
    def test_empty_colors_raise_value_error(self):
        with pytest.raises(ValueError):
            ColorSet(())
