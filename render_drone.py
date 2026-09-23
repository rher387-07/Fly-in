#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render_drone.py                                      :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:52:36 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/23 15:44:29 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Drone management."""

import pygame
from render_camera import Camera


class Drone(pygame.sprite.Sprite):
    """An animated drone sprite rendered either on a platform or in flight.

    Attributes:
        sprite (pygame.Surface): Original drone spritesheet.
        frames (list[pygame.Surface]): Individual animation frames.
        current_frame (int): Index of the currently displayed frame.
        speed (int): Animation update interval in milliseconds.
        x (float): Horizontal animation position.
        direction (int): Horizontal movement direction.
    """

    def __init__(
        self,
        sprite: pygame.Surface,
        forward_sprite: pygame.Surface | None = None,
    ) -> None:
        """Initialize the drone and slices its spritesheet into frames.

        Args:
            sprite (pygame.Surface): Default spritesheet used for the
                drone's animation frames.
            forward_sprite (pygame.Surface | None, optional): Spritesheet
                used instead of `sprite` when the drone is moving forward
                (e.g. a distinct "in flight" animation). Defaults to
                None, in which case `sprite` is used for both.
        """
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
        """Advances the drone's animation frame and horizontal position.

        Frame advancement is time-based: a new frame is shown roughly
        every `self.speed / speed_multiplier` milliseconds, looping back
        to the first frame after the last one.

        Args:
            speed_multiplier (float, optional): Factor controlling how
                fast the animation plays; higher values shorten the
                delay between frames. Values at or below 0 leave the
                drone unchanged (no-op). Defaults to 1.0.
        """
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

    # def draw(
    #     self,
    #     screen: pygame.Surface,
    #     platform: Platform | None,
    #     camera: Camera
    # ) -> None:
    #     """Draws the drone on screen, scaled by the camera's zoom.

    #     If `platform` is given, the drone is anchored just above the
    #     platform's top-center. Otherwise, it is drawn at its own `x`
    #     position and current vertical center.

    #     Args:
    #         screen (pygame.Surface): Surface to draw the drone onto.
    #         platform (Platform | None): The hub/platform to anchor the
    #             drone to, or None to use the drone's own position.
    #         camera (Camera): Camera providing the current zoom factor.
    #     """
    #     if platform is not None:
    #         x = platform.rect.centerx
    #         y = platform.rect.top + self.velocity
    #     else:
    #         x = int(self.x)
    #         y = int(self.rect.centery)

    #     width = int(self.image.get_width() * camera.zoom)
    #     height = int(self.image.get_height() * camera.zoom)

    #     image = pygame.transform.scale(self.image, (width, height))
    #     self.rect = image.get_rect(midbottom=(x, y))
    #     screen.blit(image, self.rect)

    def draw(
        self,
        screen: pygame.Surface,
        position: tuple[int, int],
        camera: Camera,
    ) -> None:
        """Draws the drone at an explicit screen position, zoom-scaled.

        Used to place the drone along a path (e.g. mid-flight between
        two hubs) rather than anchored to a platform. The drone is
        offset slightly upward from `position` so it appears to hover
        above it.

        Args:
            screen (pygame.Surface): Surface to draw the drone onto.
            position (tuple[int, int]): Target (x, y) screen position to
                center the drone above.
            camera (Camera): Camera providing the current zoom factor.
        """
        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)
        image = pygame.transform.scale(self.image, (width, height))
        position_drone = (position[0], position[1] - 30 * camera.zoom)
        self.rect = image.get_rect(center=position_drone)
        screen.blit(image, self.rect)

        # print(f"drone: {self.rect.x} {self.rect.y}")
        # return (self.rect.x, self.rect.y)
