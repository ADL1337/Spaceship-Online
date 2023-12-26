import socket
import threading

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

SERVER = socket.gethostbyname(socket.gethostname())
PORT = 5080
FORMAT = 'utf-8'
DISCONNECT_MESSAGE = "!bye"

try:
    s.bind((SERVER, PORT))

except socket.error as e:
    print(str(e))

s.listen(2)
print("[WAITING] Waiting for a connection...")

available_ids = ["0", "1"] # store available ids
current_id = 0 # store current id
positions = ["", ""] # store positions
healths = ["", ""] # store healths
bullets = ["", ""] # store bullets

def update_data(data):
    """Update player data and return id of updated player."""

    global positions, healths, bullets
    elem = data.split(";") # separating data
    id = int(elem[0]) # getting id
    positions[id] = elem[1] # updating position
    healths[id] = elem[2] # updating health
    bullets[id] = elem[3] # updating bullets
    return id

def format_data(id):
    """Format data to send to client."""

    global positions, healths, bullets
    return f"{id};{positions[id]};{healths[id]};{bullets[id]}"

def threaded_client(conn, addr):
    """Handle client connection."""

    global current_id, positions
    id = available_ids[current_id%2] # getting id
    conn.send(id.encode()) # sending id
    print(f"[ASSIGN] Assigned ID \"{id}\" to {addr}.")
    current_id += 1
    reply = ''

    while True:
        if current_id >= 2:
            try:
                data = conn.recv(1024) # receiving data
                reply = data.decode(FORMAT) # decoding data
                if not data: # checking if data is empty
                    conn.send("Goodbye".encode(FORMAT)) # sending goodbye message
                    break
                else:
                    print("[INPUT] Received: " + reply)
                    id = update_data(reply) # updating data and getting id

                    # getting other player's id
                    if id == 0: nid = 1 
                    if id == 1: nid = 0

                    reply = format_data(nid) # formatting reply
                    print("[REPLY] Sending: " + reply)
                    conn.sendall(reply.encode(FORMAT))
            except:
                break
    current_id -= 1
    print(f"[DISCONNECT] {addr}: \"{id}\" has disconnected.")
    conn.close() # closing connection

while True: # accepting connections
    conn, addr = s.accept()
    print("[NEW CONNECTION] Connected to: ", addr)
    if threading.active_count() < 3: # checking if there are less than 2 connections
        thread = threading.Thread(target=threaded_client, args=(conn, addr))
        thread.start()