from game import Layout
from action import Direction
from state import State
from search import AStarDynamicSearch
import pygame
import time

class PacmanGame:
    def __init__(self, layout):
        # Khởi tạo game với layout đã cho.
        self.layout = layout
        
        # Khởi tạo trạng thái ban đầu của Pacman.
        # Sử dụng vị trí đầu tiên của Pacman trong layout, hướng STOP và trạng thái ban đầu của thực phẩm.
        self.state = State(self.layout.agentPositions[0][1], Direction.STOP, self.getFoodGrid(), 0)
        
        # Thời gian còn lại cho phép Pacman ăn bánh kỳ diệu.
        self.power_timer = 0
        
        # Tổng số bánh kỳ diệu ban đầu trong layout.
        self.total_pies = len(self.getMagicalPies())
        
        # Đếm số bước để xoay mê cung
        self.step_count = 0
        self.score = 0  # Điểm số của game
        # Cờ game over khi Pacman đụng ma
        self.game_over = False
        # Danh sách các ô tường đã lên kế hoạch phá sau khi ăn magical pie
        self.planned_walls = set()
        # Bộ tìm kiếm
        self.simple_dynamic_search = None

    def getStartState(self):
        # Trả về trạng thái ban đầu của Pacman (vị trí).
        return self.state.getPosition()
        
    def getFoodGrid(self):
        # Tạo một lưới thực phẩm, đánh dấu các vị trí có thức ăn (trắng).
        return [
            [self.isFood((x, y)) for x in range(self.layout.width)]
            for y in range(self.layout.height)
        ]
        
    def isFood(self, pos):
        # Kiểm tra xem vị trí có phải là thức ăn hay không.
        try:
            return self.layout.food.get_at(pos) == (255, 255, 255)
        except (IndexError, ValueError):
            return False
        
    def isWall(self, pos):
        # Kiểm tra xem vị trí có phải là tường hay không.
        try:
            return self.layout.walls.get_at(pos) == (255, 255, 255)
        except (IndexError, ValueError):
            return True  # Nếu ra ngoài bounds, coi như là tường
        
    def isMagicalPie(self, pos):
        # Kiểm tra xem vị trí có phải là bánh kỳ diệu hay không.
        return pos in self.getMagicalPies()

    def getMagicalPies(self):
        # Trả về danh sách các vị trí bánh kỳ diệu.
        return self.layout.magical_pies

    def getSuccessors(self, pos):
        successors = []
        x, y = pos
        width, height = self.layout.width, self.layout.height
        corners = self.layout.opposite_corners

        # Nếu vị trí hiện tại là cổng dịch chuyển, chuyển đến vị trí đối diện.
        if (x, y) in corners:
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

    def isGoalState(self, state):
        # Kiểm tra xem Pacman đã ăn hết tất cả thực phẩm và ở cổng exit hay chưa.
        pos = state.getPosition()
        exit_gates = self.layout.exit_gates
        
        # Kiểm tra đã ăn hết thức ăn chưa
        food_eaten = not any(any(row) for row in state.food_grid)
        
        # Kiểm tra có ở cổng exit không
        at_exit = pos in exit_gates
        
        return food_eaten and at_exit

    def update(self):
        if self.power_timer > 0:
            self.power_timer -= 1  # Giảm thời gian của bánh kỳ diệu.
        
        pos = self.state.getPosition()
        
        # Kiểm tra bounds của Pacman - đảm bảo không ra ngoài mê cung
        if (pos[0] < 0 or pos[0] >= self.layout.width or 
            pos[1] < 0 or pos[1] >= self.layout.height):
            # Điều chỉnh vị trí về trong bounds
            new_x = max(0, min(pos[0], self.layout.width - 1))
            new_y = max(0, min(pos[1], self.layout.height - 1))
            self.state.pos = (new_x, new_y)
            pos = self.state.getPosition()
        
        # Nếu Pacman ăn thức ăn, xóa thức ăn khỏi bản đồ và tăng điểm.
        if self.isFood(pos):
            try:
                self.layout.food.set_at(pos, (0, 0, 0))
            except Exception:
                pass
            self.score += 10  # Tăng 10 điểm cho mỗi thức ăn
        
        # Nếu Pacman ăn bánh kỳ diệu, xóa nó khỏi danh sách bánh kỳ diệu và bật chế độ siêu Pacman.
        if self.isMagicalPie(pos):
            self.layout.magical_pies.remove(pos)
            self.power_timer = 5  # Bật chế độ siêu Pacman trong 5 bước đi.
            self.score += 50  # Tăng 50 điểm cho bánh kỳ diệu
        
        # Di chuyển tất cả ghosts
        for ghost in self.layout.ghosts:
            ghost.move(self.layout)
        
        # Kiểm tra va chạm Pacman - ma (game over)
        for ghost in self.layout.ghosts:
            if ghost.getPosition() == pos:
                self.game_over = True
                break

        if self.game_over:
            return

    def run(self):
        corners = self.layout.opposite_corners
        self._run_simple_dynamic_search()
    
    def _run_simple_dynamic_search(self):
        """
        Chạy game với hệ thống tìm kiếm động đơn giản
        """
        corners = self.layout.opposite_corners
        
        # Khởi tạo hệ thống tìm kiếm đơn giản
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
            
            # Lấy hành động tiếp theo từ hệ thống tìm kiếm đơn giản
            action = self.simple_dynamic_search.find_next_action(self.state, self.layout.ghosts)
            
            # Thực hiện hành động
            vector = Direction._directions[action]
            self.state = self.state.generateState(vector, corners)
            self.update()
            
            # Kiểm tra va chạm
            if self.game_over:
                current_pos = self.state.getPosition()
                position_data.append(f"Step {step_count}: {action} at {current_pos} (GAME OVER)")
                break
            
            # Lưu dữ liệu
            current_pos = self.state.getPosition()
            position_data.append(f"Step {step_count}: {action} at {current_pos}")
            all_actions.append(action)
            
            # Hiển thị màn hình
            if not self.layout.display(current_pos, action, self.power_timer > 0, self.power_timer, max_steps):
                break
            
            # Kiểm tra mục tiêu
            if self.isGoalState(self.state):
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

 




