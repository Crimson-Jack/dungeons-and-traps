import random
from queue import Queue


class BreadthFirstSearch:
    def __init__(self):
        # All permutations
        self.neighbors_tile_orders = list()
        self.neighbors_tile_orders.append([(1, 0), (0, 1), (-1, 0), (0, -1)])
        self.neighbors_tile_orders.append([(0, 1), (1, 0), (-1, 0), (0, -1)])
        self.neighbors_tile_orders.append([(-1, 0), (1, 0), (0, 1), (0, -1)])
        self.neighbors_tile_orders.append([(1, 0), (-1, 0), (0, 1), (0, -1)])
        self.neighbors_tile_orders.append([(0, 1), (-1, 0), (1, 0), (0, -1)])
        self.neighbors_tile_orders.append([(-1, 0), (0, 1), (1, 0), (0, -1)])
        self.neighbors_tile_orders.append([(-1, 0), (0, 1), (0, -1), (1, 0)])
        self.neighbors_tile_orders.append([(0, 1), (-1, 0), (0, -1), (1, 0)])
        self.neighbors_tile_orders.append([(0, -1), (-1, 0), (0, 1), (1, 0)])
        self.neighbors_tile_orders.append([(-1, 0), (0, -1), (0, 1), (1, 0)])
        self.neighbors_tile_orders.append([(0, 1), (0, -1), (-1, 0), (1, 0)])
        self.neighbors_tile_orders.append([(0, -1), (0, 1), (-1, 0), (1, 0)])
        self.neighbors_tile_orders.append([(0, -1), (1, 0), (-1, 0), (0, 1)])
        self.neighbors_tile_orders.append([(1, 0), (0, -1), (-1, 0), (0, 1)])
        self.neighbors_tile_orders.append([(-1, 0), (0, -1), (1, 0), (0, 1)])
        self.neighbors_tile_orders.append([(0, -1), (-1, 0), (1, 0), (0, 1)])
        self.neighbors_tile_orders.append([(1, 0), (-1, 0), (0, -1), (0, 1)])
        self.neighbors_tile_orders.append([(-1, 0), (1, 0), (0, -1), (0, 1)])
        self.neighbors_tile_orders.append([(0, 1), (1, 0), (0, -1), (-1, 0)])
        self.neighbors_tile_orders.append([(1, 0), (0, 1), (0, -1), (-1, 0)])
        self.neighbors_tile_orders.append([(0, -1), (0, 1), (1, 0), (-1, 0)])
        self.neighbors_tile_orders.append([(0, 1), (0, -1), (1, 0), (-1, 0)])
        self.neighbors_tile_orders.append([(1, 0), (0, -1), (0, 1), (-1, 0)])
        self.neighbors_tile_orders.append([(0, -1), (1, 0), (0, 1), (-1, 0)])

        # Neighbours tile order
        self._neighbors_tile_order_selection = None
        self._neighbors_tile_order = None
        # Randomly choose one of the permutation options
        self._set_random_neighbors_tile_order()

        self._path = list()
        self._is_end_reached = False

    def _set_random_neighbors_tile_order(self):
        self._neighbors_tile_order_selection = random.randint(0, len(self.neighbors_tile_orders) - 1)
        self._neighbors_tile_order = self.neighbors_tile_orders[self._neighbors_tile_order_selection]

    def _get_neighbors(self, tiles, tile):
        result = []
        for direction in self._neighbors_tile_order:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)

        # Randomly choose one of the permutation options for next iteration
        self._set_random_neighbors_tile_order()

        return result

    def _generate_path(self, current_item, items):
        while items[current_item] is not None:
            self._path.append(items[current_item])
            current_item = items[current_item]

    def search(self, all_tiles: list[tuple], start_tile: tuple, end_tile: tuple, max_distance:int = 10) -> list[tuple]:
        frontier = Queue()
        frontier.put(start_tile)
        came_from = dict()
        came_from[start_tile] = None
        self._is_end_reached = False
        self._path.clear()

        while not self._is_end_reached and not frontier.empty():
            current_tile = frontier.get()
            if current_tile == end_tile:
                self._is_end_reached = True
                self._generate_path(current_tile, came_from)
            else:
                for next_neighbor in self._get_neighbors(all_tiles, current_tile):
                    if next_neighbor not in came_from:
                        # square shape max distance
                        distance = abs(start_tile[0] - next_neighbor[0]), abs(start_tile[1] - next_neighbor[1])
                        if distance[0] <= max_distance and distance[1] <= max_distance:
                            came_from[next_neighbor] = current_tile
                            frontier.put(next_neighbor)

        return self._path

    @property
    def path(self):
        return self._path

    @property
    def is_end_reached(self):
        return self._is_end_reached
