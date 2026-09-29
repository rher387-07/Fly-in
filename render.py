#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:06 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/29 12:53:21 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

"""Pygame rendering management."""


import pygame

from parser_models import Network
from render_camera import Camera
from render_drone import Drone
from render_platform import Platform

W_FENETRE = 1800
H_FENETRE = 900

PLATF = "asset/platform/1.png"
DRONE = "asset/drone/1.png"
BACKGROUND = "asset/cloud/1.png"


class Lancer:
    """Manages the graphical rendering of the simulation using Pygame.

    Handles the Pygame window, the camera,
    the sprites (platforms and drones), as well as
    the main loop and the game loop.
    """

    def __init__(self,
                 network: Network,
                 schedules: list[tuple[list[str],
                                       list[tuple[str, str, int, int]]]],
                 filename: str,
                 turn: int,
                 velocity: int
                 ) -> None:
        """Initialize pygame, loads assets, and lays out the network.

        Args:
            network (Network): The network to render (hubs and
                connections).
            schedules (list[tuple[list[str],
                       list[tuple[str, str, int, int]]]]):
                Per-drone schedules. Each entry pairs a path (list of
                hub names) with its list of movements, where each
                movement is (from_hub, to_hub, departure_time,
                arrival_time).
            filename (str): Path of the map file being rendered, shown
                in the on-screen info panel.
            turn (int): Total number of turns in the simulation, shown
                in the on-screen info panel.

        Raises:
            ValueError: If `network` does not define both a `start_hub`
                and an `end_hub`.
        """
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
        self.filename = filename
        self.turn = turn
        self.velocity = velocity
        self.running = True
        self.paused = False
        self.simulation_time = 0.0
        self.camera = Camera(W_FENETRE, H_FENETRE)
        self.platform_image = self._load_tile(PLATF, 0, 0, 96, 32)
        self.restricted_image = self._load_tile(PLATF, 96, 0, 32, 32)
        self.drone_image = pygame.image.load(DRONE).convert_alpha()
        self.background = pygame.image.load(BACKGROUND).convert()
        self.platforms: pygame.sprite.Group[
            Platform] = pygame.sprite.Group()
        self.platforms_by_name: dict[str, Platform] = {}
        self.drones = [Drone(self.drone_image) for _ in schedules]
        (self.offset_x, self.offset_y,
         self.spacing_x, self.spacing_y) = (self._layout())
        self._create_platform()
        self.hint_font = pygame.font.SysFont("Arial", 15, bold=True)

    def _load_tile(
        self, path: str, x: int, y: int, width: int, height: int
    ) -> pygame.Surface:
        """Extract a single tile from a tileset image.

        Args:
            path (str): Path to the tileset image file.
            x (int): X offset, in pixels, of the tile within the
                tileset.
            y (int): Y offset, in pixels, of the tile within the
                tileset.
            width (int): Width, in pixels, of the tile to extract.
            height (int): Height, in pixels, of the tile to extract.

        Returns:
            pygame.Surface: A new surface containing just the extracted
            tile, with per-pixel alpha.
        """
        tileset = pygame.image.load(path).convert_alpha()
        tile = pygame.Surface((width, height), pygame.SRCALPHA)
        tile.blit(tileset, (0, 0), pygame.Rect(x, y, width, height))
        return tile

    def _layout(self) -> tuple[float, float, int, int]:
        """Compute the camera zoom and offsets needed to fit the map.

        Finds the bounding box of all hub coordinates and sets
        `self.camera.zoom` (capped at 1.0) so the whole network fits
        within the window, then derives the pixel offsets needed to
        position it.

        Returns:
            tuple[float, float, int, int]: The (offset_x, offset_y,
            spacing_x, spacing_y) values used to convert hub grid
            coordinates to window coordinates.
        """
        hubs = list(self.network.hubs.values())
        min_x = min(hub.x for hub in hubs)
        max_x = max(hub.x for hub in hubs)
        min_y = min(hub.y for hub in hubs)
        max_y = max(hub.y for hub in hubs)
        spacing_x = 200
        spacing_y = 200
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

    def _create_platform(self) -> None:
        """Create and registers a `Platform` sprite for each network hub."""
        for hub in self.network.hubs.values():
            platform = Platform(hub, self.platform_image, self.network)
            self.platforms.add(platform)
            self.platforms_by_name[hub.name] = platform

    def _screen_position(self, name: str) -> tuple[int, int]:
        """Compute the on-screen center position of a named platform.

        Args:
            name (str): Name of the hub/platform to locate.

        Returns:
            tuple[int, int]: The (x, y) screen coordinates of the
            platform's center, after applying layout spacing/offsets
            and the camera's pan and zoom.
        """
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
        self, movements: list[tuple[str, str, int, int]], time: float
    ) -> tuple[int, int]:
        """Compute a drone's interpolated on-screen position at a given time.

        Walks the drone's list of movements to find which leg `time`
        falls into, then linearly interpolates its screen position
        between the leg's start and end hubs. Before the drone's first
        departure, or after its last arrival, it stays put at the
        corresponding hub.

        Args:
            movements (list[tuple[str, str, int, int]]): The drone's
                movements, each as (from_hub, to_hub, departure_time,
                arrival_time).
            time (float): Current simulation time.

        Returns:
            tuple[int, int]: The drone's (x, y) screen coordinates at
            `time`.
        """
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
        self, movements: list[tuple[str, str, int, int]], time: float
    ) -> float:
        """Compute a drone's animation speed multiplier at a given time.

        The multiplier is halved while the drone is flying into a
        "restricted" zone hub, and 1.0 otherwise.

        Args:
            movements (list[tuple[str, str, int, int]]): The drone's
                movements, each as (from_hub, to_hub, departure_time,
                arrival_time).
            time (float): Current simulation time.

        Returns:
            float: 0.5 if `time` falls within a leg arriving at a
            "restricted" hub, 1.0 otherwise.
        """
        for _, second, departure, arrival in movements:
            if departure <= time <= arrival:
                if self.network.hubs[second].zone_type == "restricted":
                    return 0.5
                return 1.0
        return 1.0

    def _draw_background(self) -> None:
        """Draw the background image, scaled to fill the window."""
        background = pygame.transform.scale(
            self.background, (W_FENETRE, H_FENETRE)
        )
        self.screen.blit(background, background.get_rect())

    def _draw_connections(self) -> None:
        """Draw every connection as a line, with a marker on restricted legs.

        For each connection whose second hub is a "restricted" zone, a
        warning marker is also drawn at the connection's midpoint.
        """
        for connection in self.network.connections:
            first = self._screen_position(connection.hub1)
            second = self._screen_position(connection.hub2)
            pygame.draw.line(
                self.screen, (255, 255, 255), first, second, 1
            )
            if self.network.hubs[connection.hub2].zone_type == "restricted":
                img_w = self.restricted_image.get_width()
                img_h = self.restricted_image.get_height()
                marker = pygame.transform.scale(
                    self.restricted_image,
                    (
                        int(img_w * self.camera.zoom),
                        int(img_h * self.camera.zoom),
                    ),
                )
                marker_rect = marker.get_rect(
                    center=(
                        (first[0] + second[0]) // 2,
                        (first[1] + second[1]) // 2,
                    )
                )
                self.screen.blit(marker, marker_rect)

    def _draw_controls_hint(self) -> None:
        """Draw a full-width bottom bar listing the keyboard controls.

        Renders a single rounded-corner panel spanning the whole width
        of the window, anchored to the bottom of the screen, and split
        into as many equal columns as there are controls (like a table
        row), each with a thin separator on its right edge. Shows:
        Space to pause/resume, +/- (numpad) to zoom in/out, and the
        arrow keys (or numpad 2/4/6/8) to pan the camera.
        """
        all_command = "(ESC)   (SPACE)   (+ -)   (↓ ← → ↑)   (Numpad 2-4-6-8)"
        info = [
            ("Turn", f"{self.turn}"),
            ("number of drones", f"{self.network.nb_drones}"),
            ("map", f"{self.filename}"),
            ("All command", f"{all_command}")
        ]

        panel_height = 48
        panel_width = 1700
        panel_x = 50
        panel_y = 842
        border_radius = 14

        panel = pygame.Surface((panel_width, panel_height), pygame.SRCALPHA)
        pygame.draw.rect(
            panel,
            (20, 20, 20, 170),
            panel.get_rect(),
            border_radius=border_radius,
        )
        pygame.draw.rect(
            panel,
            (255, 255, 255, 60),
            panel.get_rect(),
            width=2,
            border_radius=border_radius,
        )

        column_width = panel_width / len(info)
        for index in range(1, len(info)):
            x = int(column_width * index)
            pygame.draw.line(
                panel,
                (255, 255, 255, 60),
                (x, 10),
                (x, panel_height - 10),
                2,
            )

        self.screen.blit(panel, (panel_x, panel_y))

        for index, (key, action) in enumerate(info):
            column_center = panel_x + int(column_width * (index + 0.5))

            key_surface = self.hint_font.render(key, True, (0, 200, 200))
            key_rect = key_surface.get_rect(
                center=(column_center, panel_y+13)
            )
            self.screen.blit(key_surface, key_rect)

            action_surface = self.hint_font.render(
                action, True, (230, 230, 230)
            )
            action_rect = action_surface.get_rect(
                center=(column_center, panel_y + 35)
            )
            self.screen.blit(action_surface, action_rect)

    def _draw(self) -> None:
        """Render a full simulation frame: background, hubs, and drones.

        Clears the screen, draws the background, the connections between
        hubs, every platform, then every drone at its interpolated
        position for `self.simulation_time`, the controls hint panel,
        and finally flips the display.
        """
        self.screen.fill((0, 0, 0))
        self._draw_background()
        self._draw_connections()
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
            drone.draw(
                self.screen,
                self._drone_position(movements, self.simulation_time),
                self.camera,
            )

        self._draw_controls_hint()
        pygame.display.flip()

    def run(self) -> None:
        """Execute the simulation's main loop.

        The simulation window opens and the loop begins: handling input
        (Quit, Esc, Space to pause, Numpad +/- to zoom), advancing
        simulation time (unless paused), updating the camera,
        and rendering each frame, until the window is closed.
        """
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
                    self.clock.get_time() / 1000 * self.velocity
                )
                if self.simulation_time >= self.turn:
                    self.simulation_time = self.turn
                    self._draw()
                    pygame.time.delay(500)
                    self.running = False
                    continue
            self.camera.update()
            self._draw()
            self.clock.tick(60)
        pygame.quit()
