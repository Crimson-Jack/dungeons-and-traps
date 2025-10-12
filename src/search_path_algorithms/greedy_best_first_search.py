import math

from src.search_path_algorithms.unique_priority_queue import UniquePriorityQueue


class GreedyBestFirstSearch:
    def __init__(self):
        self._neighbors_tile_order = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self._is_end_reached = False
        self._path = list()

    def _get_neighbors(self, tiles, tile):
        result = []
        for direction in self._neighbors_tile_order:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)
        return result

    @staticmethod
    def heuristic(a, b):
        # Euclidian distance
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    def _generate_path(self, current_item, items):
        while items[current_item] is not None:
            self._path.append(items[current_item])
            current_item = items[current_item]

    def search(self, all_tiles: list[tuple], start_tile: tuple, end_tile: tuple, max_distance:int = 10) -> list[tuple]:
        frontier = UniquePriorityQueue()
        frontier.add(start_tile, 0)
        came_from = dict()
        came_from[start_tile] = None
        self._is_end_reached = False
        self._path.clear()

        while not self._is_end_reached and not frontier.is_empty():
            current_tile, current_tile_priority = frontier.pop()
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
                            priority = self.heuristic(end_tile, next_neighbor)
                            frontier.add(next_neighbor, priority)

        return self._path

    @property
    def path(self):
        return self._path

    @property
    def is_end_reached(self):
        return self._is_end_reached
