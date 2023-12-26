import socket

class Network:
    """Represents a network connection."""

    MAX_SIZE = 1024
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.host = "" # Insert the server IP address here (eg. "192.168.1.1")
        self.port = 5080
        self.addr = (self.host, self.port)
        self.id = self.connect()

    def connect(self):
        """Establish a connection with the server and return the id."""
        self.client.connect(self.addr)
        return self.client.recv(self.MAX_SIZE).decode()

    def send(self, data):
        """Send data to the server and return the reply."""
        
        try:
            self.client.send(str.encode(data))
            reply = self.client.recv(self.MAX_SIZE).decode()
            return reply
        except socket.error as e:
            return str(e)