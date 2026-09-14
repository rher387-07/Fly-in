#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:06 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/14 22:14:18 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

from typing import Dict, List, Tuple

import pygame

from parser.models import Network
from .camera import Camera
from .drone import Drone
from .platform import Platform

W_FENETRE = 1280
H_FENETRE = 800
PATH_PLATF = "asset/platform/1_Industrial_Tileset_1B.png"
PATH_DRONE = "asset/drone/Idle.png"
PATH_DRONE_FORWARD = "asset/drone/Forward.png"
BACKGROUND_PATH = "asset/cloud/1.png"
MOON_PATH = "asset/cloud/2.png"
TURN_SECONDS = 0.7
MIN_SPACING_X = 200
MIN_SPACING_Y = 200
Schedule = Tuple[List[str], List[Tuple[str, str, int, int]]]


class Lancer:
    def __init__(self, network: Network, schedules: List[Schedule]) -> None:
        if network.start_hub is None or network.end_hub is None:
            raise ValueError("network must define start_hub and end_hub")
        pygame.init()
        pygame.display.set_caption("Fly-in")
        self.screen = pygame.display.set_mode((W_FENETRE, H_FENETRE))
        self.clock = pygame.time.Clock()
        self.network = network
        self.start_name = network.start_hub.name
        self.end_name = network.end_hub.name
        self.schedules = schedules
        self.running = True
        self.paused = False
        self.simulation_time = 0.0
        self.camera = Camera(W_FENETRE, H_FENETRE)
        self.platform_image = self.load_tile(PATH_PLATF, 0, 0, 96, 32)
        self.restricted_image = self.load_tile(PATH_PLATF, 96, 0, 32, 32)
        self.drone_image = pygame.image.load(PATH_DRONE).convert_alpha()
        self.forward_image = pygame.image.load(
            PATH_DRONE_FORWARD
        ).convert_alpha()
        self.background = pygame.image.load(BACKGROUND_PATH).convert()
        self.moon = pygame.image.load(MOON_PATH).convert_alpha()
        self.platforms: pygame.sprite.Group = pygame.sprite.Group()
        self.platforms_by_name: Dict[str, Platform] = {}
        self.drones = [
            Drone(self.drone_image, self.forward_image)
            for _ in schedules
        ]
        self.offset_x, self.offset_y, self.spacing_x, self.spacing_y = (
            self._layout()
        )
        self.create_platform()

    def load_tile(
        self, path: str, x: int, y: int, width: int, height: int
    ) -> pygame.Surface:
        tileset = pygame.image.load(path).convert_alpha()
        tile = pygame.Surface((width, height), pygame.SRCALPHA)
        tile.blit(tileset, (0, 0), pygame.Rect(x, y, width, height))
        return tile

    def _layout(self) -> Tuple[float, float, int, int]:
        hubs = list(self.network.hubs.values())
        min_x = min(hub.x for hub in hubs)
        max_x = max(hub.x for hub in hubs)
        min_y = min(hub.y for hub in hubs)
        max_y = max(hub.y for hub in hubs)
        spacing_x = MIN_SPACING_X
        spacing_y = MIN_SPACING_Y
        available_width = W_FENETRE - 160
        available_height = H_FENETRE - 220
        span_x = max(max_x - min_x, 1)
        span_y = max(max_y - min_y, 1)
        zoom_x = available_width / (span_x * spacing_x)
        zoom_y = available_height / (span_y * spacing_y)

        self.camera.zoom = min(1.0, zoom_x, zoom_y)
        offset_x = 80 / self.camera.zoom - min_x * spacing_x
        offset_y = 140 / self.camera.zoom - min_y * spacing_y
        return offset_x, offset_y, spacing_x, spacing_y

    def create_platform(self) -> None:
        for hub in self.network.hubs.values():
            platform = Platform(hub, self.platform_image, self.network)
            self.platforms.add(platform)
            self.platforms_by_name[hub.name] = platform

    def _screen_position(self, name: str) -> Tuple[int, int]:
        platform = self.platforms_by_name[name]
        x = self.offset_x + platform.x * self.spacing_x
        y = self.offset_y + platform.y * self.spacing_y
        screen_x, screen_y = self.camera.apply(int(x), int(y))
        width = platform.image.get_width() * self.camera.zoom
        height = platform.image.get_height() * self.camera.zoom
        return int(screen_x + width / 2), int(
            screen_y + height / 2
        )

    def _drone_position(
        self, movements: List[Tuple[str, str, int, int]], time: float
    ) -> Tuple[int, int]:
        if not movements:
            return self._screen_position(self.start_name)
        first_name = movements[0][0]
        for first, second, departure, arrival in movements:
            if time < departure:
                return self._screen_position(first)
            if time <= arrival:
                start = self._screen_position(first)
                end = self._screen_position(second)
                ratio = (time - departure) / max(arrival - departure, 1)
                x = int(start[0] + (end[0] - start[0]) * ratio)
                y = int(start[1] + (end[1] - start[1]) * ratio)
                return x, y
            first_name = second
        return self._screen_position(first_name)

    def _drone_speed(
        self, movements: List[Tuple[str, str, int, int]], time: float
    ) -> float:
        for _, second, departure, arrival in movements:
            if departure <= time <= arrival:
                if self.network.hubs[second].zone_type == "restricted":
                    return 0.5
                return 1.0
        return 1.0

    def draw_background(self) -> None:
        background = pygame.transform.scale(
            self.background, (W_FENETRE, H_FENETRE)
        )
        self.screen.blit(background, background.get_rect())
        moon = pygame.transform.scale(self.moon, (640, 400))
        self.screen.blit(moon, moon.get_rect())

    def draw_connections(self) -> None:
        for connection in self.network.connections:
            first = self._screen_position(connection.hub1)
            second = self._screen_position(connection.hub2)
            pygame.draw.line(
                self.screen, (255, 255, 255), first, second, 2
            )
            if self.network.hubs[connection.hub2].zone_type == "restricted":
                marker = pygame.transform.scale(
                    self.restricted_image,
                    (
                        int(
                            self.restricted_image.get_width()
                            * self.camera.zoom
                        ),
                        int(
                            self.restricted_image.get_height()
                            * self.camera.zoom
                        ),
                    ),
                )
                marker_rect = marker.get_rect(
                    center=(
                        (first[0] + second[0]) // 2,
                        (first[1] + second[1]) // 2,
                    )
                )
                self.screen.blit(marker, marker_rect)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        self.draw_background()
        self.draw_connections()
        for platform in self.platforms:
            platform.draw_platform(
                self.screen,
                self.spacing_x,
                self.spacing_y,
                self.offset_x,
                self.offset_y,
                self.camera,
            )
        for drone, (_, movements) in zip(self.drones, self.schedules):
            speed = self._drone_speed(movements, self.simulation_time)
            drone.update(speed)
            drone.draw_at(
                self.screen,
                self._drone_position(movements, self.simulation_time),
                self.camera,
            )
        pygame.display.flip()

    def run(self) -> None:
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        self.running = False
                    elif event.key == pygame.K_SPACE:
                        self.paused = not self.paused
                    elif event.key == pygame.K_KP_MINUS:
                        self.camera.zoom_out()
                    elif event.key == pygame.K_KP_PLUS:
                        self.camera.zoom_in()
            if not self.paused:
                self.simulation_time += (
                    self.clock.get_time() / 1000 / TURN_SECONDS
                )
            self.camera.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
