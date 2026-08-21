import pygame

# class Pygame:
#     def __init__(self):
#         self.py_init = pygame.init()
#         pygame.display.set_caption("Fly-In")
#         self.screen = pygame.display.set_mode((1920, 1080))
#         # pygame.
#         # self.background = pygame.image.load("asset/cloud/1.png")

#     # def apply_background(self):
#     #     self.background = pygame.transform.smoothscale(self.background, self.screen.get_size())
#     #     self.screen.blit(self.background, (0, 0))
#     #     pygame.display.flip()

#     def run(self):
#         running = True
#         while running:
#             # self.apply_background()
#             for event in pygame.event.get():
#                 if event.type == pygame.QUIT:
#                     running = False
#                     pygame.quit()
#                     print("Fenetre fermer")


# ap = Pygame()
# ap.run()

W_DISPLAY = 1900
H_DISPLAY = 990
class Lancer:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Fly-in")
        self.screen = pygame.display.set_mode((W_DISPLAY, H_DISPLAY))

    def run(self):
        running = True
        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    pygame.quit()
                    print("Fermeture de fenetre")

py = Lancer()
py.run()
