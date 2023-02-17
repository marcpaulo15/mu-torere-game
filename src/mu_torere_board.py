import pygame
import json
from typing import Tuple, List
from mu_torere_space import MuTorereSpace


class MuTorereBoard:
    """
    MuTorereBoard implements the logic behind a Mu Torere Board.
        Allows and manages the movement of counters along the board. Displays
        the board (an eight-pointed star) and its counters (MuTorereSpaces).

    MuTorereBoard Attributes:
        central_space         - space that is placed at the center of the board
        empty_space           - at each step, space that is empty
        winner                - which player has won. 0 if the game is not done
        outer_spaces_list     - contains the outer spaces (eight-pointed star)
        all_spaces_list       - contains all the spaces, including the center

    MuTorereBoard Methods:
        move      - moves the given counter to the empty space.
        draw      - display the board's content on the given screen.
    """

    def __init__(self,
                 center: Tuple[int, int],
                 config_path: str = "../config/config.json") -> None:
        """
        Inits a MuTorereBoard instance centered at the given location 'center'.

        :param center: (x,y) coordinates where the board is centered
        :param config_path: path from where to read the configuration file
        :return: None
        """

        # Define the central space. Initially, this is the empty space as well.
        self.central_space = MuTorereSpace(center=center, state=0)
        self.empty_space = self.central_space
        self.winner = 0  # 0 if the game is not done, 1|2 if there is a winner

        # Read the configuration file
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        # Properties of the straight lines connecting Spaces
        self._edge_color = config['edge_color']
        self._edge_width = config['edge_width']

        # Compute the location of the slots (the coordinates of their centers)
        # (tl_x, tl_y) define the top-left corner of bounding box of the board
        tl_x = self.central_space.x - config['board_radius']
        tl_y = self.central_space.y - config['board_radius']
        self.tl = (tl_x, tl_y)
        length = config['board_radius'] * 2

        p = 0.3  # arbitrary value used to define separation between slots

        # Compute the centers of the outer Spaces, (an eight-pointed star)
        outer_centers_list = [
            (tl_x + int((1-p)*length), tl_y),
            (tl_x + length, tl_y + int(p*length)),
            (tl_x + length, tl_y + int((1-p)*length)),
            (tl_x + int((1-p)*length), tl_y + length),
            (tl_x + int(p*length), tl_y + length),
            (tl_x, tl_y + int((1-p)*length)),
            (tl_x, tl_y + p*length),
            (tl_x + int(length*p), tl_y)
        ]

        # Create a list with the outer spaces (eight-pointed star)
        self.outer_spaces_list = []
        for center, init_player in zip(outer_centers_list, [1]*4 + [2]*4):
            self.outer_spaces_list.append(
                MuTorereSpace(center=center, state=init_player)
            )
        # Create a list with all the spaces, including the central space
        self.all_spaces_list = self.outer_spaces_list.copy()
        self.all_spaces_list.append(self.central_space)
        # Prepares the board to let player_starting start the game
        self._update_availability(active_player=config['player_starting'])

    def _get_neighbours(self, space: MuTorereSpace) -> List[MuTorereSpace]:
        """
        Return the neighbours of the given Space. Two Spaces are neighbours if
        it is possible to go from one to the another in just one step.
        I.e. there is and edge connecting them.

        :param space: MuTorereSpace instance
        :return: list of its neighbours. list of MuTorereSpace instances
        """

        if space == self.central_space:
            return self.outer_spaces_list
        else:
            space_idx = self.outer_spaces_list.index(space)
            return [
                self.outer_spaces_list[space_idx-1],
                self.outer_spaces_list[(space_idx+1) % 8],
                self.central_space
            ]

    def _get_available_counters(self,
                                active_player: int) -> List[MuTorereSpace]:
        """
        Given an active_player, finds his/her available counters for the
        current turn, based on the state of the board and the empty_space.
        RULES: Players can move only to an adjacent outer space, and can move
        to the central space only when the moved counter is adjacent to an
        opponent's counter.

        :param active_player: which player is playing the current turn
        :return: list of available counters for the given active player
        """

        available_counters = []
        candidates_list = self._get_neighbours(space=self.empty_space)

        if self.empty_space == self.central_space:  # center is empty
            opponent_player = 1 if active_player == 2 else 2
            for space in candidates_list:  # all outer spaces are candidates
                if space.state != active_player:
                    continue
                # only interested in left and right neighbours, not the center.
                state_neighbours = self._get_neighbours(space=space)
                for neighbour in state_neighbours:
                    if neighbour.state == opponent_player:
                        available_counters.append(space)
                        break
        else:  # empty space is not the center
            neighbours = self._get_neighbours(space=self.empty_space)
            available_counters = []
            for space in neighbours:
                if space.state == active_player:
                    available_counters.append(space)

        return available_counters

    def _update_availability(self, active_player: int) -> List[MuTorereSpace]:
        """
        Updates the availability of the active_player's counters. First, make
        everything unavailable. Then, make available only those counters that
        active_player is allowed to move.

        :param active_player: which player is playing the current turn
        :return: list of available counters after updating availability
        """

        # Make everything unavailable
        for space in self.all_spaces_list:
            space.update_availability(is_available=False)
        # Get the available counters based on empty_slot and active_player
        new_available_counters = self._get_available_counters(active_player)
        # Make these counters (Spaces) available for active_player
        for counter in new_available_counters:
            counter.update_availability(is_available=True)
        return new_available_counters

    def move(self, counter: MuTorereSpace) -> None:
        """
        Plays one turn of the game. Moves the given counter to the empty space.

        :param counter: MuTorereSpace that is a counter (not the empty_space)
        :return: None
        """

        if not (counter.state in (1, 2) and counter.is_available):
            raise ValueError("Invalid move in MuTorereBoard")

        current_active_player = counter.state
        new_active_player = 1 if counter.state == 2 else 2
        # Fill the empty_space (move the counter to its new Space)
        self.empty_space.update(state=counter.state)
        # Empty the old space (the Space where the counter was placed)
        self.empty_space = counter
        self.empty_space.update(state=0)
        # Make available those counters that can be player in the next turn
        new_available_counters = self._update_availability(
            active_player=new_active_player
        )
        # check if the next player has available moves to play. If no legal
        # moves are available, current_active_player is the winner of the game.
        if len(new_available_counters) == 0:
            self.winner = current_active_player

    def _draw_edge(self,
                   screen: pygame.Surface,
                   point1: Tuple[int, int],
                   point2: Tuple[int, int]) -> None:
        """
        Draw a straight line from pointA to pointB. Color and width are
        provided in the config file

        :param screen: pygame surface where the line is drawn
        :param point1: (x,y) coordinates of pointA
        :param point2: (x,y) coordinates of pointB
        :return: None
        """

        pygame.draw.line(surface=screen,
                         color=self._edge_color,
                         start_pos=point1,
                         end_pos=point2,
                         width=self._edge_width)

    def draw(self, screen: pygame.Surface) -> None:
        """
        Display the board's content on the given screen. Draws the nine spaces
        and the lines connecting them.

        :param screen: pygame surface where the board is displayed
        :return: None
        """

        board_center = self.central_space.center
        # From each space, there is a connection (line) to its adjacent spaces
        # and to the central space as well
        for i in range(len(self.outer_spaces_list)):
            point1 = self.outer_spaces_list[i].center
            point2 = self.outer_spaces_list[i-1].center
            self._draw_edge(screen=screen, point1=point1, point2=point2)
            self._draw_edge(screen=screen, point1=point1, point2=board_center)
        # Display the spaces in the board
        for space in self.all_spaces_list:
            space.draw(screen)


if __name__ == "__main__":

    # 1) create a pygame Surface where the Slots (counters) will be placed
    screen_width, screen_height = 800, 800
    pygame.init()
    screen = pygame.display.set_mode((screen_width, screen_height))
    pygame.display.set_caption("~ MuTorereBoard class. Demo ~")
    clock = pygame.time.Clock()

    # 2) Initialize a Mu Torere board and play the first turn
    board = MuTorereBoard(center=(screen_width//2, screen_height//2))
    board.move(board.outer_spaces_list[0])

    # 3) Set up the usual pygame flow
    done = False
    while not done:

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                done = True

        screen.fill([255, 255, 255])  # fill the screen with a withe background
        # Display the cells on the screen
        board.draw(screen)
        pygame.display.update()  # update the screen content

        clock.tick(60)
    pygame.quit()
