import pygame

from renderer.platform import Platform


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

        self.platform_image = pygame.image.load(
            "asset/platform/1_Industrial_Tileset_1B.png"
        ).convert_alpha()

        self.platforms = []

        self.create_platforms()

    def create_platforms(self):
        for hub in self.network.hubs.values():
            platform = Platform(
                hub,
                self.platform_image
            )

            self.platforms.append(platform)

    def draw(self):
        self.screen.fill((30, 30, 30))

        for platform in self.platforms:
            platform.draw(
                self.screen,
                self.tile_size,
                self.offset_x,
                self.offset_y
            )

        pygame.display.flip()

    def run(self):
        while self.running:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            self.draw()

            self.clock.tick(60)

        pygame.quit()
