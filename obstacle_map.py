class ObstacleMap:
    def __init__(self, layers=[]):
        self.layers = layers
        self.items = []

        # Get size: layers, rows and columns
        self.number_of_layers = len(layers)
        self.number_of_rows = 0
        self.number_of_columns = 0

        if self.number_of_layers > 0:
            self.number_of_rows = len(layers[0])
            if self.number_of_rows > 0:
                self.number_of_columns = len(layers[0][0])

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
