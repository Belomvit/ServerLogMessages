import socket 
import threading
from datetime import datetime
import random
import string

# Сlass describing the whole server  
class Server:
    # Сonstructor initializing main variables 
    # Parameter SERVER - server IP address  
    # Parameter PORT1 - port number. Server port used to provide unique code to clients
    # Parameter PORT2 - port number. Server port used to receive message from clients
    # Parameter FORMAT - text format
    # Parameter MSG_LENGTH - max size of message
    def __init__(self, SERVER, PORT1, PORT2, FORMAT, MSG_LENGTH):
        self.SERVER = SERVER
        self.PORT1 = PORT1
        self.PORT2 = PORT2
        self.FORMAT = FORMAT
        self.MSG_LENGTH = MSG_LENGTH
        self.id_list = {}
        self.lock_file = threading.Lock()
        self.lock_list = threading.Lock()

    # Unique code generation for clients
    # Return value: 8 character string
    def generate_code(self):
        return ''.join(random.SystemRandom().choice(string.ascii_uppercase + string.digits) for _ in range(8))

    # User registration. 
    # Obtaining ID from clients and generating a code for them
    # For already used IDs it sends message that their ID already in use 
    # Parameter conn - is a new socket object usable to send and receive data on the connection
    # Parameter addr - is the address bound to the socket on the other end of the connection
    def register_user(self, conn, addr):
        msg = conn.recv(self.MSG_LENGTH).decode(self.FORMAT)       
        print(f"[NEW MESSAGE][{self.PORT1}][{addr}] {msg}")
        if(self.id_list.get(msg) == None):
            new_id_code = self.generate_code()
            while self.lock_list.locked():
                continue
            self.lock_list.acquire()
            self.id_list[msg] = new_id_code
            self.lock_list.release()
            conn.send(f"{new_id_code}".encode(self.FORMAT))
            print(f"[NEW USER] ID: {msg} added. Code: {new_id_code}")
        else:
            conn.send(f"ID {msg} already in use".encode(self.FORMAT))
        conn.close()

    # User authorization
    # Сhecks if the user ID matches the unique code and gets client message
    # Parameter conn - is a new socket object usable to send and receive data on the connection
    # Parameter addr - is the address bound to the socket on the other end of the connection
    # Raise NameError exception if user not authorized
    # Return value: string message received from user
    def authorize_user(self, conn, addr):
        user_id = conn.recv(self.MSG_LENGTH).decode(self.FORMAT)
        print(f"[NEW MESSAGE][{self.PORT2}][{addr}] {user_id}")
        if(self.id_list.get(user_id) == None):
            conn.send("Not authorized".encode(self.FORMAT))
            raise NameError("Not authorized")
        else:
            conn.send("OK".encode(self.FORMAT))

        user_code = conn.recv(self.MSG_LENGTH).decode(self.FORMAT)
        print(f"[NEW MESSAGE][{self.PORT2}][{addr}] {user_code}")
        if(self.id_list.get(user_id) != user_code):
            conn.send("Not authorized".encode(self.FORMAT))
            raise NameError("Not authorized")
        else:
            conn.send("OK".encode(self.FORMAT))

        print(f"[AUTHORIZED] ID: {user_id}, Code: {user_code}")
        return conn.recv(self.MSG_LENGTH).decode(self.FORMAT)

    # Used to receive and write message from user to a log file
    # Parameter conn - is a new socket object usable to send and receive data on the connection
    # Parameter addr - is the address bound to the socket on the other end of the connection
    def log_user_message(self, conn, addr):
        try:
            msg = self.authorize_user(conn, addr)
            print(f"[Message acquired] {msg}")
        except NameError:
            print("[NOT AUTHORIZED]")
            return
        try:
            while self.lock_file.locked():
                continue
            self.lock_file.acquire()
            f = open("log.txt", "a")
            f.write(f"{datetime.now()} {msg}\n")
            f.close()
            self.lock_file.release()
        except Exception as e:
            print(e)

    # Socket listener located on PORT1. Used to accept new clients and start registration
    def listener8000(self):
        self.server1.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER} port: {self.PORT1}")
        while True:
            try:
                conn, addr = self.server1.accept()
            except OSError:
                print("[SHUTDOWN] listener8000")
                break
            except Exception as e:
                print(f"[ERROR] listener8000 {e}")
                continue
                
            thread = threading.Thread(target=self.register_user, args=(conn, addr))
            thread.start()
            print(f"[USER CONNECTED][{self.PORT1}] User: {addr}")

    # Socket listener located on PORT2. Used recieve and logging messages from clients
    def listener8001(self):
        self.server2.listen()
        print(f"[LISTENING] Server is listening on {self.SERVER} port: {self.PORT2}")
        while True:
            try:
                conn, addr = self.server2.accept()
            except OSError:
                print("[SHUTDOWN] listener8001")
                break
            except Exception as e:
                print(f"[ERROR] listener8001 {e}")
                continue

            thread = threading.Thread(target=self.log_user_message, args=(conn, addr))
            thread.start()
            print(f"[USER CONNECTED][{self.PORT2}] User: {addr}")

    # Main method is used to start both listeners 
    def start_server(self):
        try:
            f = open("log.txt", "x")
        except FileExistsError:
            pass

        print("[STARTING] Server is starting...")
        self.main_thread_1 = threading.Thread(target=self.listener8000)
        self.main_thread_2 = threading.Thread(target=self.listener8001)

        self.server1 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server2 = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server1.bind((self.SERVER, self.PORT1))
        self.server2.bind((self.SERVER, self.PORT2))

        print("[STARTING] listener8000 is starting...")
        self.main_thread_1.start()
        print("[STARTING] listener8001 is starting...")
        self.main_thread_2.start()

    # Server shutdown
    # Turns off both listeners 
    def shutdown_server(self):
        self.server1.close()
        self.server2.close()

        self.main_thread_1.join()
        self.main_thread_2.join()
        print("[OFF]")
