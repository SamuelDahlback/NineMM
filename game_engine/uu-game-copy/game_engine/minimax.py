from game_engine.game_state import game_state
from game_engine.difficulty import difficulty


class minimax():
    def __init__(self, arg_difficulty):
        self._point_system = {
            'two_adjacent_pieces': 40,
            'double_two_adjacent_pieces': 100,
            'middle_pieces': 20,
            'formed_rows': 200,
            'number_of_peices': 20,
        }

        self._difficulty = arg_difficulty
        if self._difficulty == difficulty.EASY:
            self._depth = 1
            self._point_system = {
                'middle_pieces': 20,
                'number_of_peices': 0,
                'formed_rows': 0,
            }
        elif self._difficulty == difficulty.MEDIUM:
            self._depth = 3
            self._point_system = {
                'middle_pieces': 10,
                'number_of_peices': 30,
                'formed_rows': 30,
            }
        elif self._difficulty == difficulty.HARD:
            self._depth = 5
            self._point_system = {
                'middle_pieces': 10,
                'number_of_peices': 30,
                'formed_rows': 30,
            }

    def get_action(self, game):
        self._player = game.get_current_player_to_move()
        self._enemy_player = game.get_previous_player_to_move()

        if self._difficulty == difficulty.HARD:
            if len(game.get_available_actions(self._player)) > 10:
                self._depth = 4
            else:
                self._depth = 5

        self._points, self._best_action = self._minimax(
            game, self._depth, True, float('-inf'), float('inf'), {})
        return self._best_action

    def _minimax(self, game, depth, is_player_maximizer, alpha, beta, best_action):
        if depth == 0 or game.is_finished():
            # we're at the end. time to evaluate the game we're in
            return self.evaluation(game, best_action, depth), best_action

        player = self._player if is_player_maximizer else self._enemy_player
        available_actions = game.get_available_actions(player)

        value = float('-inf') if is_player_maximizer else float('+inf')

        if len(available_actions) == 0:
            return value, best_action

        for action in available_actions:
            clone = game.get_clone()
            clone.make_action(action)
            evaluation = self._minimax(
                clone, depth - 1, not is_player_maximizer, alpha, beta, action)

            if is_player_maximizer:
                if evaluation[0] > value:
                    value = evaluation[0]
                    best_action = action
                alpha = max(alpha, evaluation[0])
            else:
                if evaluation[0] < value:
                    value = evaluation[0]
                    best_action = action
                beta = min(beta, evaluation[0])

            if beta <= alpha:
                break

        return value, best_action

    def evaluation(self, game, action, depth):

        my_game_state = game.get_game_state()

        if my_game_state == game_state.TIE:
            return 0
        elif my_game_state == game_state.PLAYER1_WON or\
                my_game_state == game_state.PLAYER2_WON:
            game_winner = game.get_winner()
            # used to get the least amount of turns to finish the game
            multiplier = depth if depth > 0 else 1
            if game_winner == self._player:
                return 99999999999 * multiplier
            else:
                return -99999999999 * multiplier

        points = 0

        # number of pieces in the middle square
        points += game.get_middle_pieces_for_player(
            self._player) * self._point_system['middle_pieces']
        points -= game.get_middle_pieces_for_player(
            self._enemy_player) * self._point_system['middle_pieces']

        # number of pieces in the board
        points += len(game.get_positions(self._player)) * \
            self._point_system['number_of_peices']
        points -= len(game.get_positions(self._enemy_player)) * \
            self._point_system['number_of_peices']

        points += len(game.get_formed_rows_for_player(self._player)) * \
            self._point_system['formed_rows']
        points -= len(game.get_formed_rows_for_player(self._enemy_player)) * \
            self._point_system['formed_rows']

        return points
