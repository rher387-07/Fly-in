#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render_platform.py                                   :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 12:09:02 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/21 18:02:35 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame
import time
from parser_models import Network, Hub
from render_camera import Camera


class Platform(pygame.sprite.Sprite):
    """A hub sprite, rendered as a platform with its name label.
    """
    def __init__(
        self,
        hub: Hub,
        image: pygame.Surface,
        network: Network
    ) -> None:
        """Initializes the platform sprite for a given hub.

        Args:
            hub (Hub): The hub this platform represents.
            image (pygame.Surface): Base image used to render the
                platform.
            network (Network): The network the hub belongs to; used to
                identify whether this hub is the start or end hub.

        Raises:
            ValueError: If `network` does not define both a `start_hub`
                and an `end_hub`.
        """
        super().__init__()
        self.network = network
        if network.start_hub is None or network.end_hub is None:
            raise ValueError("network must define start_hub and end_hub")
        self.start_name = network.start_hub.name
        self.end_name = network.end_hub.name
        self.hub = hub
        self.image = image

        self.x = hub.x
        self.y = hub.y

        self.bar: float = 100
        self.max_bar: float = 100

        self.max_drones = hub.max_drones

        self.rect = self.image.get_rect()
        self.font = pygame.font.Font(None, 22)
        self.paused = False

    def __str__(self) -> str:
        return self.hub.name

    def _get_color_random(self) -> tuple[int, int, int]:
        """Generates a smoothly cycling RGB color based on elapsed time.

        Used for hubs with `zone_type` (or color) "rainbow", so their
        label color shifts continuously over time.

        Returns:
            tuple[int, int, int]: An (r, g, b) color, each channel in
            the 0-255 range.
        """
        from math import sin
        now = time.time()
        r = int((sin(now) * 127 + 127))
        g = int(sin(now + 2) * 127 + 127)
        b = int(sin(now + 4) * 127 + 127)
        return (r, g, b)

    def draw_platform(
        self,
        screen: pygame.Surface,
        space_x: int,
        space_y: int,
        offset_x: float,
        offset_y: float,
        camera: Camera
    ) -> None:
        """Draws the platform and its hub name label on screen.

        Converts the hub's grid coordinates to screen coordinates using
        the given spacing/offset and the camera's pan and zoom, then
        renders the platform image followed by the hub's name (colored
        according to `hub.color`, or cycling if "rainbow") just below it.

        Args:
            screen (pygame.Surface): Surface to draw the platform onto.
            space_x (int): Horizontal pixel spacing between grid units.
            space_y (int): Vertical pixel spacing between grid units.
            offset_x (int): Horizontal pixel offset applied before
                scaling by `space_x`.
            offset_y (int): Vertical pixel offset applied before scaling
                by `space_y`.
            camera (Camera): Camera providing the current pan offset and
                zoom factor.

        Raises:
            ValueError: If `hub.color` is not a valid color name or
                value recognized by `pygame.Color`.
        """

        window_x = offset_x + self.x * space_x
        window_y = offset_y + self.y * space_y

        screen_x, screen_y = camera.apply(window_x, window_y)

        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)

        image = pygame.transform.scale(self.image, (width, height))

        self.rect = image.get_rect(topleft=(screen_x, screen_y))

        # ajust_x = 24
        # ajust_y = 38

        screen.blit(image, self.rect)

        color_hub: pygame.Color | tuple[int, int, int]
        try:
            if self.hub.color == "rainbow":
                color_hub = self._get_color_random()
            elif self.hub.color:
                color_hub = pygame.Color(self.hub.color)
            else:
                color_hub = pygame.Color("white")

        except ValueError as e:
            raise ValueError(f"Colors Invalid: '{self.hub.color}'") from e

        name_hub = self.font.render(self.hub.name, True, color_hub)
        w_name_hub = int(name_hub.get_width() * camera.zoom)
        h_name_hub = int(name_hub.get_height() * camera.zoom)

        name_hub = pygame.transform.scale(name_hub, (w_name_hub, h_name_hub))
        name_hub_rect = name_hub.get_rect(
            midtop=(self.rect.centerx,
                    self.rect.bottom + int(10 * camera.zoom)
                    )
        )
        screen.blit(name_hub, name_hub_rect)

        # return (self.rect.x + ajust_x, self.rect.y - ajust_y)
