import pygame
import os
import time


class Direction:
    """Định nghĩa các hướng di chuyển"""
    NORTH = 'North'
    SOUTH = 'South'
    EAST = 'East'
    WEST = 'West'
    STOP = 'Stop'
    _directions = {NORTH: (0, -1),
                   SOUTH: (0, 1),
                   EAST:  (1, 0),
                   WEST:  (-1, 0),
                   STOP:  (0, 0)}


class PacmanAnimation:
    """Xử lý hoạt ảnh Pacman"""
    FRAME_SIZE = (25, 25)  # Kích thước của mỗi khung hình
    FRAME_REPEAT = 1  # Số lần lặp lại mỗi khung hình
    ANIMATION_SPEED = 0.05  # Thời gian giữa các lần cập nhật

    def __init__(self):
        self.images = self.load_images()
        self.animation_frames = self.create_animation_frames()
        self.current_frame = 0
        self.last_update = 0

    def load_images(self):
        """Tải tất cả hình ảnh Pacman"""
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.normpath(os.path.join(base_dir, "..", "assets", "pacman_images"))
        return [
            pygame.transform.scale(
                pygame.image.load(os.path.join(images_dir, f"{i}.png")), 
                self.FRAME_SIZE
            ) 
            for i in range(1, 5)
        ]

    def create_animation_frames(self):
        """Tạo danh sách các khung hình animation"""
        return [img for img in self.images for _ in range(self.FRAME_REPEAT)]

    def get_current_frame(self, current_time, direction):
        """Trả về khung hình hiện tại"""
        if current_time - self.last_update >= self.ANIMATION_SPEED:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.last_update = current_time
        return self.rotate_image(self.animation_frames[self.current_frame], direction)

    def rotate_image(self, image, direction):
        """Xoay hình ảnh theo hướng di chuyển"""
        angles = {
            Direction.EAST: 0,
            Direction.NORTH: 90,
            Direction.WEST: 180,
            Direction.SOUTH: 270,
            Direction.STOP: 0
        }
        return pygame.transform.rotate(image, angles.get(direction, 0))


class Movement:
    """Xử lý di chuyển và interpolation"""
    def __init__(self):
        self.move_progress = 0
        self.last_pos = None
        self.current_pos = None
        self.teleport_target = None

    def update_position(self, new_pos, opposite_corners=None, allow_auto_teleport=True):
        """Cập nhật vị trí mới"""
        if self.current_pos != new_pos:
            self.last_pos = self.current_pos if self.current_pos else new_pos
            self.current_pos = new_pos
            self.move_progress = 0
            
            if allow_auto_teleport and opposite_corners and new_pos in opposite_corners:
                self.teleport_target = opposite_corners[new_pos]
            else:
                self.teleport_target = None

    def get_interpolated_position(self):
        """Tính toán vị trí nội suy"""
        if not self.last_pos or not self.current_pos:
            return self.current_pos

        if self.teleport_target:
            return self.teleport_target
        
        self.move_progress = min(1.0, self.move_progress + 0.1)
        
        x = self.last_pos[0] * (1 - self.move_progress) + self.current_pos[0] * self.move_progress
        y = self.last_pos[1] * (1 - self.move_progress) + self.current_pos[1] * self.move_progress
        return (x, y)


class GameVisualizer:
    """Engine hiển thị đồ họa game"""
    
    def __init__(self, width: int, height: int, cell_size: int = 30):
        self.width = width
        self.height = height
        self.cell_size = cell_size
        self.info_bar_height = 40
        
        # Khởi tạo animation và movement
        self.animation = PacmanAnimation()
        self.movement = Movement()
        
        # Tải ảnh ghost
        self.load_ghost_image()
        
        # Khởi tạo cửa sổ game
        self.screen = pygame.display.set_mode((width * cell_size, height * cell_size + self.info_bar_height))
        pygame.display.set_caption("Pacman Game")
        self.center_window()
    
    def load_ghost_image(self):
        """Tải ảnh ghost"""
        try:
            base_dir = os.path.dirname(os.path.abspath(__file__))
            ghost_path = os.path.normpath(os.path.join(base_dir, "..", "assets", "Ghost_image", "unnamed.png"))
            self.ghost_image = pygame.image.load(ghost_path)
            self.ghost_image = pygame.transform.scale(self.ghost_image, (self.cell_size - 6, self.cell_size - 6))
        except Exception:
            self.ghost_image = None
    
    def center_window(self):
        """Đặt cửa sổ ở giữa màn hình"""
        screen_info = pygame.display.Info()
        screen_width = screen_info.current_w
        screen_height = screen_info.current_h
        
        window_width = self.width * self.cell_size
        window_height = self.height * self.cell_size + self.info_bar_height
        
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        
        try:
            os.environ['SDL_VIDEO_WINDOW_POS'] = f'{x},{y}'
        except:
            pass
    
    def resize_window(self, new_width: int, new_height: int):
        """Thay đổi kích thước cửa sổ khi xoay mê cung"""
        self.width = new_width
        self.height = new_height
        
        # Tự động điều chỉnh cell_size dựa trên tỷ lệ
        if new_height > new_width:
            self.cell_size = 18  # Kích thước cho màn hình dọc
        else:
            self.cell_size = 30  # Kích thước bình thường cho màn hình ngang
        
        # Cập nhật kích thước ảnh ghost
        self.load_ghost_image()
        
        self.screen = pygame.display.set_mode((new_width * self.cell_size, new_height * self.cell_size + self.info_bar_height))
        print(f"Window resized to: {new_width}x{new_height} (cell_size: {self.cell_size})")
        self.center_window()

    def clear_screen(self):
        """Xóa màn hình và vẽ background"""
        maze_rect = pygame.Rect(0, self.info_bar_height, self.width * self.cell_size, self.height * self.cell_size)
        pygame.draw.rect(self.screen, (0, 0, 50), maze_rect)
        
        info_rect = pygame.Rect(0, 0, self.width * self.cell_size, self.info_bar_height)
        pygame.draw.rect(self.screen, (20, 20, 20), info_rect)

    def draw_cell(self, pos, color, radius=0, border=0):
        """Vẽ một ô trên màn hình"""
        x, y = pos
        screen_x = x * self.cell_size
        screen_y = y * self.cell_size + self.info_bar_height
        
        if radius > 0:
            pygame.draw.circle(self.screen, color, (screen_x + self.cell_size // 2, screen_y + self.cell_size // 2), radius, border)
        else:
            pygame.draw.rect(self.screen, color, (screen_x, screen_y, self.cell_size, self.cell_size), border)

    def draw_walls(self, walls, powered):
        """Vẽ tường"""
        color = (0, 0, 128) if powered else (0, 0, 255)
        
        for y in range(self.height):
            for x in range(self.width):
                if walls.get_at((x, y)) == (255, 255, 255):
                    self.draw_cell((x, y), color, border=1)

    def draw_food(self, food):
        """Vẽ thức ăn"""
        for y in range(self.height):
            for x in range(self.width):
                if food.get_at((x, y)) == (255, 255, 255):
                    self.draw_cell((x, y), (255, 255, 0), radius=4)

    def draw_magical_pies(self, magical_pies):
        """Vẽ bánh kỳ diệu"""
        for pos in magical_pies:
            self.draw_cell(pos, (255, 255, 255), radius=7)

    def draw_ghosts(self, ghosts):
        """Vẽ ma"""
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
        """Vẽ cổng thoát"""
        for pos in exit_gates:
            self.draw_cell(pos, (0, 255, 0), radius=8)

    def draw_pacman(self, pos, image, powered):
        """Vẽ Pacman"""
        x, y = pos
        
        # Scale Pacman theo cell_size hiện tại
        pacman_size = int(self.cell_size * 0.8)
        scaled_image = pygame.transform.scale(image, (pacman_size, pacman_size))
        
        screen_x = x * self.cell_size + (self.cell_size - scaled_image.get_width()) // 2
        screen_y = y * self.cell_size + (self.cell_size - scaled_image.get_height()) // 2 + self.info_bar_height
        
        # Vẽ vòng tròn trắng xung quanh Pacman nếu ở chế độ powered
        if powered:
            self.draw_cell((x, y), (255, 255, 255), radius=int(self.cell_size * 0.5), border=2)
        
        self.screen.blit(scaled_image, (screen_x, screen_y))
    
    def draw_step_counter(self, step_count, total_steps):
        """Hiển thị số bước ở giữa thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        center_x = (self.width * self.cell_size) // 2
        center_y = self.info_bar_height // 2
        
        step_text = f"Step: {step_count}"
        text_surface = font.render(step_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect(center=(center_x, center_y))
        
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)
        
        # Hiển thị cảnh báo khi gần đến lần xoay tiếp theo
        next_rotation = ((step_count // 30) + 1) * 30
        steps_to_rotation = next_rotation - step_count
        
        if steps_to_rotation <= 5 and steps_to_rotation > 0:
            warning_text = f"Rotation in {steps_to_rotation} steps!"
            warning_surface = font.render(warning_text, True, (255, 255, 0))
            warning_rect = warning_surface.get_rect(center=(center_x, center_y + 25))
            
            pygame.draw.rect(self.screen, (128, 0, 0), warning_rect.inflate(20, 10))
            self.screen.blit(warning_surface, warning_rect)
    
    def draw_score(self, score):
        """Hiển thị điểm số ở bên trái thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        left_x = 20
        center_y = self.info_bar_height // 2
        
        score_text = f"Score: {score}"
        text_surface = font.render(score_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (left_x + text_rect.width // 2, center_y)
        
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)
    
    def draw_position(self, pos):
        """Hiển thị vị trí ở bên phải thanh thông tin"""
        font = pygame.font.Font(None, 36)
        
        right_x = (self.width * self.cell_size) - 20
        center_y = self.info_bar_height // 2
        
        pos_text = f"Pos: ({int(pos[0])}, {int(pos[1])})"
        text_surface = font.render(pos_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (right_x - text_rect.width // 2, center_y)
        
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)
    
    def draw_step_count_only(self, step_count):
        """Hiển thị chỉ số bước ở bên phải thanh thông tin (chế độ thủ công)"""
        font = pygame.font.Font(None, 36)
        
        right_x = (self.width * self.cell_size) - 20
        center_y = self.info_bar_height // 2
        
        step_text = f"Steps: {step_count}"
        text_surface = font.render(step_text, True, (255, 255, 255))
        text_rect = text_surface.get_rect()
        text_rect.center = (right_x - text_rect.width // 2, center_y)
        
        pygame.draw.rect(self.screen, (0, 0, 0), text_rect.inflate(20, 10))
        self.screen.blit(text_surface, text_rect)

    def draw_win_message(self):
        """Vẽ thông báo thắng cuộc"""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        
        center_x = (self.width * self.cell_size) // 2
        center_y = (self.height * self.cell_size + self.info_bar_height) // 2
        
        # Vẽ background đen mờ
        overlay = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size + self.info_bar_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ thông báo thắng
        win_text = "YOU WIN!"
        win_surface = font_large.render(win_text, True, (0, 255, 0))
        win_rect = win_surface.get_rect(center=(center_x, center_y - 30))
        
        pygame.draw.rect(self.screen, (0, 100, 0), win_rect.inflate(40, 20))
        self.screen.blit(win_surface, win_rect)
        
        # Vẽ thông báo phụ
        congrats_text = "Congratulations!"
        congrats_surface = font_medium.render(congrats_text, True, (255, 255, 255))
        congrats_rect = congrats_surface.get_rect(center=(center_x, center_y + 20))
        self.screen.blit(congrats_surface, congrats_rect)

    def draw_game_over_message(self):
        """Vẽ thông báo thua cuộc"""
        font_large = pygame.font.Font(None, 72)
        font_medium = pygame.font.Font(None, 48)
        
        center_x = (self.width * self.cell_size) // 2
        center_y = (self.height * self.cell_size + self.info_bar_height) // 2
        
        # Vẽ background đen mờ
        overlay = pygame.Surface((self.width * self.cell_size, self.height * self.cell_size + self.info_bar_height))
        overlay.set_alpha(128)
        overlay.fill((0, 0, 0))
        self.screen.blit(overlay, (0, 0))
        
        # Vẽ thông báo thua
        game_over_text = "GAME OVER!"
        game_over_surface = font_large.render(game_over_text, True, (255, 0, 0))
        game_over_rect = game_over_surface.get_rect(center=(center_x, center_y - 30))
        
        pygame.draw.rect(self.screen, (100, 0, 0), game_over_rect.inflate(40, 20))
        self.screen.blit(game_over_surface, game_over_rect)
        
        # Vẽ thông báo phụ
        try_again_text = "Try Again!"
        try_again_surface = font_medium.render(try_again_text, True, (255, 255, 255))
        try_again_rect = try_again_surface.get_rect(center=(center_x, center_y + 20))
        self.screen.blit(try_again_surface, try_again_rect)

    def update_display(self):
        """Cập nhật màn hình"""
        pygame.display.flip()