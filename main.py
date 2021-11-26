import socket 
from server import *



# Server variables for setting up a connection
SERVER = socket.gethostbyname(socket.gethostname()) # SERVER is used for server IP address  
PORT1 = 8000                                        # PORT1 - port number. Server port used to provide unique code to clients
PORT2 = 8001                                        # PORT2 - port number. Server port used to receive message from clients
MSG_LENGTH = 1024                                   # MSG_LENGTH - max size of message
FORMAT = 'utf-8'                                    # FORMAT - text format


# Server start 
s = Server(SERVER, PORT1, PORT2, FORMAT, MSG_LENGTH)
try:
    s.start_server()
    input()
    s.shutdown_server()
except Exception as e:
    print(f"{e} :(")