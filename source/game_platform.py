# Imports---------------------------------------------------------------------------------------------------------------
import time
import os
import sys
from time import sleep
import server
from threading import Thread,Lock
import socket, sys
import time
import os
import sys
import socket
import select

#WE APOLOGIZE FOR THE CODE BEING IN ONE BIG FILE. 
#This is becouse due to our limited lack of knowledge in python we had an issue with imports that we could not solve.

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
    online_game = False

    def __init__(self, max_number_of_pieces_per_player, number_of_nodes):
        self.max_number_of_pieces = max_number_of_pieces_per_player
        self.number_of_nodes = number_of_nodes

        while len(self.node_list) > 0:
            self.node_list.pop()
        for i in range(0, self.number_of_nodes):
            self.node_list.append(Coord(i, True, " "))


    def print_board(self):
        self.clear()
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
                        if self.check_mill(player, piece_pos):
                            print("Try another piece, that one is in a trio")
                        else:

                            selected_piece = Piece(piece_pos, player.name)
                            print(player.name)
                            player.pieces.remove(selected_piece)
                            self.node_list[piece_pos].figure = " "
                            self.node_list[piece_pos].empty = True
                            self.print_board()
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
            if(self.online_game == False):
                 if raw_x.upper() == 'M':
                    main_menu(True)
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
    def players_turn(self, player, online):


        if(online):
            self.online_game = True
            player = self.players[0]
        what_stage = self.check_what_stage(player)
        if what_stage == 'stage1':
            msg = self.place_piece(player)
            return 'PLA' + msg
        elif what_stage == 'stage2':
            msg = self.stage_2(player)
            return 'MOV' + msg
        elif what_stage == 'stage3':
            msg = self.stage_3(player)
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
                            self.clear_board()
                        return old_pos_msg + new_pos_msg + remove_msg
                    return old_pos_msg + new_pos_msg
            else:
                print("That is not your piece")

    def get_winner(self):
        winner = ""
        remaining_pieces = 0
        self.we_have_a_winner = True
        for player in self.players:
            if player.pieces_left() > 2:
                winner = player.name
                remaining_pieces = player.pieces_left()

        print("The winner is " + winner + "with " +
          str(remaining_pieces) + " pieces remaining")


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
        
    def clear_board(self):
        while len(self.node_list) > 0:
            self.node_list.pop()
        for i in range(0, self.number_of_nodes):
            self.node_list.append(Coord(i, True, " "))

        for player in self.players:
            player.pieces = []


    def clear(self):
        os.system("cls")



    # Setting Functions------------------------------------------------------------------------------------------------------






#Below are is code that was prevously in the interface file. It handles the functionality when creating an online game/tournament


class Menu:
    """Menu that defines string outputs for different menus"""

    def __init__(self):
        """[summary]
        """
        self.menu = ""
        self.validInput = ""
        self.mainMenu()
    
    def __str__(self):
        """[summary]

        :return: [description]
        :rtype: [type]
        """
        return self.menu

    def mainMenu(self):
        """Main menu, the inital menu that is shown to the user

        :return: Main menu string
        :rtype: String
        """
        self.menu = "MAIN MENU \n * [S]tart new server\n * [C]onnect to server\n * [B]ack\n * [Q]uit"
        self.validInput = "scqb"
        return self.menu

    def startServer(self):
        """Menu for starting a server with 1v1 or a tournament

        :return: Menu of options for the user
        :rtype: String
        """
        self.menu = "START NEW SERVER \n * [H]eads up play (1 vs 1)\n * [S]tart tournament"
        self.validInput = "hs"

        return self.menu

    def chooseGameStyle(self):
        """Menu for choosing how many player there should be in the tournament

        :return: Menu of options for the user
        :rtype: String
        """
        self.menu = "How many players? (max 8 players)"
        self.validInput = "345678"

        return self.menu    
    
    def connectServer(self):
        """Connect to a tournament server by writing in the hosts IP 
        adress in the terminal

        :return: The IP adress that has been entered by the user
        :rtype: String
        """
        self.menu = "CONNECT TO SERVER \n"
        print(chr(27) + "[2J") #Clear console
        print(self.menu) #Display menu
        address = input("Enter host IP-address: ")
        while True:
            if not validateIP(address):
                print(chr(27) + "[2J") #Clear console
                print(self.menu) #Display menu
                print("Error: Invalid IP-address, try again.")
                address = input("Enter host IP-address: ")
            else:
                return address
    
    def input(self):
        """Handles the users input when using the menu

        :return: playersChoice of action
        :rtype: String
        """
        print(chr(27) + "[2J") #Clear console
        print(self.menu) #Display menu
        while True:
            playerChoice = input("Action: ").lower()
            if not playerChoice or playerChoice[0] not in self.validInput:
                print(chr(27) + "[2J") #Clear console
                print(self.menu) #Display menu
                print("Error: invalid input, try again")
            else:
                return playerChoice

def validateIP(address):
    """Returns true if a IP adress is validated 

    :param address: A IP address that needs to be validated
    :type address: String
    :return: Whether the IP address was valid or not
    :rtype: bool
    """
    def max255(s):
        try: return str(int(s)) == s and 0 <= int(s) <= 255
        except: return False
    
    if address.count(".") == 3 and all(max255(i) for i in address.split(".")):
        return True
    else:
        return False


def startServer(address, port, minPlayers, maxPlayers):
    """Starts a server to host an online game tournament or heads-up match.

    :param address: IP address of the machine the server is run on.
    :type address: String
    :param port: The port the server should listen to.
    :type port: int
    :param minPlayers: Minimum amount of players to start a tournament
    :type minPlayers: int
    :param maxPlayers: Minimum amount of players that can connect to the server
    :type maxPlayers: int

    """
    server.main(address, port, minPlayers, maxPlayers)

  
def getIP():
    """A function that returns the IP on the computer, works
    for every operative system.

    :return: The IP on the computer
    :rtype: String
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(('10.255.255.255', 1))
        IP = s.getsockname()[0]
    except Exception:
        IP = '127.0.0.1'
    finally:
        s.close()
    return IP

def startGame(minPlayers, maxPlayers):
    """Starts a server in another thread and starts a client (host client) in the main thread which 
    connects to the server.

    :param minPlayers: Minimum amount of players to start a tournament
    :type minPlayers: int
    :param maxPlayers: Minimum amount of players that can connect to the server
    :type maxPlayers: int
    """

    hostIP = getIP()
    
    t = Thread(target=startServer, args=(hostIP, 65432, minPlayers, maxPlayers))
    t.start()
    sleep(0.1)
    HOST = hostIP   # The server's hostname or IP address
    PORT = 65432        # The port used by the host client
    client(HOST, PORT)

def online_menu():
    """Main function that handles user actions.
    """
    menu = Menu()
    choice = menu.input()
    if choice == "s":
        menu.startServer()
        choice = menu.input()
        if(choice == "h"):
            startGame(2,2)
        elif(choice == "s"):
             menu.chooseGameStyle()
             choice = menu.input()
             startGame(3, int(choice))
    elif choice == "c":
        address = menu.connectServer()
        client(address, 65432)
    elif choice == 'b':
        main_menu(False)
    elif choice == 'q':
        sys.exit()



#Code related to accesing the menu and playing a local game-------------------------------------------------------------------

def clear():
    os.system("cls")

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
        main_menu(ACTIVE_GAME)


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
        main_menu(ACTIVE_GAME)




def main_menu(ACTIVE_GAME):
    print("\t\t\t\t\t  ---------------------------------------------")
    print("\t\t\t\t\t\t\t   MAIN MENU")
    print("\t\t\t\t\t  ---------------------------------------------")
    if ACTIVE_GAME:
        print("\t\t\t\t\t\t      Enter 0 to Resume game")

    print("\t\t\t\t\t\t      Enter 1 to Start local game")
    print("\t\t\t\t\t\t      Enter 2 to Start or join an online game")
    print("\t\t\t\t\t\t      Enter 3 for How to Play")
    print("\t\t\t\t\t\t      Enter 4 for Settings")
    print("\t\t\t\t\t\t      Enter 5 to Quit")
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
        print('play online')
        online_menu()
        #implement commplatform menu
    elif choice == 3:
        rules()
    elif choice == 4:
        settings(ACTIVE_GAME)
    elif choice == 5:
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
        main_menu(False)

def change_turn(current_player):
    for player in theBoard.players:
        if player is not current_player:
            player.nextTurn = True
        else:
            player.nextTurn = False

def play(ACTIVE_GAME):
    if not ACTIVE_GAME:
        for player in theBoard.players:
            player.pieces = []
        theBoard.players[0].nextTurn = True
        print("\n\tYou will now begin the game by placing " + str(theBoard.max_number_of_pieces) + " pieces each")
        msg = theBoard.players_turn(theBoard.players[0], False)
        change_turn(theBoard.players[0])
        
    while True:
        for player in theBoard.players:
            if player.nextTurn:
                    msg = theBoard.players_turn(player, False)
                    change_turn(player)
            else:
                print("Error")



#Code that was prevously in the client file. It handles the online match
def client(hostIP, port):
    """This is right now fake playing some board game, so we
    can later on itegrate a real board game here. All moves sent should start with
    "MOV" + (the move) and if the game is finished "FIN" + ("WIN","LOSS" or "TIE")

    :param hostIP: The server IP-address
    :type hostIP: string
    :param port: The port
    :type port: int
    """
    #connect to the server
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    s.connect((hostIP, port))

    while True:
        #wait on and receive data from server
        recv_data = s.recv(1024)

        #If the recieved data is empty, we have lost connection.
        if len(recv_data)==0:
            print("\nDisconnected from the server.")
            s.close()
            break
        
        #Decode the bytelike object
        recv_data = recv_data.decode()

        #Split up the data where "|" occurs because the data can
        #include numerous messages.
        dataArray = recv_data.split(sep="|")
        for data in dataArray:
            #We should make the first move in the game(This also indicates what 
            # colour we are!)
            if (data[0:3] == 'FMV'):
                print(data[3:])
                myMov = theBoard.players_turn(theBoard.players[0], True)
                #update our game board after we make a move
                myMSG = myMov + "|"
                #Send my move
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())

            #Recieved a placement move from opponent
            if (data[0:3] == 'PLA'):
                print("opponents move: " + data[3:5])
                move = data[3:]
                if len(move) == 4:
                    print(move[2:])
                    print(move[0:2])
                    remove_coord = theBoard.convert_to_coord(move[2:])
                    theBoard.opponent_remove_piece(remove_coord, 0)
                    move_coord = theBoard.convert_to_coord(move[0:2])
                    theBoard.place_opponent(move_coord)
                elif len(move) == 2:
                    coord = theBoard.convert_to_coord(move)
                    theBoard.place_opponent(coord)
                #update game board here after recieving move

                myMov = theBoard.players_turn(theBoard.players[0], True)
                #update our game board after we make a move
                myMSG =  myMov + "|"
                #Send my move
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())

            #Received a move from the opponent. Frist we check if opponent have also removed a piece of ours then perform action
            if (data[0:3] == 'MOV'):
                move = data[3:]

                #if message length is = 6 we need to move a piece and then remove one of our pieces
                if len(move) == 6:
                    print(move[2:])
                    print(move[0:2])

                    #get coord of the piece that is moving and remove from board
                    remove_own_coord = theBoard.convert_to_coord(move[0:2])
                    theBoard.opponent_remove_piece(remove_own_coord, 1)

                    #Update board with new pos of opponents piece 
                    move_coord = theBoard.convert_to_coord(move[2:4])
                    theBoard.place_opponent(move_coord)

                    #Remove our piece
                    remove_own_coord = theBoard.convert_to_coord(move[4:6])
                    theBoard.opponent_remove_piece(remove_own_coord, 0)
                
                #If message length = 4 we only need to move a piece
                elif len(move) == 4:
                    #get coord of the piece that is moving and remove from board
                    remove_own_coord = theBoard.convert_to_coord(move[0:2])
                    theBoard.opponent_remove_piece(remove_own_coord, 1)

                    #Update board with new pos of opponents piece 
                    move_coord = theBoard.convert_to_coord(move[2:4])
                    theBoard.place_opponent(move_coord)
            
                myMov = theBoard.players_turn(theBoard.players[0], True)
                
                #update our game board after we make a move
                myMSG =  myMov + "|"
                #Send my move
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())
                    

            
            #opponent says game is finished
            if (data[0:3] == 'FIN'):
                move = data[3:]

                #if message length is = 6 we need to move a piece and then remove one of our pieces
                if len(move) == 6:
                    print(move[2:])
                    print(move[0:2])
                    #get coord of the piece that is moving and remove from board
                    remove_own_coord = theBoard.convert_to_coord(move[0:2])
                    theBoard.opponent_remove_piece(remove_own_coord, 1)

                    #Update board with new pos of opponents piece 
                    move_coord = theBoard.convert_to_coord(move[2:4])
                    theBoard.place_opponent(move_coord)

                    #Remove our piece
                    remove_own_coord = theBoard.convert_to_coord(move[4:6])
                    theBoard.opponent_remove_piece(remove_own_coord, 0)

                theBoard.clear_board()


                print("Opponent says game is finished")
                myResult = input("Did you win or not?(WIN, LOSS, TIE):")
                myMSG = myResult + "|"
                #Send my result
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())

            #Recieved a message from the server.
            if (data[0:3] == 'MSG'):
                print(data[3:])




#Creates a board object and displays the main menu 
theBoard = Board(9,24)
#print_title()
main_menu(False)
