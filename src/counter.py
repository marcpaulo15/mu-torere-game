
import pygame
import json
from typing import Tuple


class Counter:

    def __init__(self,
                 center: Tuple[float, float],
                 player: int,
                 is_available: bool,
                 config_path: str = "../config/config.json") -> None:

        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        self.player = player  # 1 or 2

        self.radius = config['counter_radius']
        self.border_radius = self.radius + config['counter_border_width']
        self.available_radius = (
                self.border_radius + config['counter_available_width']
        )

        self.colour = (
            config["player1_color"] if player == 1 else config['player2_color']
        )
        self.border_colour = config['counter_border_color']
        self.available_color = config['counter_available_color']

        topleft = (center[0] - self.radius, center[1] - self.radius)
        size = (2 * self.radius, 2 * self.radius)
        self.rect = pygame.Rect(topleft, size)

        self.is_available = is_available  # if True: it can be chosen by a player
        self.move_sound = pygame.mixer.Sound("../audio/basic_sound.wav")

    def move(self, new_pos: Tuple[float, float]) -> None:
        self.move_sound.play()
        self.rect.center = new_pos

    def draw(self, screen: pygame.Surface) -> None:
        if self.is_available:
            pygame.draw.circle(
                screen, self.available_color, self.center, self.available_radius)

        pygame.draw.circle(screen, self.border_colour, self.center, self.border_radius)
        pygame.draw.circle(screen, self.colour, self.center, self.radius)

    def __getattr__(self, name):
        # avoids having to call self.rect.<attr>, and do self.<attr> instead
        return getattr(self.rect, name)


if __name__ == "__main__":

    screen_width, screen_height = 800, 800
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))

    pygame.display.set_caption("~ Mu Torere Counter ~")
    clock = pygame.time.Clock()

    random_counter_list = [
        Counter(center=(400, 400), player=1, is_available=True),
        Counter(center=(100, 150), player=1, is_available=False),
        Counter(center=(600, 60),  player=2, is_available=True),
        Counter(center=(600, 700), player=2, is_available=False)
    ]

    done = False
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill([255, 255, 255])  # fill the screen with a black background
        # Display the cells on the screen
        for counter in random_counter_list:
            counter.draw(screen)
        pygame.display.update()  # update the screen content

        clock.tick(60)
    pygame.quit()
