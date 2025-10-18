from game import Layout
from visualize import Direction
from state import State
from base_pacman import BasePacmanGame
import pygame
import time

class PacmanGame(BasePacmanGame):
    """Manual Pacman Game - Chế độ điều khiển thủ công"""
    
    def __init__(self, layout):
        # Gọi constructor của base class
        super().__init__(layout, is_manual=True)
        
        # Hướng di chuyển hiện tại
        self.current_direction = Direction.STOP
        self.pending_direction = None  # Hướng chờ đợi để thử lại
        
        # Cải thiện điều khiển
        self.move_timer = 0  # Timer để kiểm soát tốc độ di chuyển
        self.move_delay = 2  # Số frame cần chờ giữa các lần di chuyển (càng nhỏ càng nhanh)

    def handle_input(self):
        """Xử lý input từ bàn phím"""
        keys = pygame.key.get_pressed()
        
        # Xử lý phím tăng/giảm tốc độ
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:
            if self.move_delay > 0:
                self.move_delay -= 1
        elif keys[pygame.K_MINUS]:
            if self.move_delay < 10:
                self.move_delay += 1
        
        # Xử lý phím di chuyển
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.pending_direction = Direction.NORTH
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.pending_direction = Direction.SOUTH
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.pending_direction = Direction.WEST
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.pending_direction = Direction.EAST
        elif keys[pygame.K_SPACE]:
            self.pending_direction = Direction.STOP
        
        # Xử lý teleport thủ công
        if keys[pygame.K_t]:
            if keys[pygame.K_LSHIFT] or keys[pygame.K_RSHIFT]:
                # Teleport chéo góc
                self.handle_diagonal_teleport()
            elif keys[pygame.K_1]:
                self.handle_teleport_to_corner(1)
            elif keys[pygame.K_2]:
                self.handle_teleport_to_corner(2)
            elif keys[pygame.K_3]:
                self.handle_teleport_to_corner(3)
            elif keys[pygame.K_4]:
                self.handle_teleport_to_corner(4)

    def handle_diagonal_teleport(self):
        """Xử lý teleport chéo góc"""
        current_pos = self.state.getPosition()
        
        # Kiểm tra xem có ở góc teleport không
        if current_pos in self.teleport_corners:
            corner_num = self.teleport_corners[current_pos]
            
            # Tìm góc đối diện
            opposite_corner = None
            for pos, num in self.teleport_corners.items():
                if num != corner_num:
                    opposite_corner = pos
                    break
            
            if opposite_corner:
                # Kiểm tra xem góc đối diện có phải là góc đối diện thực sự không
                if self.is_opposite_corner(current_pos, opposite_corner):
                    self.state.pos = opposite_corner

    def handle_teleport_to_corner(self, corner_num):
        """Xử lý teleport đến góc cụ thể"""
        current_pos = self.state.getPosition()
        
        # Kiểm tra xem có ở góc teleport không
        if current_pos in self.teleport_corners:
            # Tìm góc đích
            target_corner = None
            for pos, num in self.teleport_corners.items():
                if num == corner_num:
                    target_corner = pos
                    break
            
            if target_corner and target_corner != current_pos:
                self.state.pos = target_corner

    def is_opposite_corner(self, pos1, pos2):
        """Kiểm tra xem hai vị trí có phải là góc đối diện không"""
        x1, y1 = pos1
        x2, y2 = pos2
        
        # Kiểm tra xem có phải là góc đối diện thực sự không
        # (1,1) <-> (34,16) và (34,1) <-> (1,16)
        return ((x1 == 1 and y1 == 1 and x2 == 34 and y2 == 16) or
                (x1 == 34 and y1 == 16 and x2 == 1 and y2 == 1) or
                (x1 == 34 and y1 == 1 and x2 == 1 and y2 == 16) or
                (x1 == 1 and y1 == 16 and x2 == 34 and y2 == 1))

    def move_pacman(self):
        """Di chuyển Pacman theo hướng hiện tại"""
        # Tăng timer di chuyển
        self.move_timer += 1
        
        # Kiểm tra xem có thể di chuyển không
        if self.move_timer < self.move_delay:
            return
        
        # Reset timer
        self.move_timer = 0
        
        # Xử lý hướng chờ đợi
        if self.pending_direction is not None:
            self.current_direction = self.pending_direction
            self.pending_direction = None
        
        # Thực hiện di chuyển
        if self.current_direction != Direction.STOP:
            # Lấy vector di chuyển
            vector = Direction._directions[self.current_direction]
            
            # Tính vị trí mới
            new_pos = (self.state.getPosition()[0] + vector[0], 
                      self.state.getPosition()[1] + vector[1])
            
            # Kiểm tra tường - cho phép di chuyển vào tường nếu có power
            if not self.isWall(new_pos) or self.power_timer > 0:
                # Di chuyển Pacman - KHÔNG tự động teleport trong chế độ thủ công
                self.state = self.state.generateState(vector, {})  # Truyền dict rỗng để tắt teleport tự động
                
                # Cập nhật game state
                self.update()
                
                # Tăng bộ đếm bước khi thực sự di chuyển
                self.step_count += 1
                
                # Giảm power_timer khi thực sự di chuyển
                if self.power_timer > 0:
                    self.power_timer -= 1
                
                # Kiểm tra xem có cần xoay ma trận không (mỗi 30 bước, bắt đầu từ bước 30)
                if self.step_count > 0 and self.step_count % 30 == 0:
                    self.rotate_maze_and_update_coordinates()
                
                # Lưu hành động và vị trí
                self.actions_log.append(self.current_direction)
                self.position_log.append(f"Step {self.step_count}: {self.current_direction} at {self.state.getPosition()}")

    def run(self):
        """Chạy game với điều khiển thủ công"""
        clock = pygame.time.Clock()
        running = True
        
        while running and not self.game_over:
            # Xử lý sự kiện
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
            
            # Xử lý input liên tục
            self.handle_input()
            
            # Di chuyển Pacman
            self.move_pacman()
            
            # Cập nhật game state
            self.update()
            
            # Hiển thị màn hình
            current_pos = self.state.getPosition()
            if not self.layout.display(current_pos, self.current_direction, 
                                     self.power_timer > 0, self.power_timer, None):
                running = False
            
            # Kiểm tra mục tiêu
            if self.isGoalState(self.state):
                self.show_win_effect()
                break
            
            # Kiểm tra game over
            if self.game_over:
                self.show_game_over_effect()
                break
            
            clock.tick(8)  # 8 FPS để game chậm hơn và dễ chơi hơn
        
        # Lưu dữ liệu
        self.run_log = self.position_log
        self.total_cost = len(self.actions_log)
        self.final_position = self.state.getPosition()
        self.final_steps = self.step_count
        self.game_over_info = (self.step_count, self.final_position) if self.game_over else None

        # Giữ cửa sổ mở
        try:
            while True:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        return
                if not self.layout.display(current_pos, Direction.STOP, 
                                         self.power_timer > 0, self.power_timer, self.step_count):
                    break
                pygame.time.Clock().tick(60)
        except pygame.error:
            pass
