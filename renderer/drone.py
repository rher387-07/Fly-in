import pygame


class Drone:
    def __init__(self, spritesheet):
        self.spritesheet = spritesheet

        self.frame_width = 48
        self.frame_height = 48

        self.frames = []

        for i in range(4):
            frame = pygame.Surface(
                (self.frame_width, self.frame_height),
                pygame.SRCALPHA
            )

            frame.blit(
                self.spritesheet,
                (0, 0),
                pygame.Rect(
                    i * self.frame_width,
                    0,
                    self.frame_width,
                    self.frame_height
                )
            )

            self.frames.append(frame)

        self.current_frame = 0
        self.animation_speed = 100
        self.last_update = pygame.time.get_ticks()

        self.image = self.frames[0]
        self.rect = self.image.get_rect()

    def update(self):
        now = pygame.time.get_ticks()

        if now - self.last_update >= self.animation_speed:
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.current_frame = 0

            self.image = self.frames[self.current_frame]

            self.last_update = now

    def draw(
        self,
        screen,
        platform,
        camera
    ):
        x = platform.rect.centerx
        y = platform.rect.top

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
            midbottom=(x, y)
        )

        screen.blit(
            image,
            self.rect
        )
