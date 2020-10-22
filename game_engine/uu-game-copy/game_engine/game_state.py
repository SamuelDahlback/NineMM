from enum import Enum


class game_state(Enum):
    PLAYER1_WON = 1
    PLAYER2_WON = 2
    TIE = 3
    NOT_FINISHED = 4
