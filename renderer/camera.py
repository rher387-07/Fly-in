#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   camera.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:33:09 by hery-rak            #+#    #+#            #
#   Updated: 2026/08/22 15:36:32 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame


class Camera:
    def __init__(self, width: int, height: int) -> None:
        self.width = width
        self.height = height

        self.x = 0
        self.y = 0
        self.speed = 10
        self.zoom = 1.0
        self.zoom_step = 0.1
        self.zoom_min = 0.5
        self.zoom_max = 2.0

    def update(self) -> None:
        key = pygame.key.get_pressed()

        if key[pygame.K_LEFT] or key[pygame.K_KP4]:
            self.x -= self.speed

        if key[pygame.K_RIGHT] or key[pygame.K_KP6]:
            self.x += self.speed

        if key[pygame.K_UP] or key[pygame.K_KP8]:
            self.y -= self.speed

        if key[pygame.K_DOWN] or key[pygame.K_KP2]:
            self.y += self.speed

    def zoom_in(self) -> None:
        self.zoom = min(self.zoom + self.zoom_step, self.zoom_max)

    def zoom_out(self) -> None:
        self.zoom = max(self.zoom - self.zoom_step, self.zoom_min)

    def apply(self, x: int, y: int) -> tuple[float, float]:
        return ((x - self.x) * self.zoom, (y - self.y) * self.zoom)
