"""
Bach Nguyen 3-14-2025
A server-side program for a simple chat room application.

    Commands
    - To run a Server.py instance on the console: python Server.py
    - > Open the server to listen for incoming connections 
    - > Clients should be mindful of the IPv4 address if not ran locally
    
    - login UserID Password
    - -> Client.py: input validation -> sends command to server 
    - -> Server.py: verify UserID & Password -> confirm or decline login -> send message about result to client
    
    - newuser UserID Password
    - -> Note: Character limit for UserID is 3-32 and for Password 4-8. Both are case-sensitive and should not contain spaces.
    - -> Client.py: input validation -> sends command to Server
    - -> Server.py: reject if UserID already there. Users' IDs and passwords are kept in users.txt

    - send message
    - -> Note: Message size can be between 1 and 256 characters
    - -> Server.py: send "message" to the server 
    - -> Client.py: precede the message with the UserID and send it back

    - logout
    - -> Note: The connection between the server and client will be closed.
    - -> Client.py: Logout from the chat room. The client should exit.
    - -> Server.py: The server should continue running and allow other clients to connect.
"""

# Well, I don't need to explicitly use Windows-specific functions like in ~\C skeletons
# Exception handling will be used instead of return values
# 
import socket
import sys

SERVER_PORT = 16043  # 1 plus the last four digits of my student ID
MAX_PENDING = 5 # number of connections that the server will connect
MAX_LINE = 256 # message max character size

"""Returns {user_id : password} pairs"""
def load_users(filename):
    users = {}
    try:
        with open(filename, 'r') as file:
            for line in file:
                # Remove parentheses and split by comma
                user_id, password = line.strip()[1:-1].split(', ')
                users[user_id] = password
    except FileNotFoundError:
        pass
    return users

"""Writes in (user_id : password) pairs"""
def save_users(filename, users):
    with open(filename, 'w') as file:
        for user_id, password in users.items():
            file.write(f"({user_id}, {password})\n")

def main():
    users = load_users('users.txt')
    # Print(users)
    logged_in_users = {}

    print("My chat room server. Version One.")

    """s: Socket object (see documentation for python socket Library)"""
    try:
        # Create an INET, STREAMing socket
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Bind the socket to this Port
        s.bind(('', SERVER_PORT))
        # Listen on the Socket.
        s.listen(MAX_PENDING)
    except socket.error as e:
        print(f"Error setting up server: {e}")
        sys.exit(1)

    # print("Waiting for a client to connect...")
    while True:
        try:
            # Accept connections.
            conn, addr = s.accept()
            # print("Client Connected.")
            
            # Handle client requests.
            while True:
                data = conn.recv(MAX_LINE)
                if not data:
                    break
                command = data.decode().strip()
                
                if command.startswith("newuser"): # newuser UserID Password
                    _, user_id, password = command.split()
                    user_id = user_id.strip()
                    password = password.strip()

                    if user_id not in users:
                        users[user_id] = password
                        save_users('users.txt', users)
                        conn.sendall("New user account created. Please login.".encode())
                        print("New user account created.")
                    else:
                        conn.sendall("Denied. User account already exists.".encode())


                elif command.startswith("login"): # login UserID Password
                    _, user_id, password = command.split()
                    user_id = user_id.strip()
                    password = password.strip()

                    if user_id in users and users[user_id] == password:
                        logged_in_users[conn] = user_id
                        conn.sendall("login confirmed".encode())
                        print(f"{user_id} login.")
                    else:
                        conn.sendall("Denied. User name or password incorrect.".encode())

                        
                elif command.startswith("send"): # send message
                    _, message = command.split(maxsplit=1)
                    user_id = logged_in_users.get(conn)
                    if user_id:
                        response = f"{user_id}: {message}"
                        conn.sendall(response.encode())
                        print(response)
                    else:
                        conn.sendall("Denied. Please login first.".encode())
                        
                        
                elif command.startswith("logout"): # logout
                    user_id = logged_in_users.get(conn)
                    if user_id:
                        del logged_in_users[conn]
                        conn.sendall(f"{user_id} left.".encode())
                        print(f"{user_id} logout.")
                        break
                    else:
                        conn.sendall("Denied. You are not logged in.".encode()) # Edge case uncovered in the Rubric

                    
                else:
                    conn.sendall("Invalid command.".encode())
                    
            conn.close()
            # print("Client Closed.")
        except socket.error as e:
            print(f"Error in connection: {e}")
        finally:
            pass

    s.close()

if __name__ == "__main__":
    main()
