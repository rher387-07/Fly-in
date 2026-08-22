import pygame

from renderer.platform import Platform
from renderer.camera import Camera
from renderer.drone import Drone


class Game:
    def __init__(self, network):
        pygame.init()

        self.screen = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()
        self.running = True

        self.network = network

        self.tile_size = 128
        self.offset_x = 100
        self.offset_y = 100

        self.camera = Camera(1280, 720)

        self.platform_image = pygame.image.load(
            "asset/platform/1_Industrial_Tileset_1B.png"
        ).convert_alpha()

        self.drone_image = pygame.image.load(
            "asset/drone/Idle.png"
        ).convert_alpha()

        self.drone = Drone(
            self.drone_image
        )

        self.platforms = pygame.sprite.Group()
        self.start_platform = None

        self.create_platforms()

    def create_platforms(self):
        for hub in self.network.hubs.values():
            platform = Platform(
                hub,
                self.platform_image
            )

            self.platforms.add(platform)

            if hub.name.lower() == "start":
                self.start_platform = platform

    def check_collisions(self):
        hits = pygame.sprite.spritecollide(
            self.drone,
            self.platforms,
            False
        )

        for platform in hits:
            print(
                f"[COLLISION] Le drone se trouve sur la plateforme "
                f"'{platform.hub.name}'"
            )

    def draw(self):
        self.screen.fill((30, 30, 30))

        for platform in self.platforms:
            platform.draw(
                self.screen,
                self.tile_size,
                self.tile_size,
                self.offset_x,
                self.offset_y,
                self.camera
            )

        if self.start_platform is not None:
            self.drone.draw(
                self.screen,
                self.start_platform,
                self.camera
            )

        pygame.display.flip()

    def run(self):
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.drone.update()
            self.camera.update()
            self.draw()
            self.check_collisions()

            self.clock.tick(60)

        pygame.quit()
