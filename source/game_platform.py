# Imports---------------------------------------------------------------------------------------------------------------
import time
import os
import sys


# Classes---------------------------------------------------------------------------------------------------------------
class Singleton(type):
    """
    Define an Instance operation that lets clients access its unique
    instance.
    """

    def __init__(cls, name, bases, attrs, **kwargs):
        super().__init__(name, bases, attrs)
        cls._instance = None

    def __call__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__call__(*args, **kwargs)
        return cls._instance

class Player:
    pieces_placed = 0
    def __init__(self, name, figure, pieces, nextTurn):
        self.name = name  # Black/White
        self.figure = figure  # X/O
        self.pieces = pieces  # Piece list
        self.nextTurn = nextTurn  # True/False

    def __eq__(self, other):
        return self.name == other.name

    def pieces_left(self):
        return len(self.pieces)


class Piece:
    def __init__(self, pos, color):
        self.pos = pos  # Coord (0-23)
        self.color = color  # Black/White

    def __eq__(self, other):
        return self.pos == other.pos


class Coord:
    def __init__(self, pos, empty, figure):
        self.pos = pos  # Coord
        self.empty = empty  # Bool
        self.figure = figure  # What we display on the board

class Board(metaclass=Singleton):

    #The following variables should be moved so that you can start both local and online games
    node_list = []
    MENU_SHORTCUT = "M"
    players = [Player("Player 1", "X", [], False), Player("Player 2", "O", [], False)]
    #pieces_placed = 0
    we_have_a_winner = False

    def __init__(self, max_number_of_pieces_per_player, number_of_nodes):
        self.max_number_of_pieces = max_number_of_pieces_per_player
        self.number_of_nodes = number_of_nodes

        while len(self.node_list) > 0:
            self.node_list.pop()
        for i in range(0, self.number_of_nodes):
            self.node_list.append(Coord(i, True, " "))


    def print_board(self):
        clear()
        print(str(self.node_list[0].figure))
        print("\t\t\t\t   To go back to the main menu press M")
        self.print_scoreboard()
        print()
        print("\t\t\t 1       2         3          4           5         6      7")
        print()
        print("A\t\t\t[" + self.node_list[0].figure + "]--------------------------[" + self.node_list[
            1].figure + "]--------------------------[" + self.node_list[2].figure + "]")
        print(" \t\t\t |                            |                            |")
        print(" \t\t\t |                            |                            |")
        print(" \t\t\t |                            |                            |")
        print("B\t\t\t |      [" + self.node_list[3].figure + "]------------------[" + self.node_list[
            4].figure + "]------------------[" +
              self.node_list[5].figure + "]      |")
        print(" \t\t\t |       |                    |                    |       |")
        print(" \t\t\t |       |                    |                    |       |")
        print(" \t\t\t |       |                    |                    |       |")
        print(
            "C\t\t\t |       |      [" + self.node_list[6].figure + "]----------[" + self.node_list[7].figure + "]----------[" +
            self.node_list[
                8].figure + "]      |       |")
        print(" \t\t\t |       |       |                         |       |       |")
        print(" \t\t\t |       |       |                         |       |       |")
        print(" \t\t\t |       |       |                         |       |       |")
        print("D\t\t\t[" + self.node_list[9].figure + "]-----[" + self.node_list[10].figure + "]-----[" + self.node_list[
            11].figure + "]                       [" + self.node_list[12].figure + "]-----[" + self.node_list[
                  13].figure + "]-----[" +
              self.node_list[14].figure + "]")
        print(" \t\t\t |       |       |                         |       |       |")
        print(" \t\t\t |       |       |                         |       |       |")
        print(" \t\t\t |       |       |                         |       |       |")
        print(
            "E\t\t\t |       |      [" + self.node_list[15].figure + "]----------[" + self.node_list[16].figure + "]----------[" +
            self.node_list[17].figure + "]      |       |")
        print(" \t\t\t |       |                    |                    |       |")
        print(" \t\t\t |       |                    |                    |       |")
        print(" \t\t\t |       |                    |                    |       |")
        print(
            "F\t\t\t |      [" + self.node_list[18].figure + "]------------------[" + self.node_list[
                19].figure + "]------------------[" +
            self.node_list[20].figure + "]      |")
        print(" \t\t\t |                            |                            |")
        print(" \t\t\t |                            |                            |")
        print(" \t\t\t |                            |                            |")
        print("G\t\t\t[" + self.node_list[21].figure + "]--------------------------[" + self.node_list[
            22].figure + "]--------------------------[" + self.node_list[23].figure + "]")

    def adjacent_nodes(self, pos):
        adjacent = [None] * self.number_of_nodes
        adjacent[0] = [1, 9]
        adjacent[1] = [0, 2, 4]
        adjacent[2] = [1, 14]
        adjacent[3] = [4, 10]
        adjacent[4] = [1, 3, 5, 7]
        adjacent[5] = [4, 13]
        adjacent[6] = [7, 11]
        adjacent[7] = [4, 6, 8]
        adjacent[8] = [7, 12]
        adjacent[9] = [0, 10, 21]
        adjacent[10] = [3, 9, 11, 18]
        adjacent[11] = [6, 15]
        adjacent[12] = [8, 17]
        adjacent[13] = [5, 12, 14, 20]
        adjacent[14] = [2, 23]
        adjacent[15] = [11, 16]
        adjacent[16] = [15, 17, 19]
        adjacent[17] = [12, 16]
        adjacent[18] = [10, 19]
        adjacent[19] = [16, 18, 20, 22]
        adjacent[20] = [13, 19]
        adjacent[21] = [9, 22]
        adjacent[22] = [19, 21, 23]
        adjacent[23] = [14, 22]

        return adjacent[pos]

    def get_milllist(self, player, pos):
        mill_list = [[0][0]] * self.number_of_nodes
        mill_list[0] = [[0, 1, 2], [0, 9, 21]]
        mill_list[1] = [[0, 1, 2], [1, 4, 7]]
        mill_list[2] = [[0, 1, 2], [2, 14, 23]]
        mill_list[3] = [[3, 4, 5], [3, 10, 18]]
        mill_list[4] = [[3, 4, 5], [1, 4, 7]]
        mill_list[5] = [[3, 4, 5], [5, 13, 17]]
        mill_list[6] = [[6, 7, 8], [6, 11, 15]]
        mill_list[7] = [[6, 7, 8], [1, 4, 7]]
        mill_list[8] = [[6, 7, 8], [8, 12, 17]]
        mill_list[9] = [[9, 10, 11], [0, 9, 21]]
        mill_list[10] = [[9, 10, 11], [3, 10, 18]]
        mill_list[11] = [[9, 10, 11], [6, 11, 15]]
        mill_list[12] = [[12, 13, 14], [8, 12, 17]]
        mill_list[13] = [[12, 13, 14], [5, 13, 20]]
        mill_list[14] = [[12, 13, 14], [2, 14, 23]]
        mill_list[15] = [[15, 16, 17], [6, 11, 15]]
        mill_list[16] = [[15, 16, 17], [16, 19, 22]]
        mill_list[17] = [[15, 16, 17], [8, 12, 17]]
        mill_list[18] = [[18, 19, 20], [3, 10, 18]]
        mill_list[19] = [[18, 19, 20], [16, 19, 22]]
        mill_list[20] = [[18, 19, 20], [5, 13, 20]]
        mill_list[21] = [[21, 22, 23], [0, 9, 21]]
        mill_list[22] = [[21, 22, 23], [16, 19, 22]]
        mill_list[23] = [[21, 22, 23], [2, 14, 23]]

        return mill_list[pos]

    def get_max_number_of_pieces(self):
        return max_number_of_pieces

    def check_if_node_is_empty(self, pos):
        return self.node_list[pos].empty


    #Function for the first stage of the game when players are placing their pieces. msg is the coordinate that will 
    #be sent to the other player. If player gets trio the coordinate of the removed piece will be added in the message as remove_msg
    def place_piece(self, player):
        self.print_board()
        while True:
            (pos,msg) = self.get_input(str("Place a piece on an empty node (A1-G7): "))
            if pos is not None:
                if pos < self.number_of_nodes and self.node_list[pos].empty:
                    player.pieces.append(Piece(pos, player.name))
                    self.node_list[pos].figure = player.figure
                    self.node_list[pos].empty = False
                    self.print_board()
                    player.pieces_placed +=1
                    if self.is_trio(player, pos):
                       remove_msg = self.remove_piece(player)
                       return msg + remove_msg
                    
                    return msg

                else:
                    print("Invalid location")

    #Will be called by the client if the opponent places a piece
    def place_opponent(self,pos):
        if pos is not None:
            if pos < self.number_of_nodes and self.node_list[pos].empty:
                self.players[1].pieces.append(Piece(pos, self.players[1].name))
                self.node_list[pos].figure = self.players[1].figure
                self.node_list[pos].empty = False
                self.print_board()
       


    def check_mill(self, player, pos):
        mills = self.get_milllist(player, pos)
        for mill in mills:
            if self.node_list[mill[0]].figure == player.figure and self.node_list[mill[1]].figure == player.figure and \
                    self.node_list[mill[2]].figure == player.figure:
                return True

        return False


    def remove_piece(self, current_player):
        while True:
            try:

                (piece_pos,msg) = self.get_input("Which piece do you want to remove?")
                for player in self.players:
                    if player != current_player:
                        selected_piece = Piece(piece_pos, player.name)
                        print(player.name)
                        player.pieces.remove(selected_piece)
                        self.node_list[piece_pos].figure = " "
                        self.node_list[piece_pos].empty = True
                        return msg
            except:
                print("Not a valid location. Try Again!")
    
    #will be called by the client if the opponent removes a piece. Player will be 1 if the method should remove the opponents piece
    #And 0 if method should remove the players piece. 
    def opponent_remove_piece(self,piece_pos,player):
        selected_piece = Piece(piece_pos, self.players[player].name)
        self.players[player].pieces.remove(selected_piece)
        self.node_list[piece_pos].figure = " "
        self.node_list[piece_pos].empty = True
        self.print_board()



    def print_scoreboard(self):
        print("\t\t\t\t     _____________________________________")
        print("\t\t\t\t    |                    ".ljust(45) + "|")
        print(
            "\t\t\t\t    |    {} Has {} pieces on the board".format(self.players[0].name, self.players[0].pieces_left()).ljust(45,
                                                                                                                     " ") + "|")
        print(
            "\t\t\t\t    |    {} Has {} pieces on the board".format(self.players[1].name, self.players[1].pieces_left()).ljust(45,
                                                                                                                     " ") + "|")
        print("\t\t\t\t    |                    ".ljust(45) + "|")
        print("\t\t\t\t    |____________________________________|")

    #will return x which is the int converted from the coord_dict and raw_x which is the coordinate in the form A1
    def get_input(self,input_text):
        while True:
            raw_x = input(input_text)
            if raw_x.upper() == 'M':
                menu(True)
                break
            x = self.coord_dictionary(raw_x.upper())
            if x is None:
                print(raw_x + " is not a valid coordinate on the board")
            else:
                return (x,raw_x)

    def convert_to_coord(self, pos):
        print(pos + 'this is in convert')
        coord = self.coord_dictionary(pos.upper())
        return coord

    #Checks what  stage the game is in and returns it as a String. Should be redone to stop using Strings
    def check_what_stage(self,player):
        if player.pieces_placed <= self.max_number_of_pieces-1:
                return 'stage1'
        if self.players[0].pieces_left() > 2 and self.players[1].pieces_left() > 2:
            if  player.pieces_left() > 3:
                return 'stage2'
            elif player.pieces_left() == 3:
                return 'stage3'
            else:
                print("Error")

    #Called by the client if it is the players turn
    def players_turn(self, player):
        what_stage = self.check_what_stage(player)
        if what_stage == 'stage1':
            msg = self.place_piece(player)
            return 'PLA' + msg
        elif what_stage == 'stage2':
            msg = self.stage_2(player)
            return 'MOV' + msg
        elif what_stage == 'stage3':
            msg = self.stage_3(player)
            #self.get_winner()
            if(self.we_have_a_winner):
                return 'FIN' + msg
            return 'MOV' + msg

    def is_trio(self,player,pos):
        trios = self.get_triolist(player, pos)
        for trio in trios:
            if self.node_list[trio[0]].figure == player.figure and self.node_list[trio[1]].figure == player.figure \
                    and self.node_list[trio[2]].figure == player.figure:
                return True
        return False          

    def coord_dictionary(self, coord):
        coord_dict = {
            "A1": 0,
            "A4": 1,
            "A7": 2,
            "B2": 3,
            "B4": 4,
            "B6": 5,
            "C3": 6,
            "C4": 7,
            "C5": 8,
            "D1": 9,
            "D2": 10,
            "D3": 11,
            "D5": 12,
            "D6": 13,
            "D7": 14,
            "E3": 15,
            "E4": 16,
            "E5": 17,
            "F2": 18,
            "F4": 19,
            "F6": 20,
            "G1": 21,
            "G4": 22,
            "G7": 23,
            }
        return coord_dict.get(coord)

    def get_triolist(self,player, pos):
        trio_list = [[0][0]] * self.number_of_nodes
        trio_list[0] = [[0, 1, 2], [0, 9, 21]]
        trio_list[1] = [[0, 1, 2], [1, 4, 7]]
        trio_list[2] = [[0, 1, 2], [2, 14, 23]]
        trio_list[3] = [[3, 4, 5], [3, 10, 18]]
        trio_list[4] = [[3, 4, 5], [1, 4, 7]]
        trio_list[5] = [[3, 4, 5], [5, 13, 17]]
        trio_list[6] = [[6, 7, 8], [6, 11, 15]]
        trio_list[7] = [[6, 7, 8], [1, 4, 7]]
        trio_list[8] = [[6, 7, 8], [8, 12, 17]]
        trio_list[9] = [[9, 10, 11], [0, 9, 21]]
        trio_list[10] = [[9, 10, 11], [3, 10, 18]]
        trio_list[11] = [[9, 10, 11], [6, 11, 15]]
        trio_list[12] = [[12, 13, 14], [8, 12, 17]]
        trio_list[13] = [[12, 13, 14], [5, 13, 20]]
        trio_list[14] = [[12, 13, 14], [2, 14, 23]]
        trio_list[15] = [[15, 16, 17], [6, 11, 15]]
        trio_list[16] = [[15, 16, 17], [16, 19, 22]]
        trio_list[17] = [[15, 16, 17], [8, 12, 17]]
        trio_list[18] = [[18, 19, 20], [3, 10, 18]]
        trio_list[19] = [[18, 19, 20], [16, 19, 22]]
        trio_list[20] = [[18, 19, 20], [5, 13, 20]]
        trio_list[21] = [[21, 22, 23], [0, 9, 21]]
        trio_list[22] = [[21, 22, 23], [16, 19, 22]]
        trio_list[23] = [[21, 22, 23], [2, 14, 23]]

        return trio_list[pos]

    #Performs neccesary action for the player if the game is in stage 2.
    def stage_2(self,player):
        while True:
            self.print_board()
            made_move = False
            (current_pos,old_pos_msg) = self.get_input(" move a piece:")
            if self.node_list[current_pos].figure == player.figure:
                (new_pos,new_pos_msg) = self.get_input("Where do you want to move the piece?")
                for piece in player.pieces:
                    if current_pos == piece.pos:
                        made_move = self.move_piece(player, piece, new_pos, False)
                        self.print_board()
                if made_move:
                    if self.is_trio(player, new_pos):
                        remove_msg = self.remove_piece(player)
                        self.print_board()
                        return old_pos_msg + new_pos_msg + remove_msg
                return old_pos_msg + new_pos_msg
            else:
                print("That is not your piece")

    def stage_3(self,player):
        while True:
            self.print_board()
            made_move = False
            (current_pos, old_pos_msg) = self.get_input(str(player.name + " move a piece:"))
            if self.node_list[current_pos].figure == player.figure:
                (new_pos, new_pos_msg) = self.get_input("Where do you want to move the piece?")
                for piece in player.pieces:
                    if current_pos == piece.pos:
                        made_move = self.move_piece(player, piece, new_pos, True)
                if made_move:
                    if self.is_trio(player, new_pos):
                        remove_msg = self.remove_piece(player)
                        if self.players[0].pieces_left() == 2 or self.players[1].pieces_left() == 2:
                            self.get_winner()
                        return old_pos_msg + new_pos_msg + remove_msg
                    return old_pos_msg + new_pos_msg
            else:
                print("That is not your piece")

    def move_piece(self, player, piece, new_pos, is_stage_3):
        if self.valid_move(piece.pos, new_pos, is_stage_3):
            self.node_list[piece.pos].figure = " "
            self.node_list[piece.pos].empty = True
            self.node_list[new_pos].figure = player.figure
            self.node_list[new_pos].empty = False
            piece.pos = new_pos
            return True
        else:
            print(" Invalid move")
            return False

    def valid_move(self, old_pos, new_pos, is_stage_3):
        if is_stage_3 is True:
            if self.node_list[new_pos].empty:
                return True
            else:
                return False

        else:
            if self.node_list[new_pos].empty and (new_pos in self.adjacent_nodes(old_pos)):
                return True
            else:
                return False

    def get_winner(self):
        winner = ""
        remaining_pieces = 0
        for player in self.players:
            if player.pieces_left() > 2:
                winner = player.name
                remaining_pieces = player.pieces_left()
                self.we_have_a_winner = True

        print("The winner is " + winner + " with " + str(remaining_pieces) + " pieces remaining")





# below here are functions that i yet haven't moved to the board class-----------------------------------------------------------------------------------------------------



def clear():
    os.system("cls")


# Game Functions---------------------------------------------------------------------------------------------------------
def create_nodes():
    for i in range(0, NUMBER_OF_NODES):
        NODE_LIST.append(Coord(i, True, " "))


def create_new_game():
    create_nodes()
    for player in PLAYERS:
        player.pieces = []

    PLAYERS[0].nextTurn = True
    print("\n\tYou will now begin the game by placing " + str(MAX_NUMBER_OF_PIECES_PER_PLAYER) + " pieces each")
    place_piece()


def change_turn(current_player):
    for player in PLAYERS:
        if player is not current_player:
            player.nextTurn = True
        else:
            player.nextTurn = False



def play(ACTIVE_GAME):
    if not ACTIVE_GAME:
        create_new_game()
    else:
        while PLAYERS[0].pieces_left() > 2 and PLAYERS[1].pieces_left() > 2:
            for player in PLAYERS:
                if player.nextTurn:
                    if player.pieces_left() > 3:
                        stage_2(player)
                    elif player.pieces_left() == 3:
                        stage_3(player)
                    else:
                        print("Error")







# Setting Functions------------------------------------------------------------------------------------------------------
def settings(ACTIVE_GAME):
    clear()
    print()
    print("\t\t\t\t  _________       __    __  .__                      ")
    print("\t\t\t\t /   _____/ _____/  |__/  |_|__| ____    ____  ______")
    print("\t\t\t\t \_____  \_/ __ \   __\   __\  |/    \  / ___\/  ___/")
    print("\t\t\t\t /        \  ___/|  |  |  | |  |   |  \/ /_/  >___ \ ")
    print("\t\t\t\t/_______  /\___  >__|  |__| |__|___|  /\___  /____  >")
    print("\t\t\t\t        \/     \/                   \//_____/     \/ ")
    print()
    print("\t\t\t\t      Enter 1 Change Names")
    print("\t\t\t\t      Enter 2 Change Figures")
    print("\t\t\t\t      Enter 3 to go back to menu")
    print()
    print("\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t     UU-Studios©")
    print("\t\t\t\t  ---------------------------------------------")

    while True:
        try:
            choice = int(input("\t\t\t\t\t  Enter your choice: "))
            break
        except ValueError:
            print("\t\t\tNot a valid option. Try Again!")

    if choice == 1:
        change_name(ACTIVE_GAME)
    elif choice == 2:
        change_figure(ACTIVE_GAME)
    elif choice == 3:
        clear()
        menu(ACTIVE_GAME)


def change_name(ACTIVE_GAME):
    i = 1
    for player in theBoard.players:
        player.name = input("Type player " + str(i) + " name: ")
        i = i + 1
    settings(ACTIVE_GAME)


def change_figure(ACTIVE_GAME):
    for player in PLAYERS:
        player.figure = input(player.name + " figure: ")
    settings(ACTIVE_GAME)


# Piece Functions--------------------------------------------------------------------------------------------------------


def place_piece():
    for i in range(0, MAX_NUMBER_OF_PIECES_PER_PLAYER):
        for player in PLAYERS:
            if player.nextTurn is True:
                while True:
                    print_board()
                    x = get_input(str(" " + player.name + " place a piece on an empty node (A1-G7): "))
                    if x is not None:
                        if x < NUMBER_OF_NODES and NODE_LIST[x].empty:
                            player.pieces.append(Piece(x, player.name))
                            NODE_LIST[x].figure = player.figure
                            NODE_LIST[x].empty = False
                            if is_trio(player, x):
                                remove_piece(player)
                            if x != "M":
                                change_turn(player)
                            break
                        else:
                            print("Invalid location")

    play(True)




# trio Functions---------------------------------------------------------------------------------------------------------
def is_trio(player, pos):
    trios = get_triolist(player, pos)
    for trio in trios:
        if NODE_LIST[trio[0]].figure == player.figure and NODE_LIST[trio[1]].figure == player.figure \
                and NODE_LIST[trio[2]].figure == player.figure:
            return True
    return False


# Hardcoded data---------------------------------------------------------------------------------------------------------



def adjacent_nodes(pos):
    adjacent = [None] * NUMBER_OF_NODES
    adjacent[0] = [1, 9]
    adjacent[1] = [0, 2, 4]
    adjacent[2] = [1, 14]
    adjacent[3] = [4, 10]
    adjacent[4] = [1, 3, 5, 7]
    adjacent[5] = [4, 13]
    adjacent[6] = [7, 11]
    adjacent[7] = [4, 6, 8]
    adjacent[8] = [7, 12]
    adjacent[9] = [0, 10, 21]
    adjacent[10] = [3, 9, 11, 18]
    adjacent[11] = [6, 10, 15]
    adjacent[12] = [8, 13, 17]
    adjacent[13] = [5, 12, 14, 20]
    adjacent[14] = [2, 23]
    adjacent[15] = [11, 16]
    adjacent[16] = [15, 17, 19]
    adjacent[17] = [12, 16]
    adjacent[18] = [10, 19]
    adjacent[19] = [16, 18, 20, 22]
    adjacent[20] = [13, 19]
    adjacent[21] = [9, 22]
    adjacent[22] = [19, 21, 23]
    adjacent[23] = [14, 22]

    return adjacent[pos]






# Graphics Functions-----------------------------------------------------------------------------------------------------
def print_title():
    clear()
    time.sleep(3)
    print()
    print("\t\t\t\t   _   _ _   _      ____  _             _ _               ")
    print("\t\t\t\t  | | | | | | |    / ___|| |_ _   _  __| (_) ___  ___     ")
    print("\t\t\t\t  | | | | | | |____\___ \| __| | | |/ _` | |/ _ \/ __|    ")
    print("\t\t\t\t  | |_| | |_| |_____|__) | |_| |_| | (_| | | (_) \__ \    ")
    print("\t\t\t\t   \___/ \___/     |____/ \__|\__,_|\__,_|_|\___/|___/    ")
    print()
    print()
    print("\t\t\t\t\t ____                           _       _ _ ")
    print("\t\t\t\t\t|  _ \ _ __ ___  ___  ___ _ __ | |_ ___| | |")
    print("\t\t\t\t\t| |_) | '__/ _ \/ __|/ _ \ '_ \| __/ __| | |")
    print("\t\t\t\t\t|  __/| | |  __/\__ \  __/ | | | |_\__ \_|_|")
    print("\t\t\t\t\t|_|   |_|  \___||___/\___|_| |_|\__|___(_|_)")
    time.sleep(1)
    print()
    print("\t\t\t\t _   _ _   _              ____                      _ _  ")
    print("\t\t\t\t| | | | | | |  ______    / ___| __ _ _ __ ___   ___| | | ")
    print("\t\t\t\t| | | | | | | |______|  | |  _ / _` | '_ ` _ \ / _ \ | | ")
    print("\t\t\t\t| |_| | |_| |           | |_| | (_| | | | | | |  __/_|_| ")
    print("\t\t\t\t\____/\____/             \____|\__,_|_| |_| |_|\___(_|_) ")
    print("\t")
    time.sleep(2)
    clear()
    print("\t")
    print("\t\t   ___  ___  ___  ___                 ________  ________  _____ ______   _______      ")
    print("\t\t  |\  \|\  \|\  \|\  \               |\   ____\|\   __  \|\   _ \  _   \|\  ___ \     ")
    print("\t\t  \ \  \\\  \ \  \\\  \  ____________\ \  \___|\ \  \|\  \ \  \\\__\ \  \ \   __/|    ")
    print("\t\t   \ \  \\\  \ \  \\\  \|\____________\ \  \  __\ \   __  \ \  \\|__| \  \ \  \_|/__  ")
    print("\t\t    \ \  \\\  \ \  \\\  \|____________|\ \  \|\  \ \  \ \  \ \  \    \ \  \ \  \_|\ \ ")
    print("\t\t     \ \_______\ \_______\              \ \_______\ \__\ \__\ \__\    \ \__\ \_______\ ")
    print("\t\t      \|_______|\|_______|               \|_______|\|__|\|__|\|__|     \|__|\|_______|")
    print("\t")
    print()

def settings(ACTIVE_GAME):
    clear()
    print()
    print("\t\t\t\t  _________       __    __  .__                      ")
    print("\t\t\t\t /   _____/ _____/  |__/  |_|__| ____    ____  ______")
    print("\t\t\t\t \_____  \_/ __ \   __\   __\  |/    \  / ___\/  ___/")   
    print("\t\t\t\t /        \  ___/|  |  |  | |  |   |  \/ /_/  >___ \ ") 
    print("\t\t\t\t/_______  /\___  >__|  |__| |__|___|  /\___  /____  >") 
    print("\t\t\t\t        \/     \/                   \//_____/     \/ ")
    print()
    print("\t\t\t\t      Enter 1 Change Names")
    print("\t\t\t\t      Enter 2 Change Figures")
    print("\t\t\t\t      Enter 3 to go back to menu")
    print()
    print("\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t     UU-Studios")
    print("\t\t\t\t  ---------------------------------------------")

    while True:
        try:
            choice = int(input("\t\t\t\t\t  Enter your choice: "))
            break
        except ValueError:
            print("\t\t\tNot a valid option. Try Again!")

    if choice == 1:
        change_name(ACTIVE_GAME)
    elif choice == 2:
        change_figure(ACTIVE_GAME)
    elif choice == 3:
        clear()
        menu(ACTIVE_GAME)




def menu(ACTIVE_GAME):
    print("\t\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t\t   MAIN MENU")
    print("\t\t\t\t\t  ---------------------------------------------")
    if ACTIVE_GAME:
        print("\t\t\t\t\t\t      Enter 0 to Resume game")

    print("\t\t\t\t\t\t      Enter 1 to Start New game")
    print("\t\t\t\t\t\t      Enter 2 for How to Play")
    print("\t\t\t\t\t\t      Enter 3 for Settings")
    print("\t\t\t\t\t\t      Enter 4 to Quit")
    print()
    print("\t\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t         UU-Studios©")
    print("\t\t\t\t\t  ---------------------------------------------")

    while True:
        try:
            choice = int(input("\t\t\t\t\t  Enter your choice: "))
            break
        except ValueError:
            print("\t\t\tNot a valid option. Try Again!")

    if choice == 0 and ACTIVE_GAME:
        play(True)
    elif choice == 1:
        play(False)
    elif choice == 2:
        rules()
    elif choice == 3:
        settings(ACTIVE_GAME)
    elif choice == 4:
        clear()
        sys.exit()


def rules():
    clear()
    print()
    print("\t\t\t\t      __________      .__                 ")
    print("\t\t\t\t      \______   \__ __|  |   ____   ______")
    print("\t\t\t\t       |       _/  |  \  | _/ __ \ /  ___/")
    print("\t\t\t\t       |    |   \  |  /  |_\  ___/ \___ \ ")
    print("\t\t\t\t       |____|_  /____/|____/\___  >____  >")
    print("\t\t\t\t              \/                \/     \/ ")
    print("\t")
    print("\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t   UU-Studios©")
    print("\t\t\t\t  ---------------------------------------------")
    print()
    print("\t\t 1. Choose black or white pieces. The player with black pieces will start the game.")
    print()
    print("\t\t 2. Place pieces on the board using the coordinate system [A1-G7]. The player will put one piece")
    print("\t\t each turn and will place a total of 9 pieces on the board. When the player has put three pieces")
    print("\t\t in a trio the player will be able to move a piece using the coordinate system [A1-G7]. The player")
    print("\t\t can not move pieces from the opponent that are in a trio.")
    print()
    print("\t\t 3. When all pieces are placed one will be able to move the pieces between the different joints. The")
    print("\t\t player can only move one step each turn. The goal is to create a situation where the opponent loses")
    print("\t\t their pieces until they can no longer make any new moves or have less than three pieces left.")
    print()

    while True:
        try:
            choice = int(input("\t\t\t\t  Enter your 1 to go back to the Menu: "))
            break
        except ValueError:
            print("\t\t\tNot a valid option. Try Again!")

    if choice == 1:
        clear()
        menu(False)

def change_turn(current_player):
    for player in theBoard.players:
        if player is not current_player:
            player.nextTurn = True
        else:
            player.nextTurn = False

def create_new_game():
    create_nodes()
    for player in PLAYERS:
        player.pieces = []

    PLAYERS[0].nextTurn = True
    print("\n\tYou will now begin the game by placing " + str(theBoard.max_number_of_pieces) + " pieces each")
    msg = theBoard.place_piece(player)

def play(ACTIVE_GAME):
    if not ACTIVE_GAME:
        for player in theBoard.players:
            player.pieces = []
        theBoard.players[0].nextTurn = True
        print("\n\tYou will now begin the game by placing " + str(theBoard.max_number_of_pieces) + " pieces each")
        msg = theBoard.players_turn(theBoard.players[0])
        change_turn(theBoard.players[0])
        
    while True:
        for player in theBoard.players:
            if player.nextTurn:
                    msg = theBoard.place_piece(player)
                    change_turn(player)
            else:
                print("Error")



#Global Variables------------------------------------------------------------------------------------------------------
theBoard = Board(9,24)
print_title()
menu(False)