import socket
import select
import time
import game_platform

def main(hostIP, port):
    theBoard = game_platform.Board(9,24)
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
                myMov = theBoard.players_turn(0)
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

                myMov = theBoard.players_turn(0)
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
            
                myMov = theBoard.players_turn(0)
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


                print("Opponent says game is finished)
                myResult = input("Did you win or not?(WIN, LOSS, TIE):")
                myMSG = myResult + "|"
                #Send my result
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())

            #Recieved a message from the server.
            if (data[0:3] == 'MSG'):
                print(data[3:])


if __name__ == "__main__":
    pass
    #main("127.0.0.1", 6234)