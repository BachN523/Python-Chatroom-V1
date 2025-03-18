"""
Bach Nguyen 3-14-2025
A client-side program for a simple chat room application.

    Commands
    - To connect to an active Server.py instance on the console: python Client.py 127.0.0.1
    - -> If Server.py is not running locally, replace 127.0.0.1 with its valid IPv4 address 
    
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

# Tried adapting the \C skeletons demo as a starting point
import socket
import sys

SERVER_PORT = 16043  # 1 plus the last four digits of your student ID
MAX_LINE = 256 # message max character size

def get_ip_address(host):
    try:
        # If the user input is an alpha name for the host, use gethostbyname()
        # If not, get host by addr (assume IPv4)
        socket.inet_aton(host)
        return host
    except socket.error:
        try:
            return socket.gethostbyname(host)
        except socket.gaierror:
            print("Host not found")
            return None

def validate_user_id(user_id):
    return len(user_id) >= 3 and len(user_id) <= 32 and ' ' not in user_id

def validate_password(password):
    return len(password) >= 4 and len(password) <= 8 and ' ' not in password

def validate_message(message):
    return len(message) >= 1 and len(message) <= MAX_LINE

def send_receive(sock, message): # I mean I don't have to do encoding but its this basic on the socket interface
    sock.sendall(message.encode())
    return sock.recv(MAX_LINE).decode().strip()

def main():
    if len(sys.argv) < 2:
        print("\nUsage: client serverName")
        return

    server_name = sys.argv[1]
    ip_address = get_ip_address(server_name)
    if not ip_address:
        return

    print("My chat room client. Version One.")

    try:
        # Create a socket.
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # Connect to a server.
        s.connect((ip_address, SERVER_PORT))
    except socket.error as e:
        print(f"Failed to connect: {e}")
        return

    logged_in = False
    user_id = None

    while True:
        try:
            cmd = input("> ").strip()
            if not cmd:
                continue

            if cmd.startswith("newuser"):
                if logged_in:
                    print("> You are already logged in.")
                    continue
                
                # Format: newuser [userID] [password]
                parts = cmd.split()
                if len(parts) != 3:
                    print("> Invalid format. Usage: newuser [userID] [password]")
                    continue
                
                _, user_id, password = parts
                if validate_user_id(user_id) and validate_password(password):
                    response = send_receive(s, cmd)
                    print(f"> {response}")
                else:
                    print("> Invalid UserID or Password format.")

            elif cmd.startswith("login"):
                if logged_in:
                    print("> You are already logged in.")
                    continue
                
                # Format: login [userID] [password]
                parts = cmd.split()
                if len(parts) != 3:
                    print("> Invalid format. Usage: login [userID] [password]")
                    continue
                
                _, user_id, password = parts
                if validate_user_id(user_id) and validate_password(password):
                    response = send_receive(s, cmd)
                    print(f"> {response}")
                    if "login confirmed" in response:
                        logged_in = True
                else:
                    print("> Invalid UserID or Password format.")

            elif cmd.startswith("send"):
                if not logged_in:
                    print("> Denied. Please login first.")
                    continue
                
                # Format: send [message]
                message = cmd[4:].strip()
                if validate_message(message):
                    response = send_receive(s, cmd)
                    print(f"> {response}")
                else:
                    print("> Invalid message length.")

            elif cmd == "logout":
                if logged_in:
                    response = send_receive(s, cmd)
                    print(f"> {response}")
                    logged_in = False
                    break
                else:
                    print("> You are not logged in.") # Edge case uncovered in the Rubric

            else:
                print("> Invalid command.")

        except (KeyboardInterrupt, EOFError):
            print("\nClosing connection...") # Edge case uncovered in the Rubric
            s.close()
            break

    s.close()

if __name__ == "__main__":
    main()
