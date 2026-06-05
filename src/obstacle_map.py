class ObstacleMap:
    """Merged 2D grid of all blocking layers used by enemy pathfinding."""

    def __init__(self, layers: list[list[list[int]] | None] | None = None) -> None:
        """
        Build the obstacle map by combining all provided layers into one.
        Layers may contain None values — these are silently skipped.

        :param layers: list of 2D tile grids to merge; each grid cell is 0 (free) or 1 (blocked)
        """
        self._items = list()
        self._layers = list()

        if layers is not None:
            for layer in layers:
                if layer is not None:
                    self._layers.append(layer)

        if len(self._layers) > 0:
            # Get size: layers, rows and columns
            self.number_of_layers = len(self._layers)
            self.number_of_rows = 0
            self.number_of_columns = 0

            if self.number_of_layers > 0:
                self.number_of_rows = len(self._layers[0])
                if self.number_of_rows > 0:
                    self.number_of_columns = len(self._layers[0][0])

            # Combine layers into one layer
            self.combine_all_layers()

    def combine_all_layers(self) -> None:
        """Merge all layers into self._items using a logical OR across layers for each cell."""
        for row in range(0, self.number_of_rows):
            self._items.append([])

            for column in range(0, self.number_of_columns):
                new_value = False
                for layer in range(0, self.number_of_layers):
                    new_value = new_value or bool(self._layers[layer][row][column])

                self._items[row].append(int(new_value))

    @property
    def items(self) -> list[list[int]]:
        return self._items