from game import Layout
from action import Direction
from state import State
import pygame
import time

class ManualPacmanGame:
    def __init__(self, layout):
        # Khởi tạo game với layout đã cho
        self.layout = layout
        # Đánh dấu chế độ thủ công để không tự động teleport
        self.layout.manual_mode = True
        
        # Khởi tạo trạng thái ban đầu của Pacman
        self.state = State(self.layout.agentPositions[0][1], Direction.STOP, self.getFoodGrid(), 0)
        
        # Thời gian còn lại cho phép Pacman ăn bánh kỳ diệu
        self.power_timer = 0
        
        # Tổng số bánh kỳ diệu ban đầu trong layout
        self.total_pies = len(self.getMagicalPies())
        
        # Đếm số bước
        self.step_count = 0
        self.score = 0
        # Cờ game over khi Pacman đụng ma
        self.game_over = False
        # Danh sách các ô tường đã lên kế hoạch phá sau khi ăn magical pie
        self.planned_walls = set()
        
        # Hướng di chuyển hiện tại
        self.current_direction = Direction.STOP
        self.pending_direction = None  # Hướng chờ đợi để thử lại
        
        # Cải thiện điều khiển
        self.move_timer = 0  # Timer để kiểm soát tốc độ di chuyển
        self.move_delay = 2  # Số frame cần chờ giữa các lần di chuyển (càng nhỏ càng nhanh)
        
        # Lưu trữ các hành động và vị trí
        self.actions_log = []
        self.position_log = []
        
        # Lưu trữ các tường đã ăn
        self.eaten_walls = []
        
        # Lưu trữ các góc teleport ban đầu
        self.teleport_corners = {
            (1, 1): 1,      # Góc trái trên
            (34, 1): 2,     # Góc phải trên  
            (1, 16): 3,     # Góc trái dưới
            (34, 16): 4     # Góc phải dưới
        }

    def getStartState(self):
        return self.state.getPosition()
        
    def getFoodGrid(self):
        # Tạo một lưới thực phẩm, đánh dấu các vị trí có thức ăn (trắng)
        return [
            [self.isFood((x, y)) for x in range(self.layout.width)]
            for y in range(self.layout.height)
        ]
        
    def isFood(self, pos):
        # Kiểm tra xem vị trí có phải là thức ăn hay không
        try:
            return self.layout.food.get_at(pos) == (255, 255, 255)
        except (IndexError, ValueError):
            return False
        
    def isWall(self, pos):
        # Kiểm tra xem vị trí có phải là tường hay không
        try:
            return self.layout.walls.get_at(pos) == (255, 255, 255)
        except (IndexError, ValueError):
            return True  # Nếu ra ngoài bounds, coi như là tường
        
    def isMagicalPie(self, pos):
        # Kiểm tra xem vị trí có phải là bánh kỳ diệu hay không
        return pos in self.getMagicalPies()

    def getMagicalPies(self):
        # Trả về danh sách các vị trí bánh kỳ diệu
        return self.layout.magical_pies

    def isGoalState(self, state):
        # Kiểm tra xem Pacman đã ăn hết tất cả thực phẩm và ở cổng exit hay chưa
        pos = state.getPosition()
        exit_gates = self.layout.exit_gates
        
        # Kiểm tra đã ăn hết thức ăn chưa
        food_eaten = not any(any(row) for row in state.food_grid)
        
        # Kiểm tra có ở cổng exit không
        at_exit = pos in exit_gates
        
        return food_eaten and at_exit

    def rotate_maze_and_update_coordinates(self):
        """Xoay ma trận 90 độ và cập nhật tọa độ thức ăn, magical_pies"""
        
        # Lưu kích thước cũ trước khi xoay
        old_width = self.layout.width
        old_height = self.layout.height
        
        # Lưu trữ tọa độ hiện tại của thức ăn và magical_pies
        current_food_positions = []
        current_magical_pie_positions = list(self.layout.magical_pies)
        
        # Thu thập tất cả vị trí thức ăn hiện tại
        for y in range(old_height):
            for x in range(old_width):
                if self.isFood((x, y)):
                    current_food_positions.append((x, y))
        
        # Xoay ma trận layout
        self.layout.rotate_maze_simple()
        
        # Cập nhật tọa độ thức ăn sau khi xoay
        self.update_food_coordinates_after_rotation(current_food_positions, old_width, old_height)
        
        # Cập nhật tọa độ magical_pies sau khi xoay
        self.update_magical_pie_coordinates_after_rotation(current_magical_pie_positions, old_width, old_height)
        
        # Cập nhật vị trí Pacman sau khi xoay
        self.update_pacman_position_after_rotation(old_width, old_height)
        
        # Cập nhật các góc teleport sau khi xoay
        self.update_teleport_corners_after_rotation(old_width, old_height)
        

    def update_food_coordinates_after_rotation(self, old_food_positions, old_width, old_height):
        """Cập nhật tọa độ thức ăn sau khi xoay ma trận 90 độ"""
        # Xóa tất cả thức ăn cũ
        self.layout.food.fill((0, 0, 0))
        
        # Thêm thức ăn mới với tọa độ đã xoay
        for x, y in old_food_positions:
            # Xoay tọa độ 90 độ theo chiều kim đồng hồ
            new_x = old_height - 1 - y
            new_y = x
            
            # Đảm bảo tọa độ mới trong bounds của ma trận mới
            if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
                self.layout.food.set_at((new_x, new_y), (255, 255, 255))

    def update_magical_pie_coordinates_after_rotation(self, old_magical_pie_positions, old_width, old_height):
        """Cập nhật tọa độ magical_pies sau khi xoay ma trận 90 độ"""
        new_magical_pies = []
        
        for x, y in old_magical_pie_positions:
            # Xoay tọa độ 90 độ theo chiều kim đồng hồ
            new_x = old_height - 1 - y
            new_y = x
            
            # Đảm bảo tọa độ mới trong bounds của ma trận mới
            if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
                new_magical_pies.append((new_x, new_y))
        
        # Cập nhật danh sách magical_pies
        self.layout.magical_pies = new_magical_pies

    def update_pacman_position_after_rotation(self, old_width, old_height):
        """Cập nhật vị trí Pacman sau khi xoay ma trận 90 độ"""
        old_pos = self.state.getPosition()
        old_x, old_y = old_pos
        
        # Xoay tọa độ 90 độ theo chiều kim đồng hồ
        new_x = old_height - 1 - old_y
        new_y = old_x
        
        # Đảm bảo tọa độ mới trong bounds của ma trận mới
        if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
            self.state.pos = (new_x, new_y)

    def update_teleport_corners_after_rotation(self, old_width, old_height):
        """Cập nhật các góc teleport sau khi xoay ma trận 90 độ"""
        new_teleport_corners = {}
        
        for (x, y), corner_num in self.teleport_corners.items():
            # Xoay tọa độ 90 độ theo chiều kim đồng hồ
            new_x = old_height - 1 - y
            new_y = x
            
            # Đảm bảo tọa độ mới trong bounds của ma trận mới
            if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
                new_teleport_corners[(new_x, new_y)] = corner_num
        
        # Cập nhật các góc teleport
        self.teleport_corners = new_teleport_corners

    def update(self):
        # Không giảm power_timer ở đây nữa - sẽ giảm trong move_pacman()
        
        pos = self.state.getPosition()
        
        # Kiểm tra bounds của Pacman - đảm bảo không ra ngoài mê cung
        if (pos[0] < 0 or pos[0] >= self.layout.width or 
            pos[1] < 0 or pos[1] >= self.layout.height):
            # Điều chỉnh vị trí về trong bounds
            new_x = max(0, min(pos[0], self.layout.width - 1))
            new_y = max(0, min(pos[1], self.layout.height - 1))
            self.state.pos = (new_x, new_y)
            pos = self.state.getPosition()
        
        # Nếu Pacman ăn thức ăn, xóa thức ăn khỏi bản đồ và tăng điểm
        if self.isFood(pos):
            try:
                self.layout.food.set_at(pos, (0, 0, 0))
            except Exception:
                pass
            self.score += 10  # Tăng 10 điểm cho mỗi thức ăn
        
        # Nếu Pacman ăn bánh kỳ diệu, xóa nó khỏi danh sách bánh kỳ diệu và bật chế độ siêu Pacman
        if self.isMagicalPie(pos):
            self.layout.magical_pies.remove(pos)
            self.power_timer = 5  # Bật chế độ siêu Pacman trong 5 bước đi
            self.score += 50  # Tăng 50 điểm cho bánh kỳ diệu
        
        # Di chuyển tất cả ghosts
        for ghost in self.layout.ghosts:
            ghost.move(self.layout)
        
        # Kiểm tra va chạm Pacman - ma (game over)
        for ghost in self.layout.ghosts:
            if ghost.getPosition() == pos:
                self.game_over = True
                break

    def handle_input(self):
        """Xử lý input từ bàn phím với cải thiện điều khiển"""
        keys = pygame.key.get_pressed()
        
        # Lưu hướng trước đó
        previous_direction = self.current_direction
        
        # Xử lý phím mũi tên và WASD với logic cải thiện
        if keys[pygame.K_UP] or keys[pygame.K_w]:
            self.current_direction = Direction.NORTH
        elif keys[pygame.K_DOWN] or keys[pygame.K_s]:
            self.current_direction = Direction.SOUTH
        elif keys[pygame.K_LEFT] or keys[pygame.K_a]:
            self.current_direction = Direction.WEST
        elif keys[pygame.K_RIGHT] or keys[pygame.K_d]:
            self.current_direction = Direction.EAST
        elif keys[pygame.K_SPACE]:
            self.current_direction = Direction.STOP
        
        # Cải thiện: Cho phép thay đổi hướng ngay lập tức nếu có thể
        if self.current_direction != previous_direction and self.current_direction != Direction.STOP:
            # Kiểm tra xem có thể di chuyển theo hướng mới không
            if self.can_move(self.current_direction):
                # Nếu có thể, cập nhật hướng ngay lập tức
                pass
            else:
                # Nếu không thể, giữ hướng cũ nhưng lưu hướng mới để thử lại sau
                self.pending_direction = self.current_direction
                self.current_direction = previous_direction
        
        # Cải thiện: Xử lý di chuyển liên tục
        # Nếu không có phím nào được nhấn, giữ hướng hiện tại
        if not any([keys[pygame.K_UP], keys[pygame.K_DOWN], keys[pygame.K_LEFT], keys[pygame.K_RIGHT],
                   keys[pygame.K_w], keys[pygame.K_s], keys[pygame.K_a], keys[pygame.K_d], keys[pygame.K_SPACE]]):
            # Không thay đổi hướng nếu không có input mới
            pass
        
        # Điều chỉnh tốc độ di chuyển
        if keys[pygame.K_PLUS] or keys[pygame.K_EQUALS]:  # Tăng tốc độ (giảm delay)
            self.move_delay = max(0, self.move_delay - 1)  # Cho phép delay = 0 (di chuyển mỗi frame)
        elif keys[pygame.K_MINUS]:  # Giảm tốc độ (tăng delay)
            self.move_delay = min(5, self.move_delay + 1)  # Giới hạn delay tối đa là 5
        
        # Xử lý teleport thủ công
        self.handle_teleport_input(keys)

    def handle_teleport_input(self, keys):
        """Xử lý input teleport thủ công với logic mới"""
        current_pos = self.state.getPosition()
        
        # Sử dụng teleport_corners đã được cập nhật sau khi xoay
        corners = self.teleport_corners
        
        # Chỉ xử lý teleport nếu ở vị trí teleport hợp lệ
        if current_pos not in corners:
            return
        
        current_corner = corners[current_pos]
        
        # Tìm vị trí của các góc đối diện
        corner_positions = {v: k for k, v in corners.items()}
        
        # Shift + T: Dịch chuyển chéo góc
        if keys[pygame.K_LSHIFT] and keys[pygame.K_t]:
            if current_corner == 1:  # Góc 1 -> Góc 4
                if 4 in corner_positions:
                    self.state.pos = corner_positions[4]
            elif current_corner == 4:  # Góc 4 -> Góc 1
                if 1 in corner_positions:
                    self.state.pos = corner_positions[1]
            elif current_corner == 2:  # Góc 2 -> Góc 3
                if 3 in corner_positions:
                    self.state.pos = corner_positions[3]
            elif current_corner == 3:  # Góc 3 -> Góc 2
                if 2 in corner_positions:
                    self.state.pos = corner_positions[2]
        
        # T + 1: Dịch chuyển đến góc 1
        elif keys[pygame.K_t] and keys[pygame.K_1]:
            if current_corner != 1 and 1 in corner_positions:  # Không dịch chuyển nếu đã ở góc 1
                self.state.pos = corner_positions[1]
        
        # T + 2: Dịch chuyển đến góc 2
        elif keys[pygame.K_t] and keys[pygame.K_2]:
            if current_corner != 2 and 2 in corner_positions:  # Không dịch chuyển nếu đã ở góc 2
                self.state.pos = corner_positions[2]
        
        # T + 3: Dịch chuyển đến góc 3
        elif keys[pygame.K_t] and keys[pygame.K_3]:
            if current_corner != 3 and 3 in corner_positions:  # Không dịch chuyển nếu đã ở góc 3
                self.state.pos = corner_positions[3]
        
        # T + 4: Dịch chuyển đến góc 4
        elif keys[pygame.K_t] and keys[pygame.K_4]:
            if current_corner != 4 and 4 in corner_positions:  # Không dịch chuyển nếu đã ở góc 4
                self.state.pos = corner_positions[4]

    def can_move(self, direction):
        """Kiểm tra xem có thể di chuyển theo hướng đã cho không"""
        if direction == Direction.STOP:
            return True
            
        pos = self.state.getPosition()
        vector = Direction._directions[direction]
        new_x = pos[0] + vector[0]
        new_y = pos[1] + vector[1]
        new_pos = (new_x, new_y)
        
        # Kiểm tra bounds
        if (new_x < 0 or new_x >= self.layout.width or 
            new_y < 0 or new_y >= self.layout.height):
            return False
            
        # Kiểm tra tường - cho phép ăn tường khi có power
        if self.isWall(new_pos) and self.power_timer <= 0:
            return False
        
        # Không cần kiểm tra teleport ở đây vì teleport được xử lý riêng trong move_pacman
            
        return True

    def move_pacman(self):
        """Di chuyển Pacman theo hướng hiện tại với cải thiện điều khiển"""
        # Kiểm tra pending direction trước
        if self.pending_direction is not None and self.can_move(self.pending_direction):
            self.current_direction = self.pending_direction
            self.pending_direction = None
        
        if self.current_direction == Direction.STOP:
            self.move_timer = 0  # Reset timer khi dừng
            return
        
        # Kiểm soát tốc độ di chuyển
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return  # Chưa đến lúc di chuyển
            
        if not self.can_move(self.current_direction):
            return
            
        # Di chuyển bình thường - KHÔNG tự động teleport
        current_pos = self.state.getPosition()
        vector = Direction._directions[self.current_direction]
        new_x = current_pos[0] + vector[0]
        new_y = current_pos[1] + vector[1]
        new_pos = (new_x, new_y)
        
        # Cập nhật vị trí trực tiếp
        self.state.pos = new_pos
        self.state.direction = self.current_direction
        
        # Reset timer sau khi di chuyển
        self.move_timer = 0
        
        # Logic ăn tường khi có power - chỉ ăn khi thực sự di chuyển đến vị trí có tường
        if self.power_timer > 0 and self.isWall(new_pos):
            self.eat_wall_at_position(new_pos)
        
        # Kiểm tra và điều chỉnh bounds sau khi di chuyển
        pos = self.state.getPosition()
        if (pos[0] < 0 or pos[0] >= self.layout.width or 
            pos[1] < 0 or pos[1] >= self.layout.height):
            # Điều chỉnh vị trí về trong bounds
            new_x = max(0, min(pos[0], self.layout.width - 1))
            new_y = max(0, min(pos[1], self.layout.height - 1))
            self.state.pos = (new_x, new_y)
        
        # Giảm power_timer khi thực sự di chuyển (chỉ khi đã di chuyển thành công)
        if self.power_timer > 0:
            self.power_timer -= 1
        
        # Tăng bộ đếm bước khi thực sự di chuyển
        self.step_count += 1
        
        # Kiểm tra xem có cần xoay ma trận không (mỗi 30 bước)
        if self.step_count % 30 == 0:
            self.rotate_maze_and_update_coordinates()
        
        # Lưu hành động và vị trí
        self.actions_log.append(self.current_direction)
        self.position_log.append(f"Step {self.step_count}: {self.current_direction} at {self.state.getPosition()}")

    def eat_wall_at_position(self, pos):
        """Ăn tường tại vị trí hiện tại khi có power"""
        if self.isWall(pos):
            try:
                # Xóa tường khỏi bản đồ
                self.layout.walls.set_at(pos, (0, 0, 0))
                
                # Thêm điểm cho việc ăn tường
                self.score += 5
                
                # Lưu tường đã ăn để có thể khôi phục sau
                if not hasattr(self, 'eaten_walls'):
                    self.eaten_walls = []
                self.eaten_walls.append(pos)
                
            except (IndexError, ValueError):
                pass  # Bỏ qua nếu có lỗi


    def show_win_effect(self):
        """Hiệu ứng thắng cuộc"""
        self.layout.renderer.draw_win_message()
        pygame.display.flip()
        time.sleep(2)

    def show_game_over_effect(self):
        """Hiệu ứng thua cuộc"""
        self.layout.renderer.draw_game_over_message()
        pygame.display.flip()
        time.sleep(2)

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
