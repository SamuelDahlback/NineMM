import socket
import select
import time

def main(hostIP, port):
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
                myMov = input("Your move:")
                myMSG = myMov + "|"
                #Send my move
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())

            #Recieved move from opponent
            if (data[0:3] == 'MOV'):
                print("opponents move: " + data[3:])
                myMov = input("Your move:")
                myMSG = myMov + "|"
                #Send my move
                _, _, _ = select.select([], [s], [])
                s.sendall(myMSG.encode())
            
            #opponent says game is finished
            if (data[0:3] == 'FIN'):
                print("Opponent says game is finished: Oponnent says " + data[3:])
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