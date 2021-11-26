import socket
import random
import string


# Client variables for setting up a connection
SERVER = "192.168.0.10"             # SERVER is used for server IP address  
PORT1 = 8000                        # PORT1 - port number. Server port used to receive unique code from server
PORT2 = 8001                        # PORT2 - port number. Server port used to send message
MSG_LENGTH = 1024                   # MSG_LENGTH - max size of message
FORMAT = 'utf-8'                    # FORMAT - text format

ADDR1 = (SERVER, PORT1)
ADDR2 = (SERVER, PORT2)

# Sends a message to the server
# Parameter msg - string message for server
def send(client, msg):
    try:
        client.send(msg.encode(FORMAT))
    except Exception as e:
        print(f"[SEND ERROR] {e}")

# Receive message from the server
# Return value - string message from server
def receive(client):
    try:
        msg = client.recv(MSG_LENGTH).decode(FORMAT)
        return msg
    except Exception as e:
        print(f"[RECEIVE ERROR] {e}")

# ID generation
# Return value: 8 character string
def generate_id():
    return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

# Message generation
# Return value: 32 character string
def generate_msg():
    return ''.join(random.SystemRandom().choice(string.ascii_lowercase) for _ in range(32))

# Used to connect to the server on PORT1 and get the code 
# Return value - received from server code
def get_code():
    client.connect(ADDR1)
    send(client, my_id)
    my_code = receive(client)
    print(f"My Code: {my_code}")
    return my_code

# Used to authorize user on server
# Parameter my_id - my user ID
# Parameter my_code - my code on server
# Raise NameError exception if not authorized 
def authorize(my_id, my_code):
    send(client, my_id)
    rec_msg = receive(client)
    if(rec_msg != "OK"):
        print(rec_msg)
        raise NameError(rec_msg)
    else:
        send(client, my_code)
        rec_msg = receive(client)
        if(rec_msg != "OK"):
            print(rec_msg)
            raise NameError(rec_msg)
        else:
            return

# Starts authorization process and sends a message to the server
# Parameter my_code - my code on server
def send_text_message(my_code):
    client.connect(ADDR2)
    try:
        authorize(my_id, my_code)
        send(client, generate_msg())
    except NameError as e:
        print(f"[SEND MESSAGE ERROR] {e}")
        return



my_id = generate_id()
print(f"My ID: {my_id}")
try:  
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_code = get_code()   
    client.close()
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    send_text_message(my_code)
    client.close()
except ConnectionRefusedError:
    print("Server Offline")
except Exception as e:
    print(f"[Error] {e}")


