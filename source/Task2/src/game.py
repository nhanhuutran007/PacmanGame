
import pygame
import os
import time
import threading
from visualize import GameVisualizer, PacmanAnimation, Movement, Direction
from base_pacman import Ghost


class IntegratedGameManager:

    def __init__(self, layoutData):
        # Khởi tạo pygame
        pygame.init()
        
        # Đảm bảo tất cả các dòng có cùng độ dài
        max_width = max(len(line) for line in layoutData)
        layoutData = [line.ljust(max_width) for line in layoutData]
        
        # Lưu lại layout ban đầu để có thể khôi phục khi quay lại menu
        self._initial_layout = list(layoutData)

        self.width = len(layoutData[0])
        self.height = len(layoutData)
        
        # Khởi tạo các điểm cổng dịch chuyển
        self.opposite_corners = {
            (1, 1): (self.width - 2, self.height - 3),
            (self.width - 2, self.height - 3): (1, 1),
            (self.width - 2, 1): (1, self.height - 3),
            (1, self.height - 3): (self.width - 2, 1)
        }
        
        # Khởi tạo animation, movement và renderer
        self.animation = PacmanAnimation()
        self.movement = Movement()
        self.renderer = GameVisualizer(self.width, self.height)
        
        # Tạo surfaces cho game objects
        self.walls = pygame.Surface((self.width, self.height))
        self.food = pygame.Surface((self.width, self.height))
        self.walls.fill((0, 0, 0))
        self.food.fill((0, 0, 0))
        
        # Game objects
        self.magical_pies = []
        self.agentPositions = []
        self.ghosts = []
        self.exit_gates = []
        
        # Game state
        self.running = True
        self.current_mode = None
        self.game_instance = None
        self.steps = 0
        self.prev_pacman_pos = None
        
        # Tạo layout từ dữ liệu
        self.generateLayoutData(layoutData)
        self.layoutData = layoutData
        
        # Hiển thị mode selection ngay từ đầu
        self.renderer.show_mode_selection_screen()

    def generateLayoutData(self, layoutData):
       
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = layoutData[y][x]
                self.generateLayoutChar(x, y, layoutChar)

    def generateLayoutChar(self, x, y, layoutChar):
        
        if layoutChar == "%":
            self.walls.set_at((x, y), (255, 255, 255))  # Tường
        elif layoutChar == ".":
            self.food.set_at((x, y), (255, 255, 255))  # Thức ăn
        elif layoutChar == "o":
            self.magical_pies.append((x, y))  # Bánh kỳ diệu
        elif layoutChar == "P":
            self.agentPositions.append((0, (x, y)))  # Vị trí Pacman
        elif layoutChar == "G":
            self.ghosts.append(Ghost((x, y)))  # Ghost
        elif layoutChar == "E":
            self.exit_gates.append((x, y))  # Exit Gates
    
    def run(self):
        clock = pygame.time.Clock()
        
        while self.running:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        if self.renderer.is_mode_selection_visible():
                            self.running = False
                        else:
                            self.return_to_mode_selection()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 1:  # Left click
                        if self.renderer.is_mode_selection_visible():
                            action = self.renderer.handle_mode_selection_click(event.pos)
                            if action:
                                self.handle_mode_selection(action)
            
            # Hiển thị màn hình
            if self.renderer.is_mode_selection_visible():
                self.renderer.show_mode_selection_screen()
            elif self.game_instance:
                # Game đang chạy, không cần làm gì thêm
                pass
            
            # Cập nhật màn hình
            self.renderer.update_display()
            clock.tick(60)
        
        pygame.quit()
    
    def handle_mode_selection(self, action):
        if action == 'auto':
            self.start_auto_mode()
        elif action == 'manual':
            self.start_manual_mode()
        elif action == 'exit':
            self.exit_game()
    
    def start_auto_mode(self):
        print("Khoi dong che do tu dong...")
        self.renderer.hide_mode_selection()
        
        try:
            # Import động để tránh circular import
            from agent import AgentGame
            print(f"AgentPositions: {self.agentPositions}")
            print(f"Layout width: {self.width}, height: {self.height}")
            self.game_instance = AgentGame(self)
            result = self.game_instance.run()
            if result is False:
                # Game bị đóng cửa sổ, quay lại menu
                print("Game bi dong cua so, quay lai menu...")
                self.return_to_mode_selection()
            else:
                print("Che do tu dong hoan thanh!")
                time.sleep(1)
                self.return_to_mode_selection()
        except Exception as e:
            print(f"Loi trong che do tu dong: {e}")
            # Không in traceback để tránh spam console
            self.return_to_mode_selection()
    
    def start_manual_mode(self):
        print("Khoi dong che do thu cong...")
        self.renderer.hide_mode_selection()
        
        try:
            # Import động để tránh circular import
            from pacman import PacmanGame
            self.game_instance = PacmanGame(self)
            result = self.game_instance.run()
            if result is False:
                # Game bị đóng cửa sổ, quay lại menu
                print("Game bi dong cua so, quay lai menu...")
                self.return_to_mode_selection()
            else:
                print("Che do thu cong hoan thanh!")
                time.sleep(1)
                self.return_to_mode_selection()
        except Exception as e:
            print(f"Loi trong che do thu cong: {e}")
            self.return_to_mode_selection()
    
    def exit_game(self):
        print("Thoat game...")
        self.running = False
    
    def run_current_game(self):
       
        if self.game_instance:
            # Game đã được chạy trong thread riêng
            pass
    
    def return_to_mode_selection(self):
        self.game_instance = None
        self.current_mode = None
        # Reset game state
        self.steps = 0
        self.prev_pacman_pos = None
        # Khôi phục lại layout về trạng thái ban đầu để có thể chơi lại
        try:
            self.reset_layout_to_initial()
        except Exception:
            pass
        # Khôi phục kích thước cửa sổ về menu ban đầu
        if hasattr(self, 'renderer') and hasattr(self.renderer, 'reset_window'):
            self.renderer.reset_window()
        # Hiển thị lại mode selection
        self.renderer.show_mode_selection_screen()

    def display(self, pacman_pos, direction=None, powered=False, power_timer=0, total_steps=None):
        
        current_time = time.time()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                # Khi đóng cửa sổ game, quay lại menu thay vì thoát
                return False

        # Kiểm tra số bước đi của Pacman
        if hasattr(self, 'prev_pacman_pos') and self.prev_pacman_pos is not None:
            if self.prev_pacman_pos != pacman_pos:
                prev_x, prev_y = self.prev_pacman_pos
                curr_x, curr_y = pacman_pos
                distance = abs(curr_x - prev_x) + abs(curr_y - prev_y)
                
                if distance <= 1:
                    self.steps += 1
        else:
            self.steps = 0

        self.prev_pacman_pos = pacman_pos

        # Cập nhật vị trí di chuyển của Pacman
        allow_auto_teleport = not hasattr(self, 'manual_mode') or not self.manual_mode
        self.movement.update_position(pacman_pos, self.opposite_corners, allow_auto_teleport)
        interpolated_pos = self.movement.get_interpolated_position()

        # Lấy khung hình hiện tại từ animation
        current_frame = self.animation.get_current_frame(current_time, direction)

        # Làm mới màn hình và vẽ các đối tượng
        self.renderer.clear_screen()
        self.renderer.draw_walls(self.walls, powered)
        self.renderer.draw_food(self.food)
        self.renderer.draw_magical_pies(self.magical_pies)
        self.renderer.draw_ghosts(self.ghosts)
        self.renderer.draw_exit_gates(self.exit_gates)
        self.renderer.draw_pacman(interpolated_pos, current_frame, powered)
        
        # Hiển thị thông tin
        if total_steps:
            self.renderer.draw_step_counter(self.steps, total_steps)
        
        score = self.calculate_score()
        self.renderer.draw_score(score)
        
        if hasattr(self, 'manual_mode') and self.manual_mode:
            self.renderer.draw_step_count_only(self.steps)
        else:
            self.renderer.draw_position(pacman_pos)

        # Cập nhật màn hình
        self.renderer.update_display()
        pygame.time.Clock().tick(120)

        return True

    def calculate_score(self):
       
        if hasattr(self, 'pacman_game') and hasattr(self.pacman_game, 'score'):
            return self.pacman_game.score
        
        score = 0
        
        # Đếm số thức ăn đã ăn
        total_food_spots = 0
        remaining_food = 0
        
        for y in range(self.height):
            for x in range(self.width):
                if y < len(self.layoutData) and x < len(self.layoutData[y]):
                    if self.layoutData[y][x] == '.':
                        total_food_spots += 1
                
                try:
                    if (0 <= x < self.food.get_width() and 
                        0 <= y < self.food.get_height() and 
                        self.food.get_at((x, y)) == (255, 255, 255)):
                        remaining_food += 1
                except (IndexError, ValueError):
                    continue
        
        eaten_food = total_food_spots - remaining_food
        score += eaten_food * 10
        
        # Điểm cho bánh kỳ diệu đã ăn
        total_pies_spots = 0
        for y in range(self.height):
            for x in range(self.width):
                if y < len(self.layoutData) and x < len(self.layoutData[y]):
                    if self.layoutData[y][x] == 'o':
                        total_pies_spots += 1
        
        eaten_pies = total_pies_spots - len(self.magical_pies)
        score += eaten_pies * 50
        
        return score

    # ====== Helpers to rebuild layout ======
    def reset_layout_to_initial(self):
        initial_lines = list(self._initial_layout)
        # Chuẩn hóa độ dài các dòng (phòng khi xoay/ghi đè làm thay đổi)
        max_width = max(len(line) for line in initial_lines)
        initial_lines = [line.ljust(max_width) for line in initial_lines]

        # Cập nhật kích thước
        self.width = len(initial_lines[0])
        self.height = len(initial_lines)
        self.layoutData = initial_lines

        # Recompute opposite corners
        self.opposite_corners = {
            (1, 1): (self.width - 2, self.height - 3),
            (self.width - 2, self.height - 3): (1, 1),
            (self.width - 2, 1): (1, self.height - 3),
            (1, self.height - 3): (self.width - 2, 1)
        }

        # Recreate surfaces
        self.walls = pygame.Surface((self.width, self.height))
        self.food = pygame.Surface((self.width, self.height))
        self.walls.fill((0, 0, 0))
        self.food.fill((0, 0, 0))

        # Reset objects lists
        self.magical_pies = []
        self.agentPositions = []
        self.ghosts = []
        self.exit_gates = []

        # Generate objects again
        self.generateLayoutData(self.layoutData)

        # Đảm bảo cửa sổ renderer đúng kích thước logic hiện tại
        if hasattr(self, 'renderer') and hasattr(self.renderer, 'resize_window'):
            self.renderer.resize_window(self.width, self.height)
    
    def rotate_maze_simple(self):
        print("Rotating maze 90 degrees clockwise...")
        
        old_width = self.width
        old_height = self.height
        old_layout = [row[:] for row in self.layoutData]
        
        new_width = old_height
        new_height = old_width
        new_layout = []
        
        for i in range(new_height):
            new_row = []
            for j in range(new_width):
                old_i = old_height - 1 - j
                old_j = i
                
                if 0 <= old_i < old_height and 0 <= old_j < old_width:
                    new_row.append(old_layout[old_i][old_j])
                else:
                    new_row.append(' ')
            new_layout.append(''.join(new_row))
        
        self.width = new_width
        self.height = new_height
        self.layoutData = new_layout
        
        # Cập nhật surfaces
        self.walls = pygame.Surface((self.width, self.height))
        self.food = pygame.Surface((self.width, self.height))
        self.walls.fill((0, 0, 0))
        self.food.fill((0, 0, 0))
        
        # Reset objects
        self.agentPositions = []
        self.ghosts = []
        self.exit_gates = []
        
        # Regenerate layout
        for y in range(self.height):
            for x in range(self.width):
                layoutChar = self.layoutData[y][x]
                if layoutChar == "%":
                    self.walls.set_at((x, y), (255, 255, 255))
                elif layoutChar == "G":
                    self.ghosts.append(Ghost((x, y)))
                elif layoutChar == "E":
                    self.exit_gates.append((x, y))
        
        # Cập nhật renderer
        self.renderer.resize_window(self.width, self.height)
        print(f"Maze rotated: {old_width}x{old_height} -> {self.width}x{self.height}")
    
    @staticmethod
    def getLayout(name):
        if name.endswith('.txt'):
            layout = tryToLoad(name)
        else:
            layout = tryToLoad(name + '.txt')
        
        if layout is None:
            print(f"Could not find layout: {name}")
            return None
        return layout


def tryToLoad(fullname):
   
    if os.path.exists(fullname):
        try:
            with open(fullname, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return IntegratedGameManager(lines)
        except UnicodeDecodeError:
            with open(fullname, 'r', encoding='cp1252') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return IntegratedGameManager(lines)
    
    current_dir = os.path.dirname(os.path.abspath(__file__))
    full_path = os.path.join(current_dir, fullname)
    
    if os.path.exists(full_path):
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return IntegratedGameManager(lines)
        except UnicodeDecodeError:
            with open(full_path, 'r', encoding='cp1252') as f:
                lines = [line.rstrip('\n\r') for line in f]
            return IntegratedGameManager(lines)
    
    return None


def main():
    try:
        # Tải layout mặc định
        input_file = os.path.join(os.path.dirname(__file__), "..", "input", "task02_pacman_example_map.txt")
        if os.path.exists(input_file):
            with open(input_file, 'r', encoding='utf-8') as f:
                layout_data = [line.rstrip('\n\r') for line in f]
            game_manager = IntegratedGameManager(layout_data)
        else:
            print("Khong tim thay file map mac dinh!")
            # Tạo layout mặc định đơn giản
            layout_data = [
                "%%%%%%%%%%%%%%%%%%%%",
                "%..................%",
                "%P.................%",
                "%..................%",
                "%%%%%%%%%%%%%%%%%%%%"
            ]
            game_manager = IntegratedGameManager(layout_data)
        
        game_manager.run()
            
    except Exception as e:
        print(f"Loi khi khoi chay game: {e}")
        input("Nhấn Enter để thoát...")


if __name__ == '__main__':
    main()
