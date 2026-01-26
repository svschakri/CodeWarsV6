import pygame
import numpy as np
from client import Network
import time

class PlayerClient:
    def __init__(self, W=800, H=600):
        self.screen = pygame.display.set_mode((W, H))
        pygame.display.set_caption("PyTanks")

        self.get_player_name()
        self.join_server()
        self.run_game()
        self.quit_game()

    def get_player_name(self):
        self.name = ""
        while not (0 < len(self.name) < 20):
            self.name = input("Please enter your name: ")

    def join_server(self):
        self.server = Network()
        self.ID = self.server.connect(self.name)
        self.collision_map, self.grid_w, self.grid_h, self.grid_size = self.server.get_collision_map()
        self.running = True
        print("Connected to server, player ID:", self.ID)

    def run_game(self):
        clock = pygame.time.Clock()
        while self.running:
            clock.tick(30)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            # [W=jetpack, A=left, D=right, UP=aim up, DOWN=aim down, LEFT=aim left, RIGHT=aim right, SPACE=shoot]
            keyboard_input = np.zeros(8, dtype=bool)
            keys = pygame.key.get_pressed()
            if keys[pygame.K_w]:  # W for jetpack
                keyboard_input[0] = 1
            if keys[pygame.K_a]:  # A to move left
                keyboard_input[1] = 1
            if keys[pygame.K_d]:  # D to move right
                keyboard_input[2] = 1
            if keys[pygame.K_UP]:  # Up arrow for aim up
                keyboard_input[3] = 1
            if keys[pygame.K_DOWN]:  # Down arrow for aim down
                keyboard_input[4] = 1
            if keys[pygame.K_LEFT]:  # Left arrow for aim left
                keyboard_input[5] = 1
            if keys[pygame.K_RIGHT]:  # Right arrow for aim right
                keyboard_input[6] = 1
            if keys[pygame.K_SPACE]:  # Space to shoot
                keyboard_input[7] = 1
            if keys[pygame.K_ESCAPE]:
                self.running = False

            game_world = self.server.send(keyboard_input)
            self.render(game_world)

    def render(self, game_world):
        self.screen.fill((0,0,0))
        
        # Draw collision map obstacles (brown/gray blocks)
        for gy in range(self.grid_h):
            for gx in range(self.grid_w):
                if self.collision_map[gy, gx] == 0:  # obstacle
                    x = gx * self.grid_size
                    y = gy * self.grid_size
                    pygame.draw.rect(self.screen, (100, 100, 100), (x, y, self.grid_size, self.grid_size))
                    # Add border for visibility
                    pygame.draw.rect(self.screen, (70, 70, 70), (x, y, self.grid_size, self.grid_size), 1)
        
        for i in range(8):
            if game_world[i, 0] == 0:
                continue

            color = (255, 0, 0)
            if i == self.ID:
                    color = (0, 0, 255)
            # Draw player circle
            pygame.draw.circle(self.screen, color, (int(game_world[i, 1]), int(game_world[i, 2])), 25)
            # Draw aim direction line
            pygame.draw.line(self.screen, (0, 255, 0), ((int(game_world[i, 1]), int(game_world[i, 2]))), ((int(game_world[i, 1] + 25*np.cos(game_world[i, 3])), int(game_world[i, 2] + 25*np.sin(game_world[i, 3])))), 2)
            
            # Draw jetpack indicator (orange dot below player when fuel is being used)
            # If fuel is decreasing (not at max), show jetpack is active
            fuel = game_world[i, 6]
            if fuel < 99.9:  # jetpack was used recently
                pygame.draw.circle(self.screen, (255, 165, 0), (int(game_world[i, 1]), int(game_world[i, 2] + 35)), 5)
        
        # Draw fuel meter for local player
        if game_world[self.ID, 0] == 1:
            fuel = game_world[self.ID, 6]
            fuel_percent = fuel / 100.0
            # Draw fuel bar in top-left corner
            bar_x, bar_y = 10, 10
            bar_width, bar_height = 200, 20
            # Background (empty)
            pygame.draw.rect(self.screen, (50, 50, 50), (bar_x, bar_y, bar_width, bar_height))
            # Fuel level (cyan color like Mini Militia)
            fuel_width = int(bar_width * fuel_percent)
            pygame.draw.rect(self.screen, (0, 255, 255), (bar_x, bar_y, fuel_width, bar_height))
            # Border
            pygame.draw.rect(self.screen, (255, 255, 255), (bar_x, bar_y, bar_width, bar_height), 2)
        
        # Draw bullets
        for i in range(8, 48):
            if game_world[i, 0] == 0:
                continue
            pygame.draw.circle(self.screen, (255, 255, 255), (int(game_world[i, 1]), int(game_world[i, 2])), 2)

        pygame.display.update()


    def quit_game(self):
        self.server.disconnect()
        pygame.quit()
        quit()
	

if __name__ == "__main__":
    pygame.init()
    player_client = PlayerClient()
