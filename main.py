import sys
import pygame


class SpaceRace:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption('Космические гонки')
        self.screen = pygame.display.set_mode((720, 1280))
        self.bg_color = (30, 30, 30)


    def run_game(self):
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit()
            self.screen.fill(self.bg_color)
            pygame.display.flip()


if __name__ == '__main__':
    sr = SpaceRace()
    sr.run_game()
