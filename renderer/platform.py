import pygame


class Platform(pygame.sprite.Sprite):
    def __init__(self, hub, image):
        super().__init__()

        self.hub = hub
        self.image = image

        self.x = hub.x
        self.y = hub.y

        self.rect = self.image.get_rect()

        self.font = pygame.font.Font(None, 28)

    def draw(
        self,
        screen,
        spacing_x,
        spacing_y,
        offset_x,
        offset_y,
        camera
    ):
        world_x = offset_x + self.x * spacing_x
        world_y = offset_y + self.y * spacing_y

        screen_x, screen_y = camera.apply(
            world_x,
            world_y
        )

        width = int(
            self.image.get_width() * camera.zoom
        )

        height = int(
            self.image.get_height() * camera.zoom
        )

        image = pygame.transform.scale(
            self.image,
            (width, height)
        )

        self.rect = image.get_rect(
            topleft=(screen_x, screen_y)
        )

        screen.blit(
            image,
            self.rect
        )

        text = self.font.render(
            self.hub.name,
            True,
            (255, 255, 255)
        )

        text = pygame.transform.scale(
            text,
            (
                int(text.get_width() * camera.zoom),
                int(text.get_height() * camera.zoom)
            )
        )

        text_rect = text.get_rect(
            midtop=(
                self.rect.centerx,
                self.rect.bottom + int(10 * camera.zoom)
            )
        )

        screen.blit(
            text,
            text_rect
        )
