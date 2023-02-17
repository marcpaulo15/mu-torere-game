import pygame
import json
from mu_torere_board import MuTorereBoard


class GameHandler:
    """
    Game Handler implements the logic of a Mu Torere Game.
        Process each turn and updates the state of the game. It updates the GUI
        (screen) according to the game state. Calling the 'run' method will run
        the game.

    GameHandler Attributes:
        board            - game board, a MuTorereBoard instance
        mouse_pos        - (x,y) mouse coordinates (if there's a mouse click)
        active_player    - which player takes turn. one of [1 2]

    GameHandler Methods:
        process_events   - process the events of the game (mouse clicks)
        run_logic        - runs the logic of the game based on user's actions
        draw             - displays the game's elements on the given surface
        run              - runs the main loop to play the game
    """

    def __init__(self,
                 config_path: str = "../config/config.json") -> None:
        """
        Inits a GameHandler instance to play the MuTorere Game

        :param config_path: path from where to read the configuration file
        """

        # Read the config file
        with open(config_path, 'r') as config_file:
            config = json.load(config_file)

        # Initialize pygame and create the screen (surface)
        pygame.init()
        self.screen = pygame.display.set_mode(
            (config['screen_width'], config['screen_height'])
        )
        pygame.display.set_caption(config['title'])

        # Create the Mu Torere Board
        self.board = MuTorereBoard(center=config['board_center_coords'])
        self._center = config['board_center_coords']

        # Define colors, sounds, and other basic attributes for the game
        self.mouse_pos = None
        self._is_sound_on = config['is_sound_on']
        self._screen_bg_color = config['screen_bg_color']
        self._player_starting = config['player_starting']
        self.active_player = self._player_starting
        self._basic_sound = pygame.mixer.Sound(config['basic_sound_path'])
        self._win_sound = pygame.mixer.Sound(config['win_sound_path'])

        # Define the text to display the information about the game state
        font = pygame.font.SysFont(name=config['text_font'],
                                   size=config['text_font_size'])
        turn_text, winner_text = config['turn_text'], config['winner_text']
        color1, color2 = config['player1_color'], config['player2_color']
        self._your_turn1_text = font.render(turn_text, True, color1)
        self._your_turn2_text = font.render(turn_text, True, color2)
        self._winner1_text = font.render(winner_text, True, color1)
        self._winner2_text = font.render(winner_text, True, color2)

        m = 10  # margin to separate the text from the screen boundaries
        self._game_info_tl = (  # tl means top-left corner
            self.board.tl[0],
            2*m
        )

        # Define the 'new_game' button in the top-right corner of the screen
        self._new_game_button = font.render(
            'new game', True, config['new_game_button_text_color'],
            config['new_game_button_color']
        )
        self._new_game_button_rect = self._new_game_button.get_rect(
            x=config['screen_width'] - self._new_game_button.get_width() - m,
            y=m
        )

    def _process_turn(self) -> None:
        """
        Check if the mouse_pos collides with any available counter. If that is
        the case, update the board and the game params accordingly to move on
        to the next turn. If 'is_sound_on', play the proper sound. If the
        mouse_pos clicks on an unavailable counter or outside the board, do
        nothing (wait for the next mouse click)

        :return: None
        """

        selected_counter = self.board.process_mouse_click(
            mouse_pos=self.mouse_pos, active_player=self.active_player
        )

        if selected_counter is not None and not self.board.winner:
            self.board.move(counter=selected_counter)
            self.active_player = 1 if self.active_player == 2 else 2
            if self._is_sound_on and self.board.winner:
                self._win_sound.play()
            elif self._is_sound_on:
                self._basic_sound.play()

    def _reset_game(self) -> None:
        """
        Creates a new board and sets the game parameters to their values
        by default when initialized. Called when new_game button is clicked

        :return: None
        """

        self.board = MuTorereBoard(center=self._center)
        self.active_player = self._player_starting

    def _display_game_information(self, screen: pygame.Surface) -> None:
        """
        Displays information about the state of the game. If the game is
        running, tells which player takes turn. If there is a winner, announce
        the winner. The text colour tells which player takes turn or is winner.

        :param screen: pygame surface where the text is displayed
        :return: None
        """

        if self.board.winner == 1:  # player1 wins the game
            text = self._winner1_text
        elif self.board.winner == 2:  # player2 wins the game
            text = self._winner2_text
        elif self.active_player == 1:  # ongoing game, player1 takes turn
            text = self._your_turn1_text
        else:  # ongoing game, player2 takes turn
            text = self._your_turn2_text
        screen.blit(text, self._game_info_tl)

    def process_events(self) -> bool:
        """
        Deals with the user's input (right mouse click).
        Possible actions: quit the game, mouse click on an available Space

        :return: whether to quit the game
        """

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                return True
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    return True
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                # store the position of the mouse click. It will be used in the
                # run_logic method
                self.mouse_pos = pygame.mouse.get_pos()
        return False

    def run_logic(self) -> None:
        """
        Translates the mouse clicks from the users into the proper game change
        Possible actions: click on an available counter, or click the new_game
        button. If the mouse has not been clicked, do nothing.

        :return: None
        """

        if self.mouse_pos is None:
            return
        if self._new_game_button_rect.collidepoint(self.mouse_pos):
            self._reset_game()  # restart the game (board)
        else:  # check if the mouse click is to select an available counter
            self._process_turn()
        # return to mouse_pos default value, wait for the next mouse click
        self.mouse_pos = None

    def draw(self, screen: pygame.Surface) -> None:
        """
        Displays the game's elements on the given surface.

        :param screen: pygame Surface where the game is displayed
        :return: None
        """

        screen.fill(self._screen_bg_color)
        self.board.draw(screen=screen)
        self._display_game_information(screen=screen)
        screen.blit(self._new_game_button, self._new_game_button_rect)
        pygame.display.update()

    def run(self) -> None:
        """
        Runs the main loop to play the game

        :return: None
        """

        clock = pygame.time.Clock()
        done = False
        while not done:
            done = self.process_events()
            self.run_logic()
            self.draw(screen=self.screen)
            clock.tick(60)
        pygame.quit()


if __name__ == "__main__":
    game = GameHandler()
    game.run()
