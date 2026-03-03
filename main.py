# main.py - Einstiegspunkt, Game-Loop
import pygame
from settings import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, TITLE
from game import Game


def main():
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
    pygame.display.set_caption(TITLE)
    clock = pygame.time.Clock()

    game = Game()
    running = True

    while running:
        events = pygame.event.get()
        running = game.handle_events(events)
        game.update()
        game.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)

    pygame.quit()


if __name__ == '__main__':
    main()
