import pygame
from .camera import Camera
from .platform import Platform

class Drone(pygame.sprite.Sprite):
    def __init__(self, sprite: pygame.Surface, path: list[Platform]) -> None:
        super().__init__()
        self.sprite = sprite

        self.frame_w = 48
        self.frame_h = 48
        self.frames = []

        for i in range(4):
            frame = pygame.Surface((self.frame_w, self.frame_h), pygame.SRCALPHA)
            frame.blit(self.sprite, (0, 0),
                       pygame.Rect(i * self.frame_w, 0, self.frame_w, self.frame_h))
            self.frames.append(frame)

        self.current_frame = 0
        self.anim_speed = 100
        self.last_update = pygame.time.get_ticks()

        self.image: pygame.Surface = self.frames[0]

        self.path = path
        self.path_index = 0

        start = self.path[0]
        ## ajout des zone a phathh
        self.rect = self.image.get_rect(center=start.rect.center)
        self.pos = pygame.Vector2(self.rect.center)

        self.move_speed = 120
        self.reached_end = False

    @property
    def target(self) -> Platform | None:
        if self.path_index < len(self.path):
            return self.path[self.path_index]
        return None

    def update(self, dt: float) -> None:
        now = pygame.time.get_ticks()
        if now - self.last_update >= self.anim_speed:
            self.current_frame = (self.current_frame + 1) % len(self.frames)
            self.image = self.frames[self.current_frame]
            self.last_update = now

        target = self.target
        if target is None:
            self.reached_end = True
            return

        target_pos = pygame.Vector2(target.rect.center)
        direction = target_pos - self.pos

        if direction.length() > 0:
            direction = direction.normalize()
            self.pos += direction * self.move_speed * dt

        self.rect.center = (round(self.pos.x), round(self.pos.y))

    def check_collision(self) -> Platform | None:
        """À appeler chaque frame pour détecter l'arrivée sur la platform cible."""
        target = self.target
        if target is None:
            return None

        if self.rect.colliderect(target.rect):
            self._on_platform_reached(target)
            return target
        return None

    def _on_platform_reached(self, platform: Platform) -> None:
        # signal / événement
        print(f"Drone arrivé sur {platform.hub.name}")
        self.path_index += 1

    def draw(self, screen: pygame.Surface, camera: Camera) -> None:
        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)
        image = pygame.transform.scale(self.image, (width, height))

        screen_x, screen_y = camera.apply(self.rect.x, self.rect.y)
        screen_rect = image.get_rect(topleft=(screen_x, screen_y))
        screen.blit(image, screen_rect)


"""
import pygame
from .platform import Platform
from .camera import Camera


class Drone:
    def __init__(self, sprite: pygame.Surface) -> None:
        self.sprite = sprite

        self.frame_w = 48
        self.frame_h = 48
        self.frames = []

        for i in range(4):
            frame = pygame.Surface(
                (self.frame_w, self.frame_h),
                pygame.SRCALPHA)

            frame.blit(
                self.sprite,
                (0, 0),
                pygame.Rect(i*self.frame_w, 0, self.frame_w, self.frame_h))
            self.frames.append(frame)

        self.current_frame = 0
        self.speed = 100
        self.last_update = pygame.time.get_ticks()

        self.image: pygame.Surface = self.frames[0]
        self.rect = self.image.get_rect()

    def update(self) -> None:
        now = pygame.time.get_ticks()

        if now - self.last_update >= self.speed:
            self.current_frame += 1

            if self.current_frame >= len(self.frames):
                self.current_frame = 0

            self.image = self.frames[self.current_frame]
            self.last_update = now

    def draw(
        self,
        screen: pygame.Surface,
        platform: Platform | None,
        camera: Camera
    ) -> None:
        if platform is not None:
            x = platform.rect.centerx
            y = platform.rect.top
        width = int(self.image.get_width() * camera.zoom)
        height = int(self.image.get_height() * camera.zoom)

        image = pygame.transform.scale(self.image, (width, height))
        self.rect = image.get_rect(midbottom=(x, y))
        screen.blit(image, self.rect)

"""
