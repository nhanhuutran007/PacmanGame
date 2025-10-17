import pygame
import os
import time
from visualize import GameVisualizer, PacmanAnimation, Movement, Direction
from base_pacman import Ghost

class Layout:
    def __init__(self, layoutData):
        # Khởi tạo pygame và các thuộc tính của Layout.
        pygame.init()
        
        # Đảm bảo tất cả các dòng có cùng độ dài
        max_width = max(len(line) for line in layoutData)
        layoutData = [line.ljust(max_width) for line in layoutData]
        
        self.width = len(layoutData[0])  # Chiều rộng của layout (số cột).
        self.height = len(layoutData)  # Chiều cao của layout (số hàng).
        
        # Khởi tạo các điểm cổng dịch chuyển (opposite corners).
        # Dịch chuyển chéo góc: (1,1) ↔ (34,16)
        # Dịch chuyển dọc: (1,1) ↔ (1,16) và (34,1) ↔ (34,16)
        self.opposite_corners = {
            (1, 1): (self.width - 2, self.height - 3),  # (1,1) -> (34,16)
            (self.width - 2, self.height - 3): (1, 1),   # (34,16) -> (1,1)
            (1, self.height - 3): (1, 1),                # (1,16) -> (1,1)
            (self.width - 2, 1): (self.width - 2, self.height - 3)  # (34,1) -> (34,16)
        }
        
        # Khởi tạo các đối tượng animation, movement và renderer.
        self.animation = PacmanAnimation()
        self.movement = Movement()
        self.renderer = GameVisualizer(self.width, self.height)
        
        # Tạo bề mặt cho các đối tượng trong game (tường, thức ăn, v.v.).
        self.walls = pygame.Surface((self.width, self.height))
        self.food = pygame.Surface((self.width, self.height))
        self.walls.fill((0, 0, 0))  # Màu đen cho tường.
        self.food.fill((0, 0, 0))  # Màu đen cho thức ăn.
        
        self.magical_pies = []  # Danh sách lưu các vị trí của bánh kỳ diệu.
        self.agentPositions = []  # Danh sách lưu các vị trí của Pacman.
        self.ghosts = []  # Danh sách lưu các đối tượng Ghost.
        self.exit_gates = []  # Danh sách lưu các vị trí của Exit Gates.
        
        # Tạo layout từ dữ liệu.
        self.generateLayoutData(layoutData)
        self.layoutData = layoutData

    def generateLayoutData(self, layoutData):
        # Tạo các đối tượng trong layout từ dữ liệu.
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutData[y][x]
                self.generateLayoutChar(x, y, layoutChar)

    def generateLayoutChar(self, x, y, layoutChar):
        # Sinh ra các đối tượng trong layout dựa trên ký tự tương ứng.
        if layoutChar == "%":
            self.walls.set_at((x, y), (255, 255, 255))  # Tường.
        elif layoutChar == ".":
            self.food.set_at((x, y), (255, 255, 255))  # Thức ăn.
        elif layoutChar == "o":  # Thay đổi từ "O" thành "o" theo yêu cầu
            self.magical_pies.append((x, y))  # Bánh kỳ diệu.
        elif layoutChar == "P":
            self.agentPositions.append((0, (x, y)))  # Vị trí Pacman.
        elif layoutChar == "G":
            self.ghosts.append(Ghost((x, y)))  # Tạo đối tượng Ghost.
        elif layoutChar == "E":
            self.exit_gates.append((x, y))  # Vị trí Exit Gates.

    def rotate_maze_simple(self):
        """Xoay mê cung 90 độ sang phải - phiên bản đơn giản"""
        print("Rotating maze 90 degrees clockwise...")
        
        # Lưu trạng thái hiện tại
        old_width = self.width
        old_height = self.height
        old_layout = [row[:] for row in self.layoutData]  # Copy deep
        
        # Tạo layout mới với kích thước đã xoay
        new_width = old_height
        new_height = old_width
        new_layout = []
        
        # Tạo layout mới bằng cách xoay từng ô
        for i in range(new_height):
            new_row = []
            for j in range(new_width):
                # Công thức xoay: (i, j) trong layout mới = (old_height - 1 - j, i) trong layout cũ
                old_i = old_height - 1 - j
                old_j = i
                
                if 0 <= old_i < old_height and 0 <= old_j < old_width:
                    new_row.append(old_layout[old_i][old_j])
                else:
                    new_row.append(' ')  # Padding với space
            new_layout.append(''.join(new_row))
        
        # Cập nhật kích thước và layout
        self.width = new_width
        self.height = new_height
        self.layoutData = new_layout
        
        # Tạo lại surfaces với kích thước mới
        self.walls = pygame.Surface((self.width, self.height))
        self.food = pygame.Surface((self.width, self.height))
        self.walls.fill((0, 0, 0))
        self.food.fill((0, 0, 0))
        
        # KHÔNG reset thức ăn và bánh kỳ diệu - giữ nguyên trạng thái
        # Chỉ reset các objects khác
        self.agentPositions = []
        self.ghosts = []
        self.exit_gates = []
        
        # Tạo lại walls từ layout mới
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = self.layoutData[y][x]
                if layoutChar == "%":
                    self.walls.set_at((x, y), (255, 255, 255))  # Tường
                elif layoutChar == "G":
                    self.ghosts.append(Ghost((x, y)))
                elif layoutChar == "E":
                    self.exit_gates.append((x, y))
        
        # Cập nhật cổng dịch chuyển
        self.opposite_corners = {
            (1, 1): (self.width - 2, self.height - 3),  # (1,1) -> (34,16)
            (self.width - 2, self.height - 3): (1, 1),   # (34,16) -> (1,1)
            (1, self.height - 3): (1, 1),                # (1,16) -> (1,1)
            (self.width - 2, 1): (self.width - 2, self.height - 3)  # (34,1) -> (34,16)
        }
        
        # Cập nhật renderer và thay đổi kích thước cửa sổ
        self.renderer.resize_window(self.width, self.height)
        
        print(f"Maze rotated: {old_width}x{old_height} -> {self.width}x{self.height}")
        
    def rotate_maze(self):
        """Wrapper function để sử dụng hàm xoay mới"""
        self.rotate_maze_simple()
        

    @staticmethod
    def getLayout(name):
        """
        Tải layout từ file, nếu không tìm thấy sẽ báo lỗi.
        """
        if name.endswith('.txt'):
            layout = tryToLoad(name)  # Tải file nếu đã có phần mở rộng .txt.
        else:
            layout = tryToLoad(name + '.txt')  # Tự động thêm phần mở rộng .txt.
        
        if layout is None:
            print(f"Could not find layout: {name}")  # Thông báo lỗi nếu không tìm thấy file.
            return None
        return layout

    def display(self, pacman_pos, direction=None, powered=False, power_timer=0, total_steps=None):
        """
        Hiển thị layout, Pacman và các đối tượng trên màn hình.
        """
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False  # Nếu thoát game, trả về False.

        # Kiểm tra số bước đi của Pacman.
        if hasattr(self, 'prev_pacman_pos'):
            if self.prev_pacman_pos != pacman_pos:
                self.steps += 1  # Tăng số bước đi nếu vị trí Pacman thay đổi.
        else:
            self.steps = 0  # Khởi tạo số bước đi nếu chưa có.

        self.prev_pacman_pos = pacman_pos  # Lưu lại vị trí Pacman trước đó.

        # Cập nhật vị trí di chuyển của Pacman.
        # Trong chế độ thủ công, không cho phép teleport tự động
        allow_auto_teleport = not hasattr(self, 'manual_mode') or not self.manual_mode
        self.movement.update_position(pacman_pos, self.opposite_corners, allow_auto_teleport)
        interpolated_pos = self.movement.get_interpolated_position()  # Tính toán vị trí nội suy.

        # Lấy khung hình hiện tại từ animation.
        current_frame = self.animation.get_current_frame(current_time, direction)

        # Làm mới màn hình và vẽ các đối tượng.
        self.renderer.clear_screen()
        self.renderer.draw_walls(self.walls, powered)  # Vẽ tường.
        self.renderer.draw_food(self.food)  # Vẽ thức ăn.
        self.renderer.draw_magical_pies(self.magical_pies)  # Vẽ bánh kỳ diệu.
        self.renderer.draw_ghosts(self.ghosts)  # Vẽ Ghosts.
        self.renderer.draw_exit_gates(self.exit_gates)  # Vẽ Exit Gates.
        self.renderer.draw_pacman(interpolated_pos, current_frame, powered)  # Vẽ Pacman.

        # Hiển thị step counter ở giữa trên cùng
        if total_steps:
            self.renderer.draw_step_counter(self.steps, total_steps)
        
        # Tính điểm số dựa trên thức ăn đã ăn và bánh kỳ diệu
        score = self.calculate_score()
        
        # Hiển thị điểm số ở bên trái trên cùng
        self.renderer.draw_score(score)
        
        # Hiển thị vị trí ở bên phải trên cùng
        self.renderer.draw_position(pacman_pos)

        # Cập nhật màn hình và điều chỉnh tốc độ khung hình.
        self.renderer.update_display()
        pygame.time.Clock().tick(120)

        return True

    def calculate_score(self):
        """Tính điểm số dựa trên thức ăn đã ăn và bánh kỳ diệu"""
        # Sử dụng score từ PacmanGame nếu có
        if hasattr(self, 'pacman_game') and hasattr(self.pacman_game, 'score'):
            return self.pacman_game.score
        
        # Fallback: tính toán thủ công
        score = 0
        
        # Đếm số thức ăn đã ăn (so với tổng số ban đầu)
        total_food_spots = 0
        remaining_food = 0
        
        # Đếm tổng số vị trí thức ăn ban đầu và còn lại
        for y in range(self.height):
            for x in range(self.width):
                if y < len(self.layoutData) and x < len(self.layoutData[y]):
                    if self.layoutData[y][x] == '.':
                        total_food_spots += 1
                
                # Kiểm tra thức ăn còn lại một cách an toàn
                try:
                    if (0 <= x < self.food.get_width() and 
                        0 <= y < self.food.get_height() and 
                        self.food.get_at((x, y)) == (255, 255, 255)):
                        remaining_food += 1
                except (IndexError, ValueError):
                    continue
        
        # Điểm cho thức ăn đã ăn (10 điểm mỗi thức ăn)
        eaten_food = total_food_spots - remaining_food
        score += eaten_food * 10
        
        # Điểm cho bánh kỳ diệu đã ăn (50 điểm mỗi bánh)
        total_pies_spots = 0
        for y in range(self.height):
            for x in range(self.width):
                if y < len(self.layoutData) and x < len(self.layoutData[y]):
                    if self.layoutData[y][x] == 'o':
                        total_pies_spots += 1
        
        eaten_pies = total_pies_spots - len(self.magical_pies)
        score += eaten_pies * 50
        
        return score

def tryToLoad(fullname):
    """
    Thử tải file layout từ đường dẫn đầy đủ.
    """
    # Kiểm tra đường dẫn tuyệt đối trước
    if os.path.exists(fullname):
        try:
            with open(fullname, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return Layout(lines)
        except UnicodeDecodeError:
            # Thử với encoding khác nếu UTF-8 không hoạt động
            with open(fullname, 'r', encoding='cp1252') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return Layout(lines)
    
    # Nếu không tìm thấy, thử tìm trong thư mục hiện tại
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, fullname)
    
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return Layout(lines)
        except UnicodeDecodeError:
            # Thử với encoding khác nếu UTF-8 không hoạt động
            with open(full_path, 'r', encoding='cp1252') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return Layout(lines)
    
    return None