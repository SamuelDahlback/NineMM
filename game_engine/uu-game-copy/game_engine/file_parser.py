from game_engine.difficulty import difficulty
from game_engine.utils.config import config
import json


class file_parser():

    VALID_GAME_BOARD = [
        ".-----.-----.",
        "|-    |    -|",
        "| .---.---. |",
        "| |-  |  -| |",
        "| | .-.-. | |",
        "| | |   | | |",
        ".-.-.   .-.-.",
        "| | |   | | |",
        "| | .-.-. | |",
        "| |-  |  -| |",
        "| .---.---. |",
        "|-    |    -|",
        ".-----.-----."
    ]

    def __init__(self, game_file_path):
        self._game_file_path = game_file_path
        self._game_json = self._get_game_json(game_file_path)

    def write_game_file(self, game, arg_difficulty):
        game_json = {}
        game_json['difficulty'] = arg_difficulty.name
        game_json['game_board'] = [''.join(row)
                                   for row in game.get_game_board()]
        game_json['turn'] = game.get_turn()
        game_json['player_to_move'] = game.get_current_player_to_move()

        game_json['player1 pieces left to place'] = game.get_number_pieces_left_to_place_for_player(
            'player1')
        game_json['player2 pieces left to place'] = game.get_number_pieces_left_to_place_for_player(
            'player2')

        if game.get_previous_player_to_move() == 'player1':
            game_json['player1_previous_action'] = game.get_last_action()
            game_json['player2_previous_action'] = self.get_last_action_for_player(
                'player2')
        else:
            game_json['player1_previous_action'] = self.get_last_action_for_player(
                'player1')
            game_json['player2_previous_action'] = game.get_last_action()

        try:
            with open(self._game_file_path, 'w') as f:
                # json requires one extra backslacke to escape it
                json.dump(game_json, f, ensure_ascii=False, indent=4)
        except FileNotFoundError:
            print(f'{self._game_file_path} file not found!')

    def get_game_board(self):
        """ validate & returns the game board in game.json"""
        game_board_text = self._get('game_board')
        if self._is_valid_game_board(game_board_text):
            return [list(row) for row in game_board_text]

        print("The game board is invalid. It should be similar to where ."
              "signifies available, player1 or player2 positions: ")
        print('\n'.join(self.VALID_GAME_BOARD))
        exit(1)

    def get_difficulty(self):
        my_difficulty = self._get('difficulty').upper()

        if (my_difficulty not in difficulty.__members__):
            print('difficulty setting in game.json should be one of these:')
            {print(diff) for diff in difficulty.__members__}
            exit()

        if my_difficulty == 'EASY':
            return difficulty.EASY
        elif my_difficulty == 'MEDIUM':
            return difficulty.MEDIUM
        elif my_difficulty == 'HARD':
            return difficulty.HARD

    def get_last_action_for_player(self, player):
        if (f"{player}_previous_action" not in self._game_json):
            return {}

        return self._get(f"{player}_previous_action")

    def get_player_to_move(self):
        player = self._get('player_to_move')

        if player != 'player1' and player != 'player2':
            print(
                'player_to_move setting in game.json should be either player1 or player2')
            exit()

        return player

    def get_turn(self):
        turn = self._get('turn')

        if (type(turn) is not int):
            print('turn setting in game.json should be an integer')
            exit()

        if (turn < 0):
            print('turn setting in game.json should be a more than 0')
            exit()

        return turn

    def _is_valid_game_board(self, input_game_board):
        available_sign = config().get('board_signs')['available']
        player1_sign = config().get('board_signs')['player1']
        player2_sign = config().get('board_signs')['player2']
        valid_signs = [available_sign, player1_sign, player2_sign]

        if len(input_game_board) != len(self.VALID_GAME_BOARD):
            return False

        for row_index, row in enumerate(input_game_board):
            if len(row) != len(self.VALID_GAME_BOARD[row_index]):
                return False

            for position_index, position in enumerate(row):
                valid_position = self.VALID_GAME_BOARD[row_index][position_index]
                # . files should be available or player positions
                if valid_position == '.':
                    if position not in valid_signs:
                        return False
                elif valid_position != position:
                    return False

        return True

    def _get_game_json(self, game_file_path):
        try:
            with open(game_file_path, 'r') as json_file:
                # json requires one extra backslacke to escape it
                json_object = json.loads(json_file.read())
        except FileNotFoundError:
            print(f'{game_file_path} file not found!')
            exit()

        # lower case keys
        game_json = {key.lower(): value
                     for (key, value) in json_object.items()}
        return game_json

    def _get(self, game_info):
        if (game_info not in self._game_json):
            print(f"{game_info} setting isn't found in game file")
            exit()
        return self._game_json[game_info]
