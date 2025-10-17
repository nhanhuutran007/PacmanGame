from game import Layout
from visualize import Direction
from state import State
from search import AStarDynamicSearch
from base_pacman import BasePacmanGame
import pygame
import time

class AgentGame(BasePacmanGame):
    """AI Agent - Trí tuệ nhân tạo tự động chơi game"""
    
    def __init__(self, layout):
        # Gọi constructor của base class
        super().__init__(layout, is_manual=False)
        
        # Bộ tìm kiếm AI
        self.simple_dynamic_search = None

    def getSuccessors(self, pos):
        """Tìm các bước đi có thể từ vị trí hiện tại"""
        successors = []
        x, y = pos
        width, height = self.layout.width, self.layout.height
        corners = self.layout.opposite_corners

        # CHỈ cho phép teleport tại các vị trí teleport hợp lệ đã định nghĩa
        # Kiểm tra xem có phải là vị trí teleport hợp lệ không
        valid_teleport_positions = set(corners.keys())
        if (x, y) in valid_teleport_positions:
            x, y = corners[(x, y)]
            new_pos = (x, y)
            successors.append((new_pos, Direction.STOP, 0))

        # Lấy các hướng di chuyển từ các vị trí xung quanh.
        for direction, (dx, dy) in Direction._directions.items():
            if direction == Direction.STOP:
                continue
            next_x, next_y = x + dx, y + dy
            
            # Kiểm tra bounds nghiêm ngặt - phải trong phạm vi hợp lệ
            if (0 <= next_x < width and 0 <= next_y < height):
                # Kiểm tra có thể di chuyển không (không phải tường hoặc có power)
                can_move = not self.isWall((next_x, next_y)) or self.power_timer > 0
                if can_move:
                    new_pos = (next_x, next_y)
                    # Kiểm tra thêm: vị trí mới phải hợp lệ và không phải tường
                    if (0 <= new_pos[0] < width and 0 <= new_pos[1] < height and 
                        (not self.isWall(new_pos) or self.power_timer > 0)):
                        
                        # Chi phí đơn vị (không né ma) để tìm đường ngắn nhất
                        cost = 1

                        successors.append((new_pos, direction, cost))
            # Nếu ra ngoài bounds, không thêm vào successors

        # Thêm hành động WAIT (STOP) với chi phí cố định 1
        successors.append(((x, y), Direction.STOP, 1))

        return successors

    def run(self):
        """Chạy AI Agent"""
        corners = self.layout.opposite_corners
        self.run_ai_search()
    
    def run_ai_search(self):
        """
        Chạy game với hệ thống tìm kiếm AI thông minh
        """
        corners = self.layout.opposite_corners
        
        # Khởi tạo hệ thống tìm kiếm AI
        self.simple_dynamic_search = AStarDynamicSearch(self, corners)
        
        # Tạo danh sách để lưu dữ liệu vị trí
        position_data = []
        all_actions = []
        total_cost = 0
        step_count = 0
        max_steps = 500  # Giới hạn số bước để tránh vòng lặp vô hạn
        
        while not self.game_over and step_count < max_steps:
            step_count += 1
            current_pos = self.state.getPosition()
            
            # Kiểm tra xoay ma trận mỗi 30 bước
            if step_count % 30 == 0:
                self.rotate_maze_and_update_coordinates()
                # Cập nhật lại hệ thống tìm kiếm sau khi xoay
                self.simple_dynamic_search = AStarDynamicSearch(self, corners)
            
            # Lấy hành động tiếp theo từ hệ thống tìm kiếm AI
            action = self.simple_dynamic_search.find_next_action(self.state, self.layout.ghosts)
            
            # Thực hiện hành động
            vector = Direction._directions[action]
            self.state = self.state.generateState(vector, corners)
            self.update()
            
            # Kiểm tra va chạm
            if self.game_over:
                current_pos = self.state.getPosition()
                position_data.append(f"Step {step_count}: {action} at {current_pos} (GAME OVER)")
                self.show_game_over_effect()
                break
            
            # Lưu dữ liệu
            current_pos = self.state.getPosition()
            position_data.append(f"Step {step_count}: {action} at {current_pos}")
            all_actions.append(action)
            
            # Hiển thị màn hình
            if not self.layout.display(current_pos, action, self.power_timer > 0, self.power_timer, step_count):
                break
            
            # Kiểm tra mục tiêu
            if self.isGoalState(self.state):
                self.show_win_effect()
                break
            
            time.sleep(0.1)
        
        # Lưu dữ liệu để main.py có thể ghi file sau khi chạy
        self.run_log = position_data
        self.actions_log = all_actions
        self.total_cost = len(all_actions)
        self.final_position = self.state.getPosition()
        self.final_steps = step_count
        self.game_over_info = (step_count, self.final_position) if self.game_over else None

        # Giữ cửa sổ mở (an toàn khi pygame đã tắt)
        current_pos = self.state.getPosition()
        try:
            while True:
                if not self.layout.display(current_pos, Direction.STOP, self.power_timer > 0, self.power_timer, step_count):
                    break
                pygame.time.Clock().tick(60)
        except pygame.error:
            # Tránh lỗi 'video system not initialized' nếu pygame đã bị đóng
            pass
