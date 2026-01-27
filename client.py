import socket
import numpy as np

class Network:
    def __init__(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # default to localhost for local testing
        self.host = "10.7.243.89"
        self.port = 5555
        self.addr = (self.host, self.port)

    def connect(self, name):
        self.client.connect(self.addr)

        # inform server of username
        self.client.send(str.encode(name))

        # receive user ID from server
        val = self.client.recv(8)
        player_id = int(val.decode())
        
        # receive collision map info
        map_info_bytes = self.client.recv(12)  # 3 int32s
        map_info = np.frombuffer(map_info_bytes, dtype=np.int32)
        self.grid_w, self.grid_h, self.grid_size = map_info
        
        # receive collision map data
        map_size = self.grid_w * self.grid_h * 4  # int32 = 4 bytes
        map_bytes = bytes()
        while len(map_bytes) < map_size:
            map_bytes += self.client.recv(4096)
        self.collision_map = np.frombuffer(map_bytes[:map_size], dtype=np.int32).reshape((self.grid_h, self.grid_w))
        
        return player_id 

    def disconnect(self):
        self.client.close()
    
    def get_collision_map(self):
        """Return the collision map and grid info"""
        return self.collision_map, self.grid_w, self.grid_h, self.grid_size

    def send(self, keyboard_input):
        try:
            client_msg = keyboard_input.tobytes()
            self.client.send(client_msg)
            reply = bytes()
            # expect 48 rows * 10 columns * 8 bytes per float64 = 3840 bytes
            while len(reply) < 3840:
                reply += self.client.recv(1024)
            game_world = np.frombuffer(reply, dtype=np.float64).reshape((48, 10))
            return game_world
        except socket.error as e:
            print(e)

