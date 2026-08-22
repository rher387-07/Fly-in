import pygame


class Camera:
    def __init__(self, width, height):
        self.x = 0
        self.y = 0

        self.width = width
        self.height = height

        self.speed = 10

        self.zoom = 1.0
        self.zoom_step = 0.1
        self.min_zoom = 0.1
        self.max_zoom = 2.0

    def update(self):
        keys = pygame.key.get_pressed()

        if keys[pygame.K_LEFT]:
            self.x -= self.speed

        if keys[pygame.K_RIGHT]:
            self.x += self.speed

        if keys[pygame.K_UP]:
            self.y -= self.speed

        if keys[pygame.K_DOWN]:
            self.y += self.speed

    def zoom_in(self):
        self.zoom = min(
            self.zoom + self.zoom_step,
            self.max_zoom
        )

    def zoom_out(self):
        self.zoom = max(
            self.zoom - self.zoom_step,
            self.min_zoom
        )

    def apply(self, x, y):
        return (
            (x - self.x) * self.zoom,
            (y - self.y) * self.zoom
        )
