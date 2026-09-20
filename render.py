#!/usr/bin/env python3
# ########################################################################### #
#   shebang: 1                                                                #
#                                                          :::      ::::::::  #
#   render.py                                            :+:      :+:    :+:  #
#                                                      +:+ +:+         +:+    #
#   By: hery-rak <hery-rak@student.42antananarivo.   +#+  +:+       +#+       #
#                                                  +#+#+#+#+#+   +#+          #
#   Created: 2026/09/11 23:52:06 by hery-rak            #+#    #+#            #
#   Updated: 2026/09/20 15:26:56 by hery-rak           ###   ########.fr      #
#                                                                             #
# ########################################################################### #

import pygame

from parser_models import Network
from render_camera import Camera
from render_drone import Drone
from render_platform import Platform

W_FENETRE = 1920
H_FENETRE = 1000

PLATF = "asset/platform/1_Industrial_Tileset_1B.png"
DRONE = "asset/drone/free-drones-pack-pixel-art/1 Drones/2/Forward.png"
BACKGROUND = "asset/cloud/1.png"
MENU_BACKGROUND = "asset/menu/fond.jpeg"
START_BUTTON = "asset/menu/Start_Button.png"
EXIT_BUTTON = "asset/menu/Exit_Button.png"

MIN_SPACING_X = 200
MIN_SPACING_Y = 200


class BoutonImage:
    """A clickable image button with a "hover" (mouse-over) image state.
    """
    def __init__(self, x, y, chemin_image, largeur, hauteur):
        """Initializes the button and loads/scales its images.

        Args:
            x (int): X position (top-left) of the button.
            y (int): Y position (top-left) of the button.
            chemin_image (str): Path to the button's image file.
            largeur (int): Width, in pixels, the normal image is scaled
                to. The hover image is scaled to 1.5x this width.
            hauteur (int): Height, in pixels, both images are scaled to.
        """
        self.image_normale = pygame.image.load(chemin_image).convert_alpha()
        self.image_normale = pygame.transform.smoothscale(self.image_normale, (largeur, hauteur))
        self.image_survol = pygame.transform.smoothscale(
            self.image_normale, (int(largeur * 1.5), int(hauteur))
        )
        self.rect = self.image_normale.get_rect(topleft=(x, y))

    def draw(self, surface):
        """Draws the button, swapping to the hover image under the mouse.

        Args:
            surface (pygame.Surface): Surface to draw the button onto.
        """
        souris = pygame.mouse.get_pos()
        if self.rect.collidepoint(souris):
            image = self.image_survol
            rect = image.get_rect(center=self.rect.center)
        else:
            image = self.image_normale
            rect = self.rect
        surface.blit(image, rect)

    def press(self, event):
        """Checks whether an event is a left click on this button.

        Args:
            event (pygame.event.Event): The pygame event to check.

        Returns:
            bool: True if `event` is a left mouse button-down click
            landing inside the button's (normal, non-hover) rect, False
            otherwise.
        """
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            return self.rect.collidepoint(event.pos)
        return False


class Lancer:
    """Runs the pygame menu and the graphical rendering of the simulation.

    Owns the pygame window, camera, sprites (platforms and drones), and
    the main menu/game loops.
    """
    def __init__(self, network: Network, schedules: list[tuple[list[str], list[tuple[str, str, int, int]]]], filename: str, turn: int) -> None:
        """Initializes pygame, loads assets, and lays out the network.

        Args:
            network (Network): The network to render (hubs and
                connections).
            schedules (list[tuple[list[str], list[tuple[str, str, int, int]]]]):
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
        self.running = True
        self.paused = False
        self.simulation_time = 0.0
        self.camera = Camera(W_FENETRE, H_FENETRE)
        self.platform_image = self.load_tile(PLATF, 0, 0, 96, 32)
        self.restricted_image = self.load_tile(PLATF, 96, 0, 32, 32)
        self.forward_image = pygame.image.load(
            DRONE
        ).convert_alpha()
        self.background = pygame.image.load(BACKGROUND).convert()
        self.platforms: pygame.sprite.Group = pygame.sprite.Group()
        self.platforms_by_name: dict[str, Platform] = {}
        self.drones = [
            Drone(self.forward_image)
            for _ in schedules
        ]
        self.offset_x, self.offset_y, self.spacing_x, self.spacing_y = (
            self._layout()
        )
        self.create_platform()

    def load_tile(
        self, path: str, x: int, y: int, width: int, height: int
    ) -> pygame.Surface:
        """Extracts a single tile from a tileset image.

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
        """Computes the camera zoom and offsets needed to fit the map.

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
        """Creates and registers a `Platform` sprite for each network hub.
        """
        for hub in self.network.hubs.values():
            platform = Platform(hub, self.platform_image, self.network)
            self.platforms.add(platform)
            self.platforms_by_name[hub.name] = platform

    def _screen_position(self, name: str) -> tuple[int, int]:
        """Computes the on-screen center position of a named platform.

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
        """Computes a drone's interpolated on-screen position at a given time.

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
        """Computes a drone's animation speed multiplier at a given time.

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

    def draw_background(self) -> None:
        """Draws the background image, scaled to fill the window.
        """
        background = pygame.transform.scale(
            self.background, (W_FENETRE, H_FENETRE)
        )
        self.screen.blit(background, background.get_rect())

    def draw_connections(self) -> None:
        """Draws every connection as a line, with a marker on restricted legs.

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
        """Renders a full simulation frame: background, hubs, and drones.

        Clears the screen, draws the background, the connections between
        hubs, every platform, then every drone at its interpolated
        position for `self.simulation_time`, and finally flips the
        display.
        """
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


    def draw_text_shadow(self, font: pygame.font.Font, message: str, screen_: pygame.Surface, width: int, height: int):
        """Draws text with a drop shadow for readability.

        Renders `message` twice: once offset in a dark shadow color,
        then once on top in the main color, at (width, height).

        Args:
            font (pygame.font.Font): Font used to render the text.
            message (str): Text to draw.
            screen_ (pygame.Surface): Surface to draw the text onto.
            width (int): X position of the main (non-shadow) text.
            height (int): Y position of the main (non-shadow) text.
        """
        blue_cyan = (0, 200, 200)
        shadow = (54, 51, 46)
        msg = font.render(message, True, blue_cyan)
        msg_shadow = font.render(message, True, shadow)

        screen_.blit(msg_shadow, (width+10, height+5))
        screen_.blit(msg, (width, height))


    def draw_menu(self, screen_menu: pygame.Surface):
        """Draws the info panel shown on the main menu screen.

        Displays the map filename, number of drones, start/end hub
        names, hub count, and total turn count, each with a drop shadow.

        Args:
            screen_menu (pygame.Surface): Surface (the menu screen) to
                draw the info panel.
        """
        font = pygame.font.SysFont("Arial", 24, bold=True)
        self.draw_text_shadow(font, "[INFO]", screen_menu, 240, 30)
        self.draw_text_shadow(font, f"Map: {self.filename}", screen_menu, 35, 90)
        self.draw_text_shadow(font, f"Number of drones: {self.network.nb_drones}", screen_menu, 35, 125)
        self.draw_text_shadow(font, f"Start area:   {self.network.start_hub.name}", screen_menu, 35, 160)
        self.draw_text_shadow(font, f"Finish area:  {self.network.end_hub.name}", screen_menu, 35,195)
        self.draw_text_shadow(font, f"Number of hubs:   {len(self.network.hubs)}", screen_menu, 35, 230)
        self.draw_text_shadow(font, f"Turn:   {self.turn}", screen_menu, 35, 265)


    def menu_window(self) -> str:
        """Runs the main menu loop until the user picks an action.

        Displays the menu background, the info panel, and Start/Exit
        buttons, and reacts to quit events, Escape, and button clicks.

        Returns:
            str: "jouer" if the user clicked Start, "quitter" if they
            quit the window, pressed Escape, or clicked Exit.
        """
        w_fenetre = 1920//2
        h_fenetre = 1080//2
        menu_screen = pygame.display.set_mode((w_fenetre, h_fenetre))
        pygame.display.set_caption("Menu Principal")

        fond_image = pygame.image.load(MENU_BACKGROUND).convert()
        fond_image = pygame.transform.smoothscale(fond_image, (w_fenetre, h_fenetre))

        largeur_bouton = 100
        hauteur_bouton = 50
        espace = 25
        marge_x = 220
        y_depart = h_fenetre//2 + 95

        bouton_start = BoutonImage(marge_x, y_depart, START_BUTTON, largeur_bouton, hauteur_bouton)
        bouton_exit = BoutonImage(marge_x, y_depart + (hauteur_bouton + espace), EXIT_BUTTON, largeur_bouton, hauteur_bouton)


        en_menu = True
        action = "quitter"
        while en_menu:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    action = "quitter"
                    en_menu = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        action = "quitter"
                        en_menu = False
                elif bouton_start.press(event):
                    action = "jouer"
                    en_menu = False

                elif bouton_exit.press(event):
                    action = "quitter"
                    en_menu = False


            menu_screen.blit(fond_image, (0, 0))
            self.draw_menu(menu_screen)
            bouton_start.draw(menu_screen)
            bouton_exit.draw(menu_screen)
            pygame.display.flip()
            self.clock.tick(60)

        return action

    def run(self) -> None:
        """Shows the menu, then runs the simulation's main loop.

        If the menu is dismissed without choosing "jouer" (play), exits
        immediately after shutting down pygame. Otherwise, reopens the
        simulation window and loops: handling input (quit, Escape,
        Space to pause, +/- on the numpad to zoom), advancing simulation
        time while unpaused, updating the camera, and drawing each
        frame, until the window is closed.
        """
        action = self.menu_window()
        if action != "jouer":
            pygame.quit()
            return

        self.screen = pygame.display.set_mode((W_FENETRE, H_FENETRE))
        pygame.display.set_caption("Fly-in")

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
                    self.clock.get_time() / 1000 / 0.7
                )
            self.camera.update()
            self.draw()
            self.clock.tick(60)
        pygame.quit()
