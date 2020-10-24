from time import sleep
import server
import client
from threading import Thread,Lock
import socket, sys
import game_platform
import time
import os
import sys


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
    client.main(HOST, PORT)

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
        client.main(address, 65432)
    elif choice == 'b':
        main_menu(False)

def clear():
    os.system("cls")

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

# Hardcoded data---------------------------------------------------------------------------------------------------------







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
        msg = theBoard.players_turn(theBoard.players[0], True)
        change_turn(theBoard.players[0])
        
    while True:
        for player in theBoard.players:
            if player.nextTurn:
                    msg = theBoard.players_turn(player,False)
                    change_turn(player)
            else:
                print("Error")

if __name__ == "__main__":

    theBoard = game_platform.Board(9,24)
    #print_title()
    main_menu(False)