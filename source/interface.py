from time import sleep
import server
import client
from threading import Thread,Lock
import socket, sys

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
        self.menu = "MAIN MENU \n * [S]tart new server\n * [C]onnect to server\n * [Q]uit"
        self.validInput = "scq"
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

def main():
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

if __name__ == "__main__":
    main()