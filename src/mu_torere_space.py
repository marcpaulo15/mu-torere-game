import pygame
import json
from typing import Tuple


class MuTorereSpace:
    """
    MuTorereSpace class defines the logic behind a space in a Mu Torere board.
    There are 9 spaces in a simple board. Each player has 4 counters that
    are placed in different spaces, so at any step there is only one empty
    space. A counter (space filled by any of the players) is available when the
    active player is allowed to move it to the emtpy space.

    MuTorereSpace Attributes:
        - center:        (x,y) coordinates where the space is centered
        - state:         0 if it's empty, 1|2 if any player's counter is placed
        - is_available:  whether the counter can be chosen in current turn
        - rect:          allows to detect collisions with mouse clicks

    MuTorereSpace Methods:
        - update:               updates the value of 'state' attribute
        - update_availability:  updates the value of 'is_available' attribute
        - draw:                 displays the Space on the given surface
    """

    def __init__(self,
                 center: Tuple[int, int],
                 state: int = 0,
                 is_available: bool = False,
                 config_path: str = "../config/config.json") -> None:
        """
        Inits a MuTorereSpace instance centered at a given position 'center'.
        If 'state' is 1 or 2, it means that there is a piece placed on this
        spoce. If 'state' is 0, it means that it is empty. If 'is_available',
        the counter (filled space) can be chosen by active_player.

        :param center: (x,y) coordinates where the space is placed
        :param state: 0 if it's empty, 1|2 if any player's counter is placed
        :param is_available: whether the counter can be chosen in current turn
        :param config_path: path from where to read the configuration file
        :return: None
        :raise ValueError: if any input argument is invalid
        """

        # some sanity checks
        if state not in (0, 1, 2):
            raise ValueError("wrong state value for MuTorereSpace instance")

        self.center = center  # (x,y) coordinates
        self.state = state  # one of (0,1,2) meaning (empty, player1, player2)
        self.is_available = is_available  # whether it can be moved

        # Read the configuration file
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        # Define the radius of the Space when it represents a counter (circle)
        self._radius = config['counter_radius']
        self._border_radius = self._radius + config['counter_border_width']
        self._available_radius = (
                self._border_radius + config['counter_available_width']
        )

        # Define the colours (can be personalized through the config file)
        self._player1_colour = config["player1_color"]
        self._player2_colour = config["player2_color"]
        self._border_colour = config['counter_border_color']
        self._available_color = config['counter_available_color']

        # Define the 'rect' attribute to detect collisions with mouse clicks
        self.x, self.y = center
        topleft = (self.x - self._radius, self.y - self._radius)
        size = (2 * self._radius, 2 * self._radius)
        self.rect = pygame.Rect(topleft, size)

    def update(self, state: int) -> None:
        """
        Updates the value of 'state' attribute

        :param state: new value for 'state' attribute
        :return: NOne
        """

        if state in (0, 1, 2):
            self.state = state
        else:
            raise ValueError("wrong state value for MuTorereSpace instance")

    def update_availability(self, is_available: bool) -> None:
        """
        Updates the availability of the counter. Availability only matters when
        the space is not empty i.e. it represents a counter.

        :param is_available: new value for 'is_available' attribute
        :return: None
        """

        self.is_available = is_available

    def draw(self, screen: pygame.Surface) -> None:
        """
        Displays the counter on the given surface. If the Space is empty (state
        is zero) do nothing.

        :param screen: pygame surface where the space is displayed on
        :return: None
        """

        if self.state == 0:  # if the space is empty, do nothing
            return

        if self.is_available:
            # draw a larger circumference around the counter
            pygame.draw.circle(
                surface=screen, color=self._available_color,
                center=self.center, radius=self._available_radius
            )
        # draw a circumference (border) around the counter
        pygame.draw.circle(surface=screen, color=self._border_colour,
                           center=self.center, radius=self._border_radius)
        # draw the counter, fill it with player's (given by 'state') colour
        col = self._player1_colour if self.state == 1 else self._player2_colour
        pygame.draw.circle(surface=screen, color=col,
                           center=self.center, radius=self._radius)


if __name__ == "__main__":

    # 1) create a pygame Surface where the Slots (counters) will be placed
    screen_width, screen_height = 800, 800
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("~ MuTorereSpace class. Demo ~")
    clock = pygame.time.Clock()

    # 2) Initialize some random Spaces having different locations and states
    random_counter_list = [
        # Two counters for player1, one available and the other unavailable
        MuTorereSpace(center=(400, 400), state=1, is_available=True),
        MuTorereSpace(center=(100, 150), state=1, is_available=False),
        # Two counters for player2, one available and the other unavailable
        MuTorereSpace(center=(600, 60),  state=2, is_available=True),
        MuTorereSpace(center=(600, 700), state=2, is_available=False),
        # One extra empty counter. Since it's empty, it is not drawn
        MuTorereSpace(center=(200, 350), state=0, is_available=False)
    ]

    # 3) Set up the usual pygame flow
    done = False
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill([255, 255, 255])  # fill the screen with a white background
        # Display the Space (counters) on the screen
        for counter in random_counter_list:
            counter.draw(screen)
        pygame.display.update()  # update the screen content

        clock.tick(60)
    pygame.quit()
