#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   drone.py                                             :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/11 23:59:59 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #


import pygame
from .platform import Platform
from .camera import Camera


class Drone(pygame.sprite.Sprite):
    def __init__(
        self,
        sprite: pygame.Surface,
        forward_sprite: pygame.Surface | None = None,
    ) -> None:
        self.sprite = sprite

        self.frame_w = 48
        self.frame_h = 48
        self.frames = []
        self.velocity = 10
        self.speed_x = 3
        self.x = 0.0
        self.direction = 1

        animation = forward_sprite or sprite
        for i in range(4):
            frame = pygame.Surface(
                (self.frame_w, self.frame_h),
                pygame.SRCALPHA)

            frame.blit(
                animation,
                (0, 0),
                pygame.Rect(i*self.frame_w, 0, self.frame_w, self.frame_h))
            self.frames.append(frame)

        self.current_frame = 0
        self.speed = 100
        self.last_update = pygame.time.get_ticks()

        self.image: pygame.Surface = self.frames[0]
        self.rect = self.image.get_rect()

    def update(self, speed_multiplier: float = 1.0) -> None:
        """Advance the sprite animation at the requested movement speed."""
        if speed_multiplier <= 0:
            return
        now = pygame.time.get_ticks()
        frame_delay = int(self.speed / max(speed_multiplier, 0.1))

        if now - self.last_update >= frame_delay:
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.current_frame = 0

            self.image = self.frames[self.current_frame]
            self.last_update = now

        self.x = self.speed * self.direction

    def draw(
        self,
        screen: pygame.Surface,
        platform: Platform | None,
        camera: Camera
    ) -> None:
        if platform is not None:
            x = platform.rect.centerx
            y = platform.rect.top + self.velocity
        else:
            x = int(self.x)
            y = int(self.rect.centery)

        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)

        image = pygame.transform.scale(self.image, (width, height))
        self.rect = image.get_rect(midbottom=(x, y))
        screen.blit(image, self.rect)

    def draw_at(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        camera: Camera,
    ) -> None:
        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)
        image = pygame.transform.scale(self.image, (width, height))
        position_drone = (position[0], position[1] - 30*camera.zoom)
        self.rect = image.get_rect(center=position_drone)
        screen.blit(image, self.rect)
