from moving_obstacle import MovingObstacle
import game_helper


class Stone(MovingObstacle):
    def __init__(self, image, position, groups, game_state, obstacle_map_items, collision_sprites):
        super().__init__(image, position, groups, game_state, obstacle_map_items, collision_sprites)
        # Note: inflate rectangle in y should have the same value as obstacles (wall)
        self.hit_box = self.rect.inflate(game_helper.multiply_by_tile_size_ratio(-10),
                                         game_helper.multiply_by_tile_size_ratio(-40))

    # Note: enemy_sprites, obstacle_sprites, moving_obstacle_sprites should be moved to the constructor
    def move_obstacle_if_allowed(self, movement_direction):
        obstacle_has_been_moved = super().move_obstacle_if_allowed(movement_direction)

        if obstacle_has_been_moved:
            # Adjust hit box
            self.hit_box.center = self.rect.center

        return obstacle_has_been_moved
