from enum import StrEnum


class SoundEffect(StrEnum):
    COLLECT_DIAMOND = 'collect_diamond'
    COLLECT_KEY = 'collect_key'
    COLLECT_BOW = 'collect_bow'
    COLLECT_SWORD = 'collect_sword'
    COLLECT_EXPLOSION = 'collect_explosion'
    COLLECT_ENERGY = 'collect_energy'
    COLLECT_LIFE = 'collect_life'
    COLLECT_CHECKPOINT = 'collect_checkpoint'
    COLLECT_LIGHTNING_SPELL = 'collect_lighting_spell'

    STRIKE_WITH_SWORD = 'strike_with_sword'
    SHOOT_ARROW = 'shoot_arrow'
    EXPLODE = 'explode'
    COLLIDE_ARROW_WITH_OBSTACLE = 'collide_arrow_with_obstacle'
    DECREASE_ENEMY_ENERGY_USING_SWORD = 'decrease_enemy_energy_using_sword'
    DECREASE_ENEMY_ENERGY_USING_BOW = 'decrease_enemy_energy_using_bow'
    DECREASE_ENEMY_ENERGY_USING_EXPLOSION = 'decrease_enemy_energy_using_explosion'
    KILL_ENEMY = 'kill_enemy'

    MOVE_PLAYER = 'move_player'
    MOVE_OBSTACLE = 'move_obstacle'
    LOST_LIFE = 'lost_life'
    COMPLETE_LEVEL = 'complete_level'
    MOVE_ENEMY = 'move_enemy'

    COLLIDE_WITH_ENEMY = 'collide_with_enemy'
    COLLIDE_WITH_HOSTILE_FORCE = 'collide_with_hostile_force'

    OPEN_DOOR = 'open_door'
    TELEPORT = 'teleport'
    SHOW_EXIT_POINT = 'show_exit_point'
