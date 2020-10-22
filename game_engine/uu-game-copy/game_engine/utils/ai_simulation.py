from game_engine.utils.config import config
from game_engine.file_parser import file_parser
from game_engine.minimax import minimax
from game_engine.game import game
from game_engine.difficulty import difficulty
import time


def get_difficulty(diff):

    diff = diff.upper()
    if diff == 'EASY':
        return difficulty.EASY
    elif diff == 'MEDIUM':
        return difficulty.MEDIUM
    elif diff == 'HARD':
        return difficulty.HARD


def run_simulation():

    my_file_parser = file_parser(config().get('game_file_path'))
    simulation_config = config().get('simulation')

    if 'ai_diffculty_1' not in simulation_config or\
            'ai_diffculty_2' not in simulation_config:
        print("ai_difficulty_1 & ai_diffculty_2 should be specified"
              "in config.json simulation object, example:")
        exit()

    if simulation_config['ai_diffculty_1'].upper() not in difficulty.__members__ or\
            simulation_config['ai_diffculty_2'].upper() not in difficulty.__members__:
        print("simulation difficulties should be one of the following:")
        {print(diff) for diff in difficulty.__members__}
        exit()

    first_ai_difficulty = get_difficulty(simulation_config['ai_diffculty_1'])
    second_ai_difficulty = get_difficulty(simulation_config['ai_diffculty_2'])
    turns = 10

    if 'turns' in simulation_config and simulation_config['turns'].isdigit():
        turns = int(simulation_config['turns'])
    else:
        print("turns smiluation config is (not provided or invalid), the"
              f" simulatioon will run for {turns} turns")

    first_minimax = minimax(first_ai_difficulty)
    second_minimax = minimax(second_ai_difficulty)

    for x in range(turns):
        my_file_parser = file_parser(config().get('simulation_game_file_path'))
        my_game = game(
            turn=my_file_parser.get_turn(),
            game_board=my_file_parser.get_game_board(),
            curr_player=my_file_parser.get_player_to_move(),
            last_action=my_file_parser.get_last_action_for_player(
                my_file_parser.get_player_to_move()),
        )
        if (my_game.is_finished()):
            print(f"game is finished: the winner is {my_game.get_winner()}")
            break

        if x % 2 == 0:
            curr_minimax = first_minimax
            curr_diff = first_ai_difficulty
        else:
            curr_minimax = second_minimax
            curr_diff = second_ai_difficulty

        start_time = time.time()

        action = curr_minimax.get_action(my_game)
        my_game.make_action(action)

        print('difficulty:', curr_diff.name)
        print('player: ', config().get('board_signs')
              [my_game.get_previous_player_to_move()])

        print('turn', my_game.get_turn())
        print('points: ', curr_minimax._points)
        print("take taken: %f.2 sec" % (time.time() - start_time))
        print('action: ', action)
        print(my_game, "\n")
        my_file_parser.write_game_file(my_game, curr_diff)
