import pygame


class GameRenderer:
    def __init__(self, width: int, height: int, cell_size: int = 30):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.info_bar_height = 60  # Chiều cao thanh thông tin
        # Tải ảnh ghost
        try:
            import os
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ghost_path = os.path.normpath(os.path.join(base_dir, "..", "assets", "Ghost_image", "unnamed.png"))
            self.ghost_image = pygame.image.load(ghost_path)
            self.ghost_image = pygame.transform.scale(self.ghost_image, (self.cell_size - 6, self.cell_size - 6))
        except Exception:
            self.ghost_image = None
        
        # Khởi tạo cửa sổ game với kích thước phù hợp + thanh thông tin
        self.screen = pygame.display.set_mode((width * cell_size, height * cell_size + self.info_bar_height))
        pygame.display.set_caption("Pacman Game")
    
    def resize_window(self, new_width: int, new_height: int):
        """Thay đổi kích thước cửa sổ khi xoay mê cung"""
        self.width = new_width
        self.height = new_height
        self.screen = pygame.display.set_mode((new_width * self.cell_size, new_height * self.cell_size + self.info_bar_height))
        print(f"Window resized to: {new_width}x{new_height}")

    def clear_screen(self):
        # Vẽ background cho mê cung
        maze_rect = pygame.Rect(0, self.info_bar_height, self.width * self.cell_size, self.height * self.cell_size)
        pygame.draw.rect(self.screen, (0, 0, 50), maze_rect)
        
        # Vẽ thanh thông tin phía trên
        info_rect = pygame.Rect(0, 0, self.width * self.cell_size, self.info_bar_height)
        pygame.draw.rect(self.screen, (20, 20, 20), info_rect)  # Màu xám đậm cho thanh thông tin

    def draw_cell(self, pos, color, radius=0, border=0):
        x, y = pos
        screen_x = x * self.cell_size
        screen_y = y * self.cell_size + self.info_bar_height  # Điều chỉnh vị trí để không che thanh thông tin
        
        # Nếu có radius, vẽ hình tròn, nếu không vẽ hình chữ nhật.
        if radius > 0:
            pygame.draw.circle(self.screen, color, (screen_x + self.cell_size // 2, screen_y + self.cell_size // 2), radius, border)
        else:
            pygame.draw.rect(self.screen, color, (screen_x, screen_y, self.cell_size, self.cell_size), border)

    def draw_walls(self, walls, powered):
        color = (0, 0, 128) if powered else (0, 0, 255)
        
        # Lặp qua tất cả các ô trên bản đồ và vẽ tường.
        for y in range(self.height):
            for x in range(self.width):
                if walls.get_at((x, y)) == (255, 255, 255):  # Kiểm tra tường (màu trắng).
                    self.draw_cell((x, y), color, border=1)

    def draw_food(self, food):
        for y in range(self.height):
            for x in range(self.width):
                if food.get_at((x, y)) == (255, 255, 255):  # Kiểm tra thức ăn (màu trắng).
                    self.draw_cell((x, y), (255, 255, 0), radius=4)

    def draw_magical_pies(self, magical_pies):
        for pos in magical_pies:
            self.draw_cell(pos, (255, 255, 255), radius=7)

    def draw_ghosts(self, ghosts):
        for ghost in ghosts:
            pos = ghost.getPosition()
            x, y = pos
            screen_x = x * self.cell_size + 3
            screen_y = y * self.cell_size + self.info_bar_height + 3
            if self.ghost_image:
                self.screen.blit(self.ghost_image, (screen_x, screen_y))
            else:
                self.draw_cell(pos, (255, 0, 0), radius=6)

    def draw_exit_gates(self, exit_gates):
        for pos in exit_gates:
            self.draw_cell(pos, (0, 255, 0), radius=8)  # Màu xanh lá cho Exit Gates

    def draw_pacman(self, pos, image, powered):
        x, y = pos
        screen_x = x * self.cell_size + (self.cell_size - image.get_width()) // 2
        screen_y = y * self.cell_size + (self.cell_size - image.get_height()) // 2 + self.info_bar_height
        
        # Vẽ vòng tròn trắng xung quanh Pacman nếu ở chế độ powered.
        if powered:
            self.draw_cell((x, y), (255, 255, 255), radius=15, border=2)
        
        # Vẽ hình ảnh Pacman tại vị trí đã tính toán.
        self.screen.blit(image, (screen_x, screen_y))
    
    def draw_step_counter(self, step_count, total_steps):
        """Hiển thị số bước ở giữa thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        # Tính toán vị trí giữa thanh thông tin
        center_x = (self.width * self.cell_size) // 2
        center_y = self.info_bar_height // 2
        
        # Tạo text
        step_text = f"Step: {step_count}/{total_steps}"
        text_surface = font.render(step_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        
        # Vẽ background đen cho text
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        
        # Vẽ text
        self.screen.blit(text_surface, text_rect)
        
        # Hiển thị cảnh báo khi gần đến lần xoay tiếp theo
        next_rotation = ((step_count // 30) + 1) * 30
        steps_to_rotation = next_rotation - step_count
        
        if steps_to_rotation <= 5 and steps_to_rotation > 0:
            warning_text = f"Rotation in {steps_to_rotation} steps!"
            warning_surface = font.render(warning_text, True, (255, 255, 0))
            warning_rect = warning_surface.get_rect(center=(center_x, center_y + 25))
            
            # Vẽ background đỏ cho cảnh báo
            pygame.draw.rect(self.screen, (128, 0, 0), warning_rect.inflate(20, 10))
            self.screen.blit(warning_surface, warning_rect)
    
    def draw_score(self, score):
        """Hiển thị điểm số ở bên trái thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        # Vị trí bên trái thanh thông tin
        left_x = 20
        center_y = self.info_bar_height // 2
        
        # Tạo text
        score_text = f"Score: {score}"
        text_surface = font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (left_x + text_rect.width // 2, center_y)
        
        # Vẽ background đen cho text
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        
        # Vẽ text
        self.screen.blit(text_surface, text_rect)
    
    def draw_position(self, pos):
        """Hiển thị vị trí ở bên phải thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        # Vị trí bên phải thanh thông tin
        right_x = (self.width * self.cell_size) - 20
        center_y = self.info_bar_height // 2
        
        # Tạo text
        pos_text = f"Pos: ({int(pos[0])}, {int(pos[1])})"
        text_surface = font.render(pos_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (right_x - text_rect.width // 2, center_y)
        
        # Vẽ background đen cho text
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        
        # Vẽ text
        self.screen.blit(text_surface, text_rect)

    def update_display(self):
        pygame.display.flip()