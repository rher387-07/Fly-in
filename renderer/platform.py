#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   platform.py                                          :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 12:09:02 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/16 17:18:50 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame
import time
from parser.models import Network, Hub
from .camera import Camera


class Platform(pygame.sprite.Sprite):
    def __init__(
        self,
        hub: Hub,
        image: pygame.Surface,
        network: Network
    ) -> None:
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
        self.debut = time.time()
        self.paused = False

    def check_capacity(self, flag: bool) -> None:
        amount = 100 / self.hub.max_drones
        if flag is True:
            self.bar -= amount
            # return 1
        elif flag is False:
            self.bar += amount
            # return -1

    def update_bar_max_drone(
        self, surface: pygame.Surface, zoom: float
    ) -> None:
        bar_color = pygame.Color("green")
        bg_bar_color = pygame.Color("grey")

        bar_w = self.max_bar * zoom
        bar_h = 5 * zoom
        offset_x = 50 * zoom

        x = self.rect.centerx - offset_x
        y = self.rect.top + 42 * zoom

        bg_rect = pygame.Rect(x, y, bar_w, bar_h)
        bar_rect = pygame.Rect(x, y, self.bar * zoom, bar_h)

        pygame.draw.rect(surface, bg_bar_color, bg_rect)
        pygame.draw.rect(surface, bar_color, bar_rect)

    def _get_color_rnadom(self) -> tuple[int, int, int]:
        from math import sin
        now = time.time()
        degr = self.debut - now
        r = int((sin(degr) * 127 + 127))
        g = int(sin(degr + 2) * 127 + 127)
        b = int(sin(degr + 4) * 127 + 127)
        return (r, g, b)

    def draw_platform(
        self,
        screen: pygame.Surface,
        space_x: int,
        space_y: int,
        offset_x: int,
        offset_y: int,
        camera: Camera
    ) -> None:

        window_x = offset_x + self.x * space_x
        window_y = offset_y + self.y * space_y

        screen_x, screen_y = camera.apply(window_x, window_y)

        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)

        image = pygame.transform.scale(self.image, (width, height))

        self.rect = image.get_rect(topleft=(screen_x, screen_y))

        screen.blit(image, self.rect)

        # print(self.hub.color)
        color_hub: pygame.Color | tuple[int, int, int]
        try:
            if self.hub.color == "rainbow":
                color_hub = self._get_color_rnadom()
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
        # if self.hub.name == self.start_name or self.hub.name == self.end_name:
        #     d = 10
        # else:
        #     d = 25
        name_hub_rect = name_hub.get_rect(
            midtop=(self.rect.centerx,
                    self.rect.bottom + int(10 * camera.zoom)
                    )
        )
        screen.blit(name_hub, name_hub_rect)

        # if getattr(self, "paused", False):
        #     platform = pygame.Surface((width, height), pygame.SRCALPHA)
        #     platform.fill((255, 255, 0, 90))
        #     screen.blit(platform, self.rect.topleft)
