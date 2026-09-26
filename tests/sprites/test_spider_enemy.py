import pygame

from src.sprites.spider_enemy import SpiderEnemy


def create_spider_enemy(rect, min_y_position):
    # Full constructor requires costumes and tile details, which are irrelevant for the culling rectangle
    spider_enemy = object.__new__(SpiderEnemy)
    spider_enemy.rect = rect
    spider_enemy.min_y_position = min_y_position
    return spider_enemy


class TestGetCullingRect:
    def test_covers_net_anchor_above_sprite(self):
        spider_enemy = create_spider_enemy(pygame.Rect(100, 300, 64, 64), 100)
        assert spider_enemy.get_culling_rect() == pygame.Rect(100, 100, 64, 264)

    def test_equals_sprite_rect_at_start_position(self):
        spider_enemy = create_spider_enemy(pygame.Rect(100, 100, 64, 64), 100)
        assert spider_enemy.get_culling_rect() == pygame.Rect(100, 100, 64, 64)
