'''
Author: TiiJeiJ8
Project: Survival & Evolution
Info: A simulation of biological evolution
Project Start Date: 2025-02-28

Module: vegetation
Description: This module contains the Vegetation class, which represents the vegetation in the simulation.
'''

# import modules
import numpy as np
import pygame
import random

class Plant(pygame.sprite.Sprite):
    def __init__(self, x, y, cluster_id):
        super().__init__()
        self.image = pygame.Surface((12, 12), pygame.SRCALPHA)
        sides = random.choice([3, 4, 5, 6])
        radius = random.randint(3, 5)
        angle_offset = random.uniform(0, 360)
        points = [
            (
                6 + radius * np.cos(np.radians(angle_offset + i * 360 / sides)),
                6 + radius * np.sin(np.radians(angle_offset + i * 360 / sides))
            ) for i in range(sides)
        ]
        color = random.choice([(169, 211, 173), (146, 185, 190), (210, 214, 153)])
        pygame.draw.polygon(self.image, color, points)
        self.rect = self.image.get_rect(center=(x, y))
        self.energy = 30.0      # 可获取能量
        self.cluster_id = cluster_id  # 所属簇ID