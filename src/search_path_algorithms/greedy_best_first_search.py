import math

from src.search_path_algorithms.unique_priority_queue import UniquePriorityQueue


class GreedyBestFirstSearch:
    def __init__(self):
        self.neighbors_tile_order = [(1, 0), (0, 1), (-1, 0), (0, -1)]

    def get_neighbors(self, tiles, tile):
        result = []
        for direction in self.neighbors_tile_order:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)
        return result

    @staticmethod
    def heuristic(a, b):
        # Euclidian distance
        return math.sqrt((a[0] - b[0]) ** 2 + (a[1] - b[1]) ** 2)

    @staticmethod
    def get_path(current_item, items):
        return_path = list()
        while items[current_item] is not None:
            return_path.append(items[current_item])
            current_item = items[current_item]

        return return_path

    def search(self, all_tiles, start_tile, end_tile):
        frontier = UniquePriorityQueue()
        frontier.add(start_tile, 0)
        came_from = dict()
        came_from[start_tile] = None
        is_end_reached = False
        path = list()

        while not is_end_reached and not frontier.is_empty():
            current_tile, current_tile_priority = frontier.pop()
            if current_tile == end_tile:
                is_end_reached = True
                path = self.get_path(current_tile, came_from)
            else:
                for next_neighbor in self.get_neighbors(all_tiles, current_tile):
                    if next_neighbor not in came_from:
                        came_from[next_neighbor] = current_tile
                        priority = self.heuristic(end_tile, next_neighbor)
                        frontier.add(next_neighbor, priority)

        return is_end_reached, path, frontier, came_from
