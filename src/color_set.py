# Percentage range (lowest_percent, highest_percent) with its rgb color
PercentRangeColor = tuple[tuple[int, int], tuple[int, int, int]]


class ColorSet:
    """
    Colors assigned to percentage ranges, used to color a bar by how full it is.
    Each item is ((lowest_percent, highest_percent), (red, green, blue)); both ends of a range are included.
    """

    COLORS: tuple[PercentRangeColor, ...] = (
        ((0, 100), (0, 0, 0)),
    )

    def __init__(self, colors: tuple[PercentRangeColor, ...] | None = None) -> None:
        """
        Store the colors of the percentage ranges.

        :param colors: tuple of percentage ranges with their colors, ordered from the lowest range; COLORS when None
        :raises ValueError: when colors is empty
        """
        if colors is None:
            colors = self.COLORS

        if len(colors) == 0:
            raise ValueError('ColorSet needs at least one percentage range with a color')

        self._colors = colors

    def get_color(self, percent: float) -> tuple[int, int, int]:
        """
        Return the color of the first range that contains the percentage.
        A percentage outside the ranges gets the color of the closest range below it,
        or the color of the first range when it is below all ranges.

        :param percent: percentage to find the color for
        :return: rgb color of the range
        """
        # Color of the closest range below the percentage; the first range when there is none
        color_below = self._colors[0][1]

        for (lowest_percent, highest_percent), color in self._colors:
            if lowest_percent <= percent <= highest_percent:
                return color

            if highest_percent < percent:
                color_below = color

        return color_below
