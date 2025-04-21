from queue import Queue
import random


class BreadthFirstSearchHelper:
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
        self.neighbors_tile_order_selection = None
        self.neighbors_tile_order = None

        # Randomly choose one of the permutation options
        self.set_random_neighbors_tile_order()

    def set_random_neighbors_tile_order(self):
        self.neighbors_tile_order_selection = random.randint(0, len(self.neighbors_tile_orders) - 1)
        self.neighbors_tile_order = self.neighbors_tile_orders[self.neighbors_tile_order_selection]

    def get_neighbors(self, tiles, tile):
        result = []
        for direction in self.neighbors_tile_order:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)
        # Randomly choose one of the permutation options
        self.set_random_neighbors_tile_order()

        return result

    @staticmethod
    def get_path(current_item, items):
        return_path = list()
        while items[current_item] is not None:
            return_path.append(items[current_item])
            current_item = items[current_item]

        return return_path

    def search(self, all_tiles, obstacles, start_tile, end_tile):
        frontier = Queue(maxsize=1000)
        frontier.put(start_tile)
        came_from = dict()
        came_from[start_tile] = None
        is_end_reached = False
        path = list()

        while not is_end_reached and not frontier.empty():
            current_tile = frontier.get()
            if current_tile == end_tile:
                is_end_reached = True
                path = self.get_path(current_tile, came_from)
            else:
                for next_neighbor in self.get_neighbors(all_tiles, current_tile):
                    if next_neighbor not in came_from and next_neighbor not in obstacles:
                        came_from[next_neighbor] = current_tile
                        frontier.put(next_neighbor)

        return is_end_reached, path, frontier, came_from
