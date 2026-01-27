import pygame
import numpy as np
import os

class MapEditor:
    def __init__(self):
        pygame.init()
        
        # Grid settings (must match server settings)
        self.CELL_SIZE = 20
        self.GRID_W = 40  # 800 / 20
        self.GRID_H = 30  # 600 / 20
        self.SCREEN_W = self.GRID_W * self.CELL_SIZE
        self.SCREEN_H = self.GRID_H * self.CELL_SIZE
        
        # Initialize collision map (1 = passable, 0 = obstacle)
        self.collision_map = np.ones((self.GRID_H, self.GRID_W), dtype=np.int32)
        
        # Create default ground
        self.collision_map[-1, :] = 0  # bottom row is solid
        
        self.screen = pygame.display.set_mode((self.SCREEN_W, self.SCREEN_H + 100))
        pygame.display.set_caption("PyTanks Map Editor")
        
        self.font = pygame.font.SysFont(None, 24)
        self.small_font = pygame.font.SysFont(None, 20)
        
        self.drawing = False
        self.erasing = False
        self.current_map_name = "default"
        
        self.run()
    
    def save_map(self, filename):
        """Save map to maps/ folder"""
        maps_dir = "maps"
        if not os.path.exists(maps_dir):
            os.makedirs(maps_dir)
        
        filepath = os.path.join(maps_dir, f"{filename}.npy")
        np.save(filepath, self.collision_map)
        print(f"Map saved: {filepath}")
        return filepath
    
    def load_map(self, filename):
        """Load map from maps/ folder"""
        filepath = os.path.join("maps", f"{filename}.npy")
        if os.path.exists(filepath):
            self.collision_map = np.load(filepath)
            self.current_map_name = filename
            print(f"Map loaded: {filepath}")
            return True
        else:
            print(f"Map not found: {filepath}")
            return False
    
    def get_available_maps(self):
        """Get list of available map files"""
        maps_dir = "maps"
        if not os.path.exists(maps_dir):
            return []
        
        map_files = []
        for file in os.listdir(maps_dir):
            if file.endswith(".npy"):
                map_files.append(file[:-4])  # Remove .npy extension
        return sorted(map_files)
    
    def clear_map(self):
        """Clear entire map"""
        self.collision_map = np.ones((self.GRID_H, self.GRID_W), dtype=np.int32)
        print("Map cleared")
    
    def fill_bottom(self):
        """Fill bottom row with obstacles (ground)"""
        self.collision_map[-1, :] = 0
        print("Bottom filled")
    
    def run(self):
        clock = pygame.time.Clock()
        running = True
        
        input_text = ""
        input_active = False
        input_mode = None  # 'save' or 'load'
        
        show_map_browser = False
        available_maps = []
        selected_map_index = 0
        
        while running:
            clock.tick(60)
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    my = event.pos[1]
                    # Check if click is in grid area
                    if my < self.SCREEN_H:
                        if event.button == 1:  # Left click - draw obstacles
                            self.drawing = True
                        elif event.button == 3:  # Right click - erase obstacles
                            self.erasing = True
                
                elif event.type == pygame.MOUSEBUTTONUP:
                    self.drawing = False
                    self.erasing = False
                
                elif event.type == pygame.KEYDOWN:
                    if show_map_browser:
                        # Handle map browser navigation
                        if event.key == pygame.K_ESCAPE:
                            show_map_browser = False
                        elif event.key == pygame.K_UP and selected_map_index > 0:
                            selected_map_index -= 1
                        elif event.key == pygame.K_DOWN and selected_map_index < len(available_maps) - 1:
                            selected_map_index += 1
                        elif event.key == pygame.K_RETURN and available_maps:
                            self.load_map(available_maps[selected_map_index])
                            show_map_browser = False
                    elif input_active:
                        # Handle text input
                        if event.key == pygame.K_RETURN:
                            if input_mode == 'save':
                                self.save_map(input_text if input_text else "default")
                            elif input_mode == 'load':
                                self.load_map(input_text if input_text else "default")
                            input_active = False
                            input_text = ""
                            input_mode = None
                        elif event.key == pygame.K_ESCAPE:
                            input_active = False
                            input_text = ""
                            input_mode = None
                        elif event.key == pygame.K_BACKSPACE:
                            input_text = input_text[:-1]
                        else:
                            # Allow alphanumeric and underscore
                            if event.unicode.isalnum() or event.unicode == '_':
                                input_text += event.unicode
                    else:
                        # Handle commands
                        if event.key == pygame.K_s:  # Save
                            input_active = True
                            input_mode = 'save'
                            input_text = self.current_map_name
                        elif event.key == pygame.K_l:  # Load
                            input_active = True
                            input_mode = 'load'
                            input_text = ""
                        elif event.key == pygame.K_c:  # Clear map
                            self.clear_map()
                        elif event.key == pygame.K_g:  # Add ground
                            self.fill_bottom()
                        elif event.key == pygame.K_q:  # Quit
                            running = False
            
            # Draw/erase with mouse
            if self.drawing or self.erasing:
                mx, my = pygame.mouse.get_pos()
                if my < self.SCREEN_H:  # Only draw in grid area
                    gx = mx // self.CELL_SIZE
                    gy = my // self.CELL_SIZE
                    if 0 <= gx < self.GRID_W and 0 <= gy < self.GRID_H:
                        self.collision_map[gy, gx] = 0 if self.drawing else 1
            
            # Render
            self.render(input_active, input_mode, input_text, show_map_browser, available_maps, selected_map_index)
        
        pygame.quit()
    
    def render(self, input_active, input_mode, input_text, show_map_browser, available_maps, selected_map_index):
        # Clear screen
        self.screen.fill((30, 30, 30))
        
        # Draw grid
        for gy in range(self.GRID_H):
            for gx in range(self.GRID_W):
                x = gx * self.CELL_SIZE
                y = gy * self.CELL_SIZE
                
                # Color based on cell type
                if self.collision_map[gy, gx] == 0:
                    color = (100, 100, 100)  # Obstacle (gray)
                else:
                    color = (40, 40, 40)  # Passable (dark)
                
                pygame.draw.rect(self.screen, color, (x, y, self.CELL_SIZE, self.CELL_SIZE))
                pygame.draw.rect(self.screen, (60, 60, 60), (x, y, self.CELL_SIZE, self.CELL_SIZE), 1)
        
        # Draw UI panel at bottom
        panel_y = self.SCREEN_H
        pygame.draw.rect(self.screen, (50, 50, 50), (0, panel_y, self.SCREEN_W, 100))
        
        # Instructions
        instructions = [
            "LEFT CLICK: Draw obstacles | RIGHT CLICK: Erase | S: Save | L: Load | B: Browse maps",
            "C: Clear map | G: Add ground | Q: Quit",
            f"Current map: {self.current_map_name}"
        ]
        
        for i, text in enumerate(instructions):
            surf = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (10, panel_y + 10 + i * 25))
        
        # Map browser
        if show_map_browser:
            browser_w = 400
            browser_h = 400
            browser_x = (self.SCREEN_W - browser_w) // 2
            browser_y = (self.SCREEN_H - browser_h) // 2
            
            pygame.draw.rect(self.screen, (60, 60, 60), (browser_x, browser_y, browser_w, browser_h))
            pygame.draw.rect(self.screen, (255, 255, 255), (browser_x, browser_y, browser_w, browser_h), 2)
            
            title_surf = self.font.render("Available Maps (Use UP/DOWN, ENTER to load, ESC to cancel)", True, (255, 255, 0))
            self.screen.blit(title_surf, (browser_x + 10, browser_y + 10))
            
            if not available_maps:
                no_maps_surf = self.font.render("No maps found in maps/ folder", True, (255, 100, 100))
                self.screen.blit(no_maps_surf, (browser_x + 50, browser_y + 50))
            else:
                list_y = browser_y + 50
                visible_count = 12
                start_index = max(0, selected_map_index - visible_count // 2)
                end_index = min(len(available_maps), start_index + visible_count)
                
                for i in range(start_index, end_index):
                    map_name = available_maps[i]
                    if i == selected_map_index:
                        pygame.draw.rect(self.screen, (100, 100, 150), (browser_x + 10, list_y, browser_w - 20, 25))
                        color = (255, 255, 255)
                    else:
                        color = (200, 200, 200)
                    
                    map_surf = self.small_font.render(f"{i+1}. {map_name}", True, color)
                    self.screen.blit(map_surf, (browser_x + 20, list_y + 5))
                    list_y += 28
        
        for i, text in enumerate(instructions):
            surf = self.small_font.render(text, True, (255, 255, 255))
            self.screen.blit(surf, (10, panel_y + 10 + i * 25))
        
        # Input box
        if input_active:
            prompt = "Enter filename to save: " if input_mode == 'save' else "Enter filename to load: "
            prompt_surf = self.font.render(prompt, True, (255, 255, 0))
            input_surf = self.font.render(input_text + "_", True, (255, 255, 255))
            
            box_y = self.SCREEN_H // 2 - 40
            pygame.draw.rect(self.screen, (80, 80, 80), (50, box_y, self.SCREEN_W - 100, 80))
            pygame.draw.rect(self.screen, (255, 255, 255), (50, box_y, self.SCREEN_W - 100, 80), 2)
            
            self.screen.blit(prompt_surf, (60, box_y + 10))
            self.screen.blit(input_surf, (60, box_y + 40))
        
        pygame.display.flip()


if __name__ == "__main__":
    editor = MapEditor()
