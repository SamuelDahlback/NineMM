from threading import Thread,Lock
import time
import selectors
import select
import socket
import types
import random
import operator

global waiting
waiting = True

class Player():
    """Player class

    :param conn: The socket connected to the player client
    :type conn: Socket
    :param playerNumber: Identifying number visible to other players
    :type playerNumber: int
    :param score: A players accumulated score during a tournament
    :type score: int
    :param playing: Wether a player is active in a game, defaults to False
    :type playing: bool, optional
    """
    def __init__(self, conn, playerNumber, score, playing=False):
        """Initialize player
        """
        self.conn = conn
        self.id = conn.fileno() # Player id == sockets file descriptor
        self.playerNumber = playerNumber
        self.score = score
        self.playing = playing
        self.disconnected = False

    def __lt__(self, other):
        """Implements ordenance. Orders after player ID.
        """
        return self.id < other.id

    #To send in a list of players to select.select, the players need a fileno()-method.
    def fileno(self):
        return self.id

class Game():
    """Game class
    
    :param player1: The player with the lowest id
    :type player1: Player
    :param player2: The player with the highest id
    :type player2: Player
    :param turn: Indicates which players turn is next, 1 for player1 and 2 for player2
    :type turn: int
    :param finished: True if the game is finished, defaults to False
    :type finished: bool, optional
    """

    def __init__(self, player1, player2, turn):
        """Initilize game
        """
        self.player1 = player1
        self.player2 = player2
        self.turn = turn
        self.active = False
        self.finished = False
        self.tie = False
        self.winner = None #player object

    def __eq__(self, other):
        """Implements equality. A Game is considered equal if both participating 
        players are the same.
        """
        return self.player1 == other.player1 and self.player2 == other.player2


    def start(self):
        """Starts the Game

        :return: False if the game ended without any moves being played (at least 
        one player was disconnected). Otherwise True.
        :rtype: Bool
        """
        # If both players were disconnected, set result to tie and end the game.
        # return False if this happens
        if self.player1.disconnected and self.player2.disconnected:
            self.end(self.player1, 'TIE')
            self.end(self.player2, 'TIE')
            return False

        #If one of the players are disconnected, the other player wins the game.
        #return False if this happens
        elif  self.player1.disconnected:
            self.end(self.player1, 'LOSS')
            self.end(self.player2, 'WIN')
            #Let the winner know that he/she got a win from walkover
            if (not self.player2.disconnected):
                _, wlist, _ = select.select([], [self.player2],[])
                if (self.player2 in wlist):
                    msg = "MSGYou got a win due to walkover from player " + str(self.player1.playerNumber) + "|"
                    self.player2.conn.send(msg.encode())
            return False

        elif  self.player2.disconnected:
            self.end(self.player2, 'LOSS')
            self.end(self.player1, 'WIN')
            #Let the winner know that he/she got a win from walkover
            if (not self.player1.disconnected):
                _, wlist, _ = select.select([], [self.player1],[])
                if (self.player1 in wlist):
                    msg = "MSGYou got a win due to walkover from player " + str(self.player2.playerNumber) + "|"
                    self.player1.conn.send(msg.encode())
            return False

        else:
            while True:
                #Make sure we are able to write to both players that the game has begun.
                _, wlist, _ = select.select([], [self.player1,self.player2],[])
                if (self.player1 in wlist) and (self.player2 in wlist):
                    msg = "MSGYour game against player " + str(self.player1.playerNumber) + " has started|"
                    self.player2.conn.send(msg.encode())
                    msg = "MSGYour game against player " + str(self.player2.playerNumber) + " has started|"
                    self.player1.conn.send(msg.encode())
                    while True:
                        #Make sure they are able to be written to again.
                        _, wlist, _ = select.select([], [self.player1,self.player2],[])
                        if (self.player1 in wlist) and (self.player2 in wlist):
                            if self.turn == 1:
                                msg = "FMVMake the first move|"
                                self.player1.conn.send(msg.encode())
                                msg = "MSGWait for oppononent to make his/her move...|"
                                self.player2.conn.send(msg.encode())
                            else:
                                msg = "FMVMake the first move|"
                                self.player2.conn.send(msg.encode())
                                msg = "MSGWait for oppononent to make his/her move...|"
                                self.player1.conn.send(msg.encode())
                            self.player1.playing = True
                            self.player2.playing = True
                            self.active = True
                            break

                    break
            return True

    
    def getOpponent(self, player):
        """Get the opponent player

        :param player: A player that is in the game
        :type player: Player
        :return: The opponent player if input was a player in the game. Otherwise None.
        :rtype: Player
        """
        if (player == self.player1):
            return self.player2
        elif (player == self.player2):
            return self.player1
        else:
            return None

    def end(self, player, result):
        """A player (client) is reporting that the game has ended, both 
        players (clients) needs to do this for the game to actually end.

        :param player: Player that is reporting the result
        :type player: Player
        :param result: Either "WIN","LOSS" or "TIE"
        :type result: String
        :return: True if both players (clients) have reported the same result
                 and the game has been ended, otherwise False.
        :rtype: Bool
        """
        opponent = self.getOpponent(player)
        if (self.winner == None and self.tie == False):
            if (result == 'WIN'):
                self.winner = player
            elif (result == 'LOSS'):
                self.winner = opponent
            elif (result == 'TIE'):
                self.tie = True
            return False
        else:
            if (result == 'WIN' and self.winner == player):
                player.score += 1
            elif (result == 'LOSS' and self.winner == opponent):
                opponent.score += 1
            elif (result == 'TIE' and self.tie == True):
                player.score += 0.5
                opponent.score += 0.5
            else:
                #someone is lying, dont give anyone score
                pass

            #Game has ended
            self.player1.playing = False
            self.player2.playing = False
            self.active = False
            self.finished = True
            return True

    def makeMove(self):
        """Communicate a move (message starts with "MOV") or that the game has
        finished (message starts with "FIN") between the two players in the game
        and call the end-method if that is the case. If a player has sent a move and
        it does not start with "MOV" or "FIN" it is assumed that their connection is
         lost and let the other player win.

        :return: True if the game has ended, otherwise False
        :rtype: Bool
        """
        if (self.turn == 1):
            player = self.player1
            opponent = self.player2
        else:
            player = self.player2
            opponent = self.player1
        rlist, wlist, _ = select.select([player], [opponent],[],0)
        #If opponent is writeable and player is readable.
        if (player in rlist) and (opponent in wlist):
            recv_data = player.conn.recv(1024)

            #Lost connection
            if(len(recv_data) == 0):
                player.disconnected = True
                player.conn.close()
                msg = "MSGLost connection to opponent, you win.|"
                opponent.conn.send(msg.encode())
                self.end(player, 'LOSS')
                return self.end(opponent, 'WIN')


            recv_data = recv_data.decode()
            if (recv_data[0:3] == 'MOV'):
                #send the move to opponent and set the turn to the opponent.
                opponent.conn.send(recv_data.encode())
                self.turn = abs(self.turn - 3)
                return False

            elif (recv_data[0:3] == 'FIN'):
                #Send the result to opponent and call the end-method
                opponent.conn.send(recv_data.encode())
                self.end(player, recv_data[3:].replace('|',''))

                #Wait until we can read from the opponent
                rlist, _, _ = select.select([opponent],[],[])
                
                if (opponent in rlist):
                    opp_data = opponent.conn.recv(1024)
                    if(len(recv_data) == 0):
                        #Disconnect the opponent and inform the player.
                        _, wlist, _ = select.select([],[player],[])
                        if (player in wlist):
                            #print("closing connection to player " + str(opponent.playerNumber))
                            opponent.disconnected = True
                            opponent.conn.close()
                            msg = "MSGLost connection to opponent, you win.|"
                            player.conn.send(msg.encode())
                            self.winner = player
                            return self.end(opponent, 'LOSS')
                    opp_data = opp_data.decode()
                    #expect a "FIN" from opponent otherwise assume disconnection.
                    if (opp_data[0:3] == 'FIN'):
                        return self.end(opponent, opp_data[3:].replace('|',''))
                    else:
                        #Disconnect the opponent and inform the player.
                        _, wlist, _ = select.select([],[player],[])
                        if (player in wlist):
                            #print("closing connection to player " + str(opponent.playerNumber))
                            opponent.disconnected = True
                            opponent.conn.close()
                            msg = "MSGLost connection to opponent, you win.|"
                            player.conn.send(msg.encode())
                            self.winner = player
                            return self.end(opponent, 'LOSS')

            else :
                #Message did not begin with "MOV" or "FIN", disconnect the player.
                #print("closing connection to player " + str(player.playerNumber))
                player.disconnected = True
                player.conn.close()
                msg = "MSGLost connection to opponent, you win.|"
                opponent.conn.send(msg.encode())
                self.end(player, 'LOSS')
                return self.end(opponent, 'WIN')
        return False


class Tournament():
    """Tournament class
    
    :param minPlayers: Minimum amount of players in order to start the tournament, defaults to 3
    :type minPlayers: int, optional
    :param maxPlayers: Maximum amount of players that can enter the tournament, defaults to 8
    :type maxPlayers: int, optional
    """

    def __init__(self, minPlayers=3, maxPlayers=8):
        """Initialize tournament
        """
        self.minPlayers = minPlayers
        self.maxPlayers = maxPlayers
        self.clients = {} # key: filedescriptor, value: Player
        self.matchUp = [] # Which matches to be played [Games]
        self.finishedGames = 0

    #Creates all match ups in the round robin tournament and shuffles the entire list.
    def matchUpPlayers(self):
        """Generate all games to be played during the tournament. Every player is 
        matched up with every other player in a round robin fashion. The order of 
        the games are randomized aswell as which player goes first in each game.
        """
        
        players = self.clients.values()
        for player1 in players:
            for player2 in players:
                if (player1 != player2):
                    game = Game(
                        min(self.clients[player1.id], self.clients[player2.id]), # Lowest playerID is player1
                        max(self.clients[player1.id], self.clients[player2.id]), # Highest playerID is player2
                        random.randint(1,2) # Starting player is chosen at random
                        )

                    if game not in self.matchUp:
                        self.matchUp.append(game)
        random.shuffle(self.matchUp)

    def beginMatches(self):
        """Begin all the matches that can begin (all matches where both players are not in 
        another game), do this whenever a match has ended.
        """
        for game in self.matchUp:
            #If both players in the matchUp are not playing and the game isnt finished, begin the game.
            if (not game.player1.playing and not game.player2.playing and not game.finished):
                started = game.start()
                #if the game is imidietly finished due to a player being disconnected
                if not started:
                    self.finishedGames += 1


        #Send this to all players that are not playing, if there is games left to play     
        if (self.finishedGames + 1 < len(self.matchUp)):
            waitingPlayers = [x for x in self.clients.values() if not x.playing]
            msg = "Your game will begin shortly..."
            self.sendMessage(msg,waitingPlayers)


    def scoreboard(self):
        """Calculates the total scoreboard of all players and returns a sorted list of all players. 
        The player with the highest score is at the beginning of the list.

        :return: List of all players, sorted in descending order by the score
        :rtype: [Player]
        """

        def playerBisect(players, newPlayer):
            """Finds the correct index to insert a player in a list of players sorted by their score.

            :param players: List of Player sorted by Player.score
            :type players: [Player]
            :param newPlayer: Player to be inserted
            :type newPlayer: Player
            :return: players with newPlayer inserted so that it is sorted by Player.score
            :rtype: [Player]
            """
            if len(players) > 0:
                for i, player in enumerate(players):
                    if newPlayer.score > player.score:
                        return i
                return len(players)
            else:
                return 0

        scoreboard = []
        for player in self.clients.values():
            scoreboard.insert(playerBisect(scoreboard, player), player)
        return scoreboard
            

    def scoreboardString(self):
        """Calculates the total scoreboard of all players (similar to scoreboard()) and returns string representation of it.

        :return: The final scoreboard as a string ready for printing.
        :rtype: String
        """
        scoreboard = self.scoreboard()
        scoreString = "\nFinal scoreboard:\n\n"
        for player in scoreboard:
            scoreString = scoreString + "Player " + str(player.playerNumber)+": "\
                          + str(player.score) + " points\n"
        return scoreString

    def start(self):
        """Starts the tournament
        """
        if (self.maxPlayers == 2 and self.minPlayers == 2):
            #send to all "1v1 game is starting."
            msg = "1v1 game is starting"
            self.sendMessage(msg, self.clients.values())
        else:
            #send to all "Round robin tournament of " + len(self.clients) +" players is starting"
            msg = "Round robin tournament of " + str(len(self.clients)) +" players is starting"
            self.sendMessage(msg, self.clients.values())

        self.matchUpPlayers()
        self.beginMatches()
        self.gameLoop()
        self.end()

    

    def end(self):
        """Ends the tournament
        """
        #Send the results to all players
        if (len(self.clients) < 3):
            winner = max(self.clients.values(), key=lambda player: player.score)
            msg = "Player " + str(winner.playerNumber) + " won the game"
            self.sendMessage(msg, self.clients.values())
        else:
            msg = "Tournament finished.\n" + self.scoreboardString()
            self.sendMessage(msg, self.clients.values())

        #close all connections
        for player in self.clients.values():
            player.conn.close()
        

    def gameLoop(self):
        """The gameloop, goes through all the games and does the communication
        between the players until there is no games left to play
        """
        while (self.finishedGames < len(self.matchUp)):
            
            for game in self.matchUp:
                if game.active:
                    #Just wait on some socket to be readable before continuing the loop
                    #to not put too much stress on this loop that is running on the host.
                    players = self.clients.values()
                    onlinePlayers = [x for x in players if not x.disconnected]
                    _, _, _ = select.select(onlinePlayers, [],[])
                    finished = game.makeMove()
                    if finished:
                        self.finishedGames += 1
                        self.beginMatches()


    def sendMessage(self, msg, players):
        """Sends messege to players

        :param msg: Message to be sent
        :type msg: String
        :param players: A list of players
        :type players: [Player]
        """
        #All communication begins with "MSG" or "FIN" and ends with "|",
        #So the players(clients) can distinguish seperate messages.
        msg = 'MSG' + msg + "|"
        #only send to players who are connected.
        onlinePlayers = [x for x in players if not x.disconnected]
        if (len(onlinePlayers) > 0):
            #the loop makes it so that we wait on all the players to be able to 
            #recieve the message
            while True:
                _, wlist, _ = select.select([], onlinePlayers,[])
                if len(onlinePlayers) == len(wlist):
                    for player in wlist:
                        player.conn.sendall(msg.encode())
                    break
    
# Set up client the first time it connects
def accept_wrapper(sock, printLock, sel, tournament):
    """Accepts a new socket and link it to a new player object and insert it 
    in the tournament.

    :param sock: Socket to accept
    :type sock: Socket
    :param printLock: A mutex lock to make prints mutual exclusive
    :type printLock: Mutex
    :param sel: selector, keeps track of the sockets
    :type sel: EpollSelector
    :param tournament: The tournament object
    :type tournament: Tournament object
    :return: The accepted players player object
    :rtype: Player
    """
    #Accept the connection
    conn, addr = sock.accept()  # Should be ready to read
    conn.setblocking(False)
    data = types.SimpleNamespace(addr=addr, inb=b'', outb=b'')
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    sel.register(conn, events, data=data)

    #create the player object and insert it into the tournament.
    playerNumber = len(tournament.clients)+1
    player = Player(conn, playerNumber, 0)
    tournament.clients[conn.fileno()] = player

    if (len(tournament.clients) != 1):
        #the first connection is the host itself so this should not print
        #when len(tournament.clients) == 1
        printLock.acquire()
        print('accepted connection from', addr)
        print("A total of " + str(len(tournament.clients)) + " player(s) have connected")
        printLock.release()
    if (len(tournament.clients) >= tournament.minPlayers):
        printLock.acquire()
        print("You can now start the game by typing 'start'")
        printLock.release()
    return player


def waitStart():
    """Takes input from the user when to start the tournament. Ment to be run in a seperate thread 
    to allow for more players to connect.
    """
    global waiting
    waiting = True
    ans = ""
    while(ans!="start"):
        ans = input()
    waiting = False

def main(address, port, minPlayers = 2, maxPlayers = 8):
    """Initializes a server to host game tournaments, waits for connecting clients and runs 
    a tournament.

    :param address: Host IP
    :type address: String
    :param port: Host port
    :type port: Int
    :param minPlayers: Minimum amount of players to start a tournament, defaults to 2
    :type minPlayers: int, optional
    :param maxPlayers: Minimum amount of players that can connect to the server, defaults to 8
    :type maxPlayers: int, optional
    """
    sel = selectors.DefaultSelector()
    host = address

    #This function is going to be executed in a separate thread, so 
    #to make sure there is no funny business in the terminal the prints 
    #is done with a mutex lock.
    printLock = Lock()

    #Create the tournament
    tournament = Tournament(minPlayers, maxPlayers)

    #Create server socket
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    server.bind((host, port))
    server.listen()
    server.setblocking(False)
    sel.register(server, selectors.EVENT_READ, data=None)
    printLock.acquire()
    print('listening on', (host, port))
    printLock.release()


    global waiting
    waiting = True
    t = Thread(target=waitStart)
    #Initiate separate thread that waits for the host to type 'start'
    t.start()
    printLock.acquire()
    print("\nServer created, tell your friends to connect to IP:", address)
    print("You are player 1")
    print("Waiting for players to connect...")
    printLock.release()

    #while host hasnt typed start or minimum amount of players havent yet connected
    while (waiting or len(tournament.clients) < tournament.minPlayers):
        if (len(tournament.clients) < tournament.maxPlayers):
            #accept new player
            events = sel.select(timeout=None)
            for key, _ in events:
                if key.data is None:
                    player = accept_wrapper(key.fileobj, printLock, sel, tournament)
                    while True:
                        #send welcome message to the new player, unless it is the host.
                        _, wlist, _ = select.select([], [player],[])
                        if (player in wlist):
                            if player.playerNumber != 1:
                                msg = "MSGWelcome player " + str(player.playerNumber) +\
                                      "!\nYou are connected to the server with IP:" + str(address) +\
                                      "\nPlease wait for the host to start the game|"
                                player.conn.sendall(msg.encode())
                            break

    #Wait on the thread t to finish(good practice)
    t.join()

    tournament.start()


if __name__ == "__main__":
    pass
    #main("127.0.0.1", 6234)
