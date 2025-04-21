class ObstacleMap:
    def __init__(self, layers=None):
        self.items = list()
        self.layers = list()

        if layers is not None:
            for layer in layers:
                if layer is not None:
                    self.layers.append(layer)

        if len(self.layers) > 0:
            # Get size: layers, rows and columns
            self.number_of_layers = len(self.layers)
            self.number_of_rows = 0
            self.number_of_columns = 0

            if self.number_of_layers > 0:
                self.number_of_rows = len(self.layers[0])
                if self.number_of_rows > 0:
                    self.number_of_columns = len(self.layers[0][0])

            # Combine layers into one layer
            self.combine_all_layers()

    def combine_all_layers(self):
        for row in range(0, self.number_of_rows):
            self.items.append([])

            for column in range(0, self.number_of_columns):
                new_value = False
                for layer in range(0, self.number_of_layers):
                    new_value = new_value or bool(self.layers[layer][row][column])

                self.items[row].append(int(new_value))
