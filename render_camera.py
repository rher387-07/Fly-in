#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render_camera.py                                     :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:33:09 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/21 15:35:59 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame


class Camera:
    """A 2D camera handling panning and zooming for the rendered view.

    Attributes:
        width (int): Width of the viewport, in pixels.
        height (int): Height of the viewport, in pixels.
        x (int): Camera's horizontal offset (panning position).
        y (int): Camera's vertical offset (panning position).
        speed (int): Number of pixels the camera moves per `update` call
            when a directional key is held.
        zoom (float): Current zoom factor.
        zoom_step (float): Amount added to or subtracted from `zoom` by
            `zoom_in`/`zoom_out`.
        zoom_min (float): Minimum allowed zoom factor.
        zoom_max (float): Maximum allowed zoom factor.
    """
    def __init__(self, width: int, height: int) -> None:
        """Initializes the camera.

        Args:
            width (int): Width of the viewport, in pixels.
            height (int): Height of the viewport, in pixels.
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
        """Moves the camera based on currently pressed directional keys.

        Reads the keyboard state and pans the camera (arrow keys or
        numpad 2/4/6/8) at `self.speed` pixels per call. Intended to be
        called once per frame.
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
        """Increases the zoom factor by `zoom_step`, capped at `zoom_max`.
        """
        self.zoom = min(self.zoom + self.zoom_step, self.zoom_max)

    def zoom_out(self) -> None:
        """Decreases the zoom factor by `zoom_step`, floored at `zoom_min`.
        """
        self.zoom = max(self.zoom - self.zoom_step, self.zoom_min)

    def apply(self, x: float, y: float) -> tuple[float, float]:
        """Converts world coordinates to screen coordinates.

        Applies the camera's current pan offset and zoom factor to a
        point in world space.

        Args:
            x (int): X coordinate in world space.
            y (int): Y coordinate in world space.

        Returns:
            tuple[float, float]: The corresponding (x, y) coordinates in
            screen space.
        """
        return ((x - self.x) * self.zoom, (y - self.y) * self.zoom)
