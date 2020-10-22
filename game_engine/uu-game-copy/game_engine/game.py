from copy import deepcopy
from math import floor, ceil
from game_engine.utils.config import config
from game_engine.game_state import game_state


class game():

    def __init__(self, turn, game_board, curr_player, last_action={}):
        self._turn = turn
        self._game_board = game_board
        self._curr_player = curr_player
        self._last_action = last_action

    def get_available_actions(self, player):
        """returns the available actions
        eg:
        [ {
        'from': [0, 0],
        'to': [0, 5],
        'remove': [0, 10]
          } ]
        """
        if player == 'player1':
            enemy_player = 'player2'
        elif player == 'player2':
            enemy_player = 'player1'

        available_moves = []
        result = []

        if self._turn < 24:
            available_moves_parsed = [{'to': x}
                                      for x in self.get_positions('available')]
        else:
            available_moves = self.get_available_moves(player)
            available_moves_parsed = []
            for move in available_moves:
                for to_move in move['to']:
                    parsed_move = {
                        'from': move['from'],
                        'to': to_move,
                    }
                    if self._is_valid_action_no_prev_row_formed(parsed_move):
                        available_moves_parsed.append(parsed_move)

        for action in available_moves_parsed:
            if self.get_formed_rows_from_action(action) > 0:
                action['remove'] = self._get_removable_positions(enemy_player)

        for move in available_moves_parsed:
            if 'remove' not in move:
                result.append(move)
                continue
            for remove_move in move['remove']:
                if 'from' not in move:
                    result.append(
                        {'to': move['to'], 'remove': remove_move})
                else:
                    result.append(
                        {'from': move['from'], 'to': move['to'], 'remove': remove_move})
        return result

    def get_middle_pieces_for_player(self, player):
        """
        get number of pieces for a player in the middle square
        """
        player_sign = config().get('board_signs')[player]

        relevant_positions = []
        relevant_positions.extend(list(self._game_board[2]))
        relevant_positions.extend(list(self._game_board[10]))
        relevant_positions.extend(
            [self._game_board[6][2], self._game_board[6][10]])

        return len([position for position in relevant_positions
                    if position == player_sign])

    def get_two_adjacent_pieces_for_player(self, player):
        """
        returns how many times the player has two pieces next to each other with an open
        space at the end, hence a possibility to take a piece from the opponent.
        """
        player_sign = config().get('board_signs')[player]
        available_sign = config().get('board_signs')['available']
        connector_signs = config().get('board_signs')['connectors']
        # traverse horizontally
        adjacent_rows = 0

        # get horizontal adjacent pieces
        for y_index, y in enumerate(self._game_board):
            player_pieces = 0
            available_position = 0
            for x_index, x in enumerate(y):
                if x == player_sign:
                    player_pieces += 1
                elif x == available_sign:
                    available_position += 1
                elif x not in connector_signs:
                    player_pieces = 0

                if player_pieces == 2 and available_position == 1:
                    adjacent_rows += 1

        # get vertical adjacent pieces
        for x in range(len(self._game_board[0])):
            player_pieces = 0
            available_position = 0
            for y in range(len(self._game_board)):
                curr_sign = self._game_board[y][x]
                if curr_sign == player_sign:
                    player_pieces += 1
                elif curr_sign == available_sign:
                    available_position += 1
                elif curr_sign not in connector_signs:
                    player_pieces = 0

                if player_pieces == 2 and available_position == 1:
                    adjacent_rows += 1

        # get diagonally right bot
        for x in range(len(self._game_board[0])):
            player_pieces = 0
            available_position = 0
            curr_sign = self._game_board[x][x]
            if curr_sign == player_sign:
                player_pieces += 1
            elif curr_sign == available_sign:
                available_position += 1
            elif curr_sign not in connector_signs:
                player_pieces = 0

            if player_pieces == 2 and available_position == 1:
                adjacent_rows += 1

        # get diagonally left top
        for x in range(len(self._game_board[0])):
            player_pieces = 0
            available_position = 0
            curr_sign = self._game_board[12 - x][x]
            if curr_sign == player_sign:
                player_pieces += 1
            elif curr_sign == available_sign:
                available_position += 1
            elif curr_sign not in connector_signs:
                player_pieces = 0

            if player_pieces == 2 and available_position == 1:
                adjacent_rows += 1

        return adjacent_rows

    def get_formed_rows_from_action(self, action):
        """
        traverse board horizontally & vertically to get the number
        of newly formed rows from an action
        """
        y_index = action['to'][0]
        x_index = action['to'][1]
        clone = self.get_clone()
        clone.make_action(action)
        clone_baord = clone.get_game_board()
        player_sign = clone_baord[y_index][x_index]
        connector_signs = config().get('board_signs')['connectors']
        formed_rows = 0

        # vertical row
        peices = 1
        curr_y_index = y_index - 1
        while (curr_y_index >= 0):
            curr_sign = clone_baord[curr_y_index][x_index]

            if curr_sign == player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index -= 1
            else:
                break

        curr_y_index = y_index + 1
        while (curr_y_index < len(clone_baord)):
            curr_sign = clone_baord[curr_y_index][x_index]

            if curr_sign == player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index += 1
            else:
                break

        if peices == 3:
            formed_rows += 1

        peices = 1
        # horizontal row
        curr_x_index = x_index - 1
        while (curr_x_index >= 0):

            curr_sign = clone_baord[y_index][curr_x_index]

            if curr_sign == player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_x_index -= 1
            else:
                break

        curr_x_index = x_index + 1
        while (curr_x_index < len(clone_baord[0])):

            curr_sign = clone_baord[y_index][curr_x_index]

            if curr_sign == player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_x_index += 1
            else:
                break

        if peices == 3:
            formed_rows += 1

        peices = 1
        # get diagonally top left
        curr_y_index = y_index - 1
        curr_x_index = x_index - 1
        while (curr_x_index >= 0 and curr_y_index >= 0):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index -= 1
                curr_x_index -= 1
            else:
                break

        # get diagonal bot right
        curr_y_index = y_index + 1
        curr_x_index = x_index + 1
        while (curr_x_index < len(self._game_board[0]) and curr_y_index < len(self._game_board)):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in player_sign:
                peices += 1
            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index += 1
                curr_x_index += 1
            else:
                break

        if peices == 3:
            formed_rows += 1

        peices = 1

        # get diagonal top right
        curr_y_index = y_index - 1
        curr_x_index = x_index + 1
        while (curr_x_index < len(self._game_board[0]) and curr_y_index >= 0):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in player_sign:
                peices += 1

            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index -= 1
                curr_x_index += 1
            else:
                break

        # get diagonal bot left
        curr_y_index = y_index + 1
        curr_x_index = x_index - 1
        while (curr_x_index >= 0 and curr_y_index < len(self._game_board)):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in player_sign:
                peices += 1
            if curr_sign in connector_signs or curr_sign == player_sign:
                curr_y_index += 1
                curr_x_index -= 1
            else:
                break

        if peices == 3:
            formed_rows += 1

        return formed_rows

    def get_formed_rows_for_player(self, player):
        """
        traverse board horizontally & vertically to get the number
        of formed rows"""
        player_sign = config().get('board_signs')[player]
        connector_signs = config().get('board_signs')['connectors']

        # traverse horizontally
        positions_forming_rows = []

        for y_index, y in enumerate(self._game_board):
            player_pieces = []
            for x_index, x in enumerate(y):
                if x == player_sign:
                    player_pieces.append([y_index, x_index])
                elif x not in connector_signs:
                    player_pieces = []

                if len(player_pieces) == 3:
                    positions_forming_rows.extend(player_pieces)

        # traverse vertically
        for x_index in range(len(self._game_board[0])):
            player_pieces = []
            for y_index in range(len(self._game_board)):
                curr_sign = self._game_board[y_index][x_index]
                if curr_sign == player_sign:
                    player_pieces.append([y_index, x_index])
                elif curr_sign not in connector_signs:
                    player_pieces = []

                if len(player_pieces) == 3:
                    positions_forming_rows.extend(player_pieces)

        # traverse diagonally from top left to bot right
        player_pieces = []
        for x_index in range(len(self._game_board[0])):
            curr_sign = self._game_board[x_index][x_index]
            if curr_sign == player_sign:
                player_pieces.append([x_index, x_index])
            elif curr_sign not in connector_signs:
                player_pieces = []

            if len(player_pieces) == 3:
                positions_forming_rows.extend(player_pieces)

        # traverse diagonally from bot left to top right
        player_pieces = []
        for y_index in range(len(self._game_board[0])):
            curr_sign = self._game_board[12 - y_index][y_index]
            if curr_sign == player_sign:
                player_pieces.append([12 - y_index, y_index])
            elif curr_sign not in connector_signs:
                player_pieces = []

            if len(player_pieces) == 3:
                positions_forming_rows.extend(player_pieces)

        return positions_forming_rows

    def get_current_player_to_move(self):
        return self._curr_player

    def get_previous_player_to_move(self):
        if self._curr_player == 'player1':
            return 'player2'
        elif self._curr_player == 'player2':
            return 'player1'

    def is_finished(self):
        curr_game_state = self.get_game_state()
        return curr_game_state == game_state.TIE or\
            curr_game_state == game_state.PLAYER1_WON or\
            curr_game_state == game_state.PLAYER2_WON

    def get_winner(self):
        my_game_state = self.get_game_state()
        if my_game_state == game_state.PLAYER1_WON:
            return 'player1'
        elif my_game_state == game_state.PLAYER2_WON:
            return 'player2'

        return None

    def get_game_state(self):
        """ game is finished when it's more than 24 turns and either players
        have less than 3 pieces"""
        if self._turn < 24:
            return game_state.NOT_FINISHED

        if len(self.get_positions('player1')) < 3 or\
                len(self.get_available_moves('player1')) == 0:
            return game_state.PLAYER2_WON
        if len(self.get_positions('player2')) < 3 or\
                len(self.get_available_moves('player2')) == 0:
            return game_state.PLAYER1_WON
        if self._turn == 200:
            return game_state.TIE

        return game_state.NOT_FINISHED

    def get_positions(self, sign_key):
        """
        finds the positions of a sign in the board
        Parameters
        ----------
        sign : str (eg: player1, available)
        Returns
        -------
        list
        a list containing the positions of the sign
        positions that it can move to
        eg:
        input:  player = player1
        result:
        [[0, 0], [0, 5], [10, 5]]
        """
        sign = config().get('board_signs')[sign_key]
        positions = []

        for y_index, y in enumerate(self._game_board):
            for x_index, x in enumerate(y):
                if x == sign:
                    positions.append([y_index, x_index])

        return positions

    def get_available_moves(self, player):
        """
        used in phase 2 & 3 and checkes what available move for each piece for a
        specific player
        Parameters
        ----------
        player : str
        eg:
        player1 or player2
        Returns
        -------
        list
        a list containing dictionaries of each piece position and the available
        positions that it can move to
        eg:
        input:  player = player1
        result:
        [
        {'from': [0, 0],
          'to': [[0, 5], [5, 0], [2, 2]]}
          ]
        """
        available_moves = []
        player_sign = config().get('board_signs')[player]

        player_positions = self.get_positions(player)
        if len(player_positions) == 3:
            available_positions = self.get_positions('available')
            for position in player_positions:
                available_move = {
                    'from': position,
                    'to': available_positions
                }
                available_moves.append(available_move)
            return available_moves

        for y_index, y in enumerate(self._game_board):
            for x_index, x in enumerate(y):
                if x == player_sign:
                    available_neighbours = self.get_available_neighbours(
                        y_index, x_index)
                    if len(available_neighbours) == 0:
                        continue

                    available_move = {
                        'from': [y_index, x_index],
                        'to': available_neighbours
                    }
                    available_moves.append(available_move)

        return available_moves

    def get_available_neighbours(self, y_index, x_index):
        """
        keep moving if you got a connector until
        you reach an available position, a non-available position, or a dead end
        Parameters
        ----------
        y_index : int
        x_index : int
        Returns
        -------
        list
        a list representing the 2d-index of available neighbours
        eg:
        input:  y_index = 0, x_index = 0
        result: [[0, 5], [5, 0], [2, 2]] if these positions are available
        """
        available_neighbours = []
        connector_signs = config().get('board_signs')['connectors']
        available_sign = config().get('board_signs')['available']

        curr_y_index = y_index - 1
        # get vertically top
        while (curr_y_index >= 0):
            curr_sign = self._game_board[curr_y_index][x_index]

            if curr_sign in connector_signs:
                curr_y_index -= 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append([curr_y_index, x_index])
            break

        curr_y_index = y_index + 1
        # get vertically bot
        while (curr_y_index < len(self._game_board)):
            curr_sign = self._game_board[curr_y_index][x_index]

            if curr_sign in connector_signs:
                curr_y_index += 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append([curr_y_index, x_index])

            break

        curr_x_index = x_index - 1
        # get horizontally left
        while (curr_x_index >= 0):

            curr_sign = self._game_board[y_index][curr_x_index]
            if curr_sign in connector_signs:
                curr_x_index -= 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append([y_index, curr_x_index])

            break

        curr_x_index = x_index + 1
        # get horizontally right
        while (curr_x_index < len(self._game_board[0])):

            curr_sign = self._game_board[y_index][curr_x_index]
            if curr_sign in connector_signs:
                curr_x_index += 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append([y_index, curr_x_index])

            break

        curr_y_index = y_index - 1
        curr_x_index = x_index - 1
        # get diagonally top left
        while (curr_x_index >= 0 and curr_y_index >= 0):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in connector_signs:
                curr_y_index -= 1
                curr_x_index -= 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append(
                    [curr_y_index, curr_x_index])

            break

        curr_y_index = y_index - 1
        curr_x_index = x_index + 1
        # get diagonal top right
        while (curr_x_index < len(self._game_board[0]) and curr_y_index >= 0):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in connector_signs:
                curr_y_index -= 1
                curr_x_index += 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append(
                    [curr_y_index, curr_x_index])
            break

        curr_y_index = y_index + 1
        curr_x_index = x_index + 1
        # get diagonal bot right
        while (curr_x_index < len(self._game_board[0]) and curr_y_index < len(self._game_board)):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in connector_signs:
                curr_y_index += 1
                curr_x_index += 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append(
                    [curr_y_index, curr_x_index])

            break

        curr_y_index = y_index + 1
        curr_x_index = x_index - 1
        # get diagonal bot left
        while (curr_x_index >= 0 and curr_y_index < len(self._game_board)):
            curr_sign = self._game_board[curr_y_index][curr_x_index]

            if curr_sign in connector_signs:
                curr_y_index += 1
                curr_x_index -= 1
                continue
            elif curr_sign == available_sign:
                available_neighbours.append(
                    [curr_y_index, curr_x_index])

            break

        return available_neighbours

    def make_action(self, action):
        player_sign = config().get('board_signs')[
            self.get_current_player_to_move()]
        available_sign = config().get('board_signs')["available"]

        # phase 1
        if 'to' in action:
            self._game_board[action['to'][0]][action['to'][1]] = player_sign
        if 'from' in action:
            self._game_board[action['from'][0]
                             ][action['from'][1]] = available_sign
        if 'remove' in action:
            self._game_board[action['remove'][0]
                             ][action['remove'][1]] = available_sign

        if self._curr_player == 'player1':
            self._curr_player = 'player2'
        elif self._curr_player == 'player2':
            self._curr_player = 'player1'

        self._last_action = action
        self._turn += 1

    def get_number_pieces_left_to_place_for_player(self, player):
        """ returns number of pieces to place for player in phase 1"""
        # phase 2
        if self._turn > 24:
            return 0

        # phase 1
        pieces_to_place = 24 - self._turn
        if player == self._curr_player:
            return ceil(pieces_to_place / 2)
        else:
            return floor(pieces_to_place / 2)

    def get_clone(self):
        return deepcopy(self)

    def get_game_board(self):
        return self._game_board

    def get_turn(self):
        return self._turn

    def get_last_action(self):
        return self._last_action

    def _get_removable_positions(self, player):

        row_formed_positions = self.get_formed_rows_for_player(player)
        all_positions = self.get_positions(player)
        if len(row_formed_positions) == 0 or \
                len(row_formed_positions) == len(all_positions):
            return all_positions
        return list(filter(lambda pos: pos not in row_formed_positions,
                           all_positions))

    def _is_valid_action_no_prev_row_formed(self, action):
        if 'from' not in self._last_action or 'to' not in self._last_action or\
                'remove' not in self._last_action:
            return True

        return not (action['to'] == self._last_action['from'] and
                    action['from'] == self._last_action['to'])

    def __eq__(self, other):
        return self._turn == other.get_turn() and \
            self._game_board == other.get_game_board()

    def __str__(self):
        result = ''
        for index, row in enumerate(self._game_board):
            result += ' '.join(map(str, row))
            if index < (len(row) - 1):
                result += '\n'

        return result
