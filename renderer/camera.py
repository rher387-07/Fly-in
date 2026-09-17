#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   camera.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:33:09 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/17 14:12:19 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame


class Camera:
    """_summary_
    """
    def __init__(self, width: int, height: int) -> None:
        """_summary_

        Args:
            width (int): _description_
            height (int): _description_
        """
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
        """_summary_
        """
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
        """_summary_
        """
        self.zoom = min(self.zoom + self.zoom_step, self.zoom_max)

    def zoom_out(self) -> None:
        """_summary_
        """
        self.zoom = max(self.zoom - self.zoom_step, self.zoom_min)

    def apply(self, x: int, y: int) -> tuple[float, float]:
        """_summary_

        Args:
            x (int): _description_
            y (int): _description_

        Returns:
            tuple[float, float]: _description_
        """
        return ((x - self.x) * self.zoom, (y - self.y) * self.zoom)
