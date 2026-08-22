import pygame

from renderer.platform import Platform
from renderer.camera import Camera
from renderer.drone import Drone

class Lancer:

    def load_tile(self, path, x, y, width, height):
        tileset = pygame.image.load(path).convert_alpha()

        tile = pygame.Surface(
            (width, height),
            pygame.SRCALPHA
        )

        tile.blit(
            tileset,
            (0, 0),
            pygame.Rect(x, y, width, height)
        )

        return tile

    def __init__(self, network):
        pygame.init()

        self.screen = pygame.display.set_mode((1366, 700))
        pygame.display.set_caption("Fly-in")

        self.clock = pygame.time.Clock()
        self.running = True

        self.network = network

        self.spacing_x = 300
        self.spacing_y = 200

        self.offset_x = 100
        self.offset_y = 100

        self.camera = Camera(1366, 700)

        self.platform_image = self.load_tile(
            "asset/platform/1_Industrial_Tileset_1B.png",
            0,
            0,
            96,
            32
        )

        self.restricted_image = self.load_tile(
            "asset/platform/1_Industrial_Tileset_1B.png",
            96,
            0,
            32,
            32
        )

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

    def draw_connections(self):
        for connection in self.network.connections:

            hub1 = self.network.hubs[connection.hub1]
            hub2 = self.network.hubs[connection.hub2]

            platform1 = next(
                platform
                for platform in self.platforms
                if platform.hub.name == hub1.name
            )

            platform2 = next(
                platform
                for platform in self.platforms
                if platform.hub.name == hub2.name
            )

            pygame.draw.line(
                self.screen,
                (255, 255, 255),
                platform1.rect.center,
                platform2.rect.center,
                max(1, int(4 * self.camera.zoom))
            )

            if hub2.zone_type == "restricted":

                center_x = (
                    platform1.rect.centerx +
                    platform2.rect.centerx
                ) // 2

                center_y = (
                    platform1.rect.centery +
                    platform2.rect.centery
                ) // 2

                width = int(
                    self.restricted_image.get_width()
                    * self.camera.zoom
                )

                height = int(
                    self.restricted_image.get_height()
                    * self.camera.zoom
                )

                restricted_image = pygame.transform.scale(
                    self.restricted_image,
                    (width, height)
                )

                restricted_rect = restricted_image.get_rect(
                    center=(center_x, center_y)
                )

                self.screen.blit(
                    restricted_image,
                    restricted_rect
                )


    def draw(self):
        self.screen.fill((30, 30, 30))
        self.draw_connections()
        for platform in self.platforms:
            platform.draw(
                self.screen,
                self.spacing_x,
                self.spacing_y,
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

                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_z:
                        self.camera.zoom_out()

                    if event.key == pygame.K_x:
                        self.camera.zoom_in()

            self.drone.update()
            self.camera.update()
            self.draw()
            self.check_collisions()
            self.clock.tick(60)

        pygame.quit()
