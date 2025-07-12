import math
from queue import PriorityQueue


class GBFSHelper:
    def __init__(self):
        self.neighbors_tile_order = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.max_distance = 10

    def get_neighbors(self, tiles, tile):
        result = []
        for direction in self.neighbors_tile_order:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)
        return result

    @staticmethod
    def heuristic(a, b):
        # Manhattan distance on a square grid
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    @staticmethod
    def get_path(current_item, items):
        return_path = list()
        while items[current_item] is not None:
            return_path.append(items[current_item])
            current_item = items[current_item]

        return return_path

    def search(self, all_tiles, obstacles, start_tile, end_tile):
        frontier = PriorityQueue(maxsize=1000)
        frontier.put((0, start_tile))
        came_from = dict()
        came_from[start_tile] = None
        is_end_reached = False
        path = set()

        counter = 0

        while not is_end_reached and not frontier.empty():
            counter += 1
            current_tile = frontier.get()[1]
            distance = ((start_tile[0] - current_tile[0]) ** 2 + (start_tile[1] - current_tile[1]) ** 2) ** 0.5

            if current_tile == end_tile:
                is_end_reached = True
                path = self.get_path(current_tile, came_from)
            elif math.floor(distance) + 1 > self.max_distance:
                continue
            else:
                for next_neighbor in self.get_neighbors(all_tiles, current_tile):
                    if next_neighbor not in came_from and next_neighbor not in obstacles:
                        came_from[next_neighbor] = current_tile
                        priority = GBFSHelper.heuristic(end_tile, next_neighbor)
                        frontier.put((priority, next_neighbor))

        print(counter)
        return is_end_reached, path, frontier, came_from
