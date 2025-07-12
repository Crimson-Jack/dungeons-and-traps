from queue import Queue


class ZoneHelper:
    def __init__(self):
        self.neighbors_tile_orders = [(1, 0), (0, 1), (-1, 0), (0, -1)]
        self.zones = dict()
        self.queue_maxsize = 3000

    def get_neighbors(self, tiles, tile):
        result = []
        for direction in self.neighbors_tile_orders:
            neighbor = (tile[0] + direction[0], tile[1] + direction[1])
            if neighbor in tiles:
                result.append(neighbor)
        return result

    @staticmethod
    def try_to_find_start_in_different_zone(all_tiles: list[tuple], obstacles: set[tuple], reached: set[tuple]):
        all_visited = reached.union(obstacles)
        not_visited = set(all_tiles).difference(all_visited)

        if len(not_visited) > 0:
            return next(iter(not_visited))
        else:
            return None

    def find_all_zones(self, all_tiles: list[tuple], obstacles: set[tuple]):
        frontier = Queue(maxsize=self.queue_maxsize)
        reached = set()
        self.zones = dict()
        zone_counter = 0

        start_tile = self.try_to_find_start_in_different_zone(all_tiles, obstacles, set())
        if start_tile is None:
            is_end_reached = True
        else:
            self.zones[start_tile] = zone_counter
            frontier.put(start_tile)
            reached.add(start_tile)
            is_end_reached = False

        while not is_end_reached:
            # Flood fill algorithm used to determine zone number for each tile
            if not frontier.empty():
                current_tile = frontier.get()
                for next_neighbor in self.get_neighbors(all_tiles, current_tile):
                    if next_neighbor not in reached and next_neighbor not in obstacles:
                        self.zones[next_neighbor] = zone_counter
                        reached.add(next_neighbor)
                        frontier.put(next_neighbor)
            else:
                # Check another zone if exists
                new_start_tile = self.try_to_find_start_in_different_zone(all_tiles, obstacles, reached)
                if new_start_tile is None:
                    is_end_reached = True
                else:
                    zone_counter += 1
                    start_tile = new_start_tile
                    self.zones[start_tile] = zone_counter
                    frontier.put(start_tile)
                    reached.add(start_tile)
