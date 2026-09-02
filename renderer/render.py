#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/08/22 11:26:52 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/02 10:09:57 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame
from parser.models import Network, Hub
from .camera import Camera
from .drone import Drone
from .platform import Platform

W_FENETRE = 1920
H_FENETRE = 1080
PATH_PLATF = "asset/platform/1_Industrial_Tileset_1B.png"
PATH_DRONE = "asset/drone/Idle.png"
BACKGROUND_PATH = "asset/cloud/1.png"


class Lancer:
    def __init__(
            self,
            network: Network,
            lst_path: list[tuple[float, list[str]]]
            ):
        pygame.init()
        pygame.display.set_caption("Fly-In")

        self.screen = pygame.display.set_mode((W_FENETRE, H_FENETRE))
        self.clock = pygame.time.Clock()
        self.running = True

        self.network = network

        self.offset_x = 200
        self.offset_y = 500
        self.spacing_x = 400
        self.spacing_y = 400

        self.camera = Camera(W_FENETRE, H_FENETRE)

        self.platform_image = self.load_tile(PATH_PLATF, 0, 0, 96, 32)
        self.restricted_image = self.load_tile(PATH_PLATF, 96, 0, 32, 32)
        self.drone_image = pygame.image.load(PATH_DRONE).convert_alpha()
        self.background = pygame.image.load(BACKGROUND_PATH)

        self.drone = Drone(self.drone_image)
        self.platforms: set[Platform] = pygame.sprite.Group()
        self.start_platform: Platform = None
        self.platforms_by_name: dict[str, Platform] = {}

        self.drone_max: dict[str, int] = {}
        self.collid: set = set()
        self.count_drone = 1
        self.path_names = lst_path[0][1] if lst_path else []
        self.create_platform()
        # self.drone.set_pause_points(self.network.connections\
        #  self.platforms_by_name)
        # self.drone.set_path(self.platforms_by_name, self.path_names)

    def load_tile(self, path: str, x: int, y: int, width: int, height: int
                  ) -> pygame.Surface:
        tileset = pygame.image.load(path).convert_alpha()
        tile = pygame.Surface((width, height), pygame.SRCALPHA)

        tile.blit(tileset, (0, 0), pygame.Rect(x, y, width, height))

        return tile

    def create_platform(self) -> None:
        for hub in self.network.hubs.values():
            platform = Platform(hub, self.platform_image, self.network)
            window_x = self.offset_x + platform.x * self.spacing_x
            window_y = self.offset_y + platform.y * self.spacing_y
            screen_x, screen_y = self.camera.apply(window_x, window_y)
            # platform.world_pos = (window_x, window_y)
            platform.rect = platform.image.get_rect(topleft=(screen_x,
                                                             screen_y))
            self.drone_max[platform.hub.name] = platform.max_drones
            self.platforms.add(platform)
            self.platforms_by_name[hub.name] = platform
            if hub.name == self.network.start_hub.name:
                self.start_platform = platform

    def check_collisions(self):
        hits: Platform = pygame.sprite.spritecollide(
            self.drone,
            self.platforms,
            False)

        current_collid = set(hits)
        new_hits: set[Platform] = current_collid - self.collid
        # for x in hits:
        #     self.drone_max[x.hub.name] = x.max_drones

        for hit in new_hits:
            # self.nbr_drone +=1
            hit.check_capacity(True)
            self.drone_max[hit.hub.name] = hit.max_drones - self.count_drone

        left_collid: set[Platform] = self.collid - current_collid
        for hit in left_collid:
            hit.check_capacity(False)
            self.drone_max[hit.hub.name] = hit.max_drones

        self.collid = current_collid

    def draw_connection(self) -> None:
        for connection in self.network.connections:
            hub1: Hub = self.network.hubs[connection.hub1]
            hub2: Hub = self.network.hubs[connection.hub2]

            self.platform1: Platform = next(platform
                                            for platform in self.platforms
                                            if platform.hub.name == hub1.name)
            self.platform2: Platform = next(platform
                                            for platform in self.platforms
                                            if platform.hub.name == hub2.name)

            pygame.draw.line(self.screen,
                             (255, 255, 255),
                             self.platform1.rect.center,
                             self.platform2.rect.center,
                             max(1, int(1 * self.camera.zoom)))

            if hub2.zone_type == "restricted":
                center_x = (self.platform1.rect.centerx
                            + self.platform2.rect.centerx) // 2
                center_y = (self.platform1.rect.centery
                            + self.platform2.rect.centery) // 2

                width = int(self.restricted_image.get_width()
                            * self.camera.zoom)
                height = int(self.restricted_image.get_height()
                             * self.camera.zoom)

                restricted_img = pygame.transform.scale(self.restricted_image,
                                                        (width, height))
                restricted_rect = restricted_img.get_rect(center=(center_x,
                                                                  center_y))

                self.screen.blit(restricted_img, restricted_rect)

    def draw_background(self) -> None:
        background = pygame.transform.scale(self.background,
                                            (W_FENETRE, H_FENETRE))
        bg_rect = background.get_rect()
        # print(background__rect)
        self.screen.blit(background, bg_rect)

    def draw(self) -> None:
        self.screen.fill((0, 0, 0))
        self.draw_background()
        self.draw_connection()
        for platform in self.platforms:
            # print(f"D{i}: {platform.max_drones}")
            platform.draw_platform(
                self.screen,
                self.spacing_x,
                self.spacing_y,
                self.offset_x,
                self.offset_y,
                self.camera
            )
            if (platform.hub.name != self.network.start_hub.name
               and platform.hub.name != self.network.end_hub.name):
                # platform.update_bar_max_drone(self.screen)

                platform.update_bar_max_drone(self.screen, self.camera.zoom)
        self.drone.draw(self.screen, self.start_platform, self.camera)

        pygame.display.flip()

    def run(self) -> None:
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                # print(pygame.K_COMMA)
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_KP_MINUS:
                        self.camera.zoom_out()
                    if event.key == pygame.K_KP_PLUS:
                        self.camera.zoom_in()

            key = pygame.key.get_pressed()
            if key[pygame.K_ESCAPE]:
                self.running = False
            # for i in range(2):
            self.drone.update()
            self.camera.update()
            self.draw()
            self.check_collisions()
            self.clock.tick(60)

        pygame.quit()
