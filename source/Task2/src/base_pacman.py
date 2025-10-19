from visualize import Direction
from state import State
import pygame
import time

class Ghost:
    def __init__(self, pos, direction=Direction.EAST):
        self.pos = pos
        self.direction = direction  # Ghost chỉ di chuyển ngang (EAST hoặc WEST)
        self.move_timer = 0  # Timer để kiểm soát tốc độ di chuyển
        self.move_delay = 2  # Số frame cần chờ giữa các lần di chuyển (càng lớn càng chậm)
        
    def move(self, layout):
        # Di chuyển ghost theo hướng hiện tại, đổi hướng khi gặp tường
        # Kiểm soát tốc độ di chuyển
        self.move_timer += 1
        if self.move_timer < self.move_delay:
            return  # Chưa đến lúc di chuyển
        
        x, y = self.pos
        dx, dy = Direction._directions[self.direction]
        new_x, new_y = x + dx, y + dy
        
        # Kiểm tra xem có thể di chuyển không
        if (0 <= new_x < layout.width and 
            0 <= new_y < layout.height):
            # Kiểm tra có phải tường không
            try:
                is_wall = layout.walls.get_at((new_x, new_y)) == (255, 255, 255)
                if not is_wall:
                    self.pos = (new_x, new_y)
                    self.move_timer = 0  # Reset timer sau khi di chuyển
                else:
                    # Đổi hướng khi gặp tường
                    self.reverse_direction()
                    self.move_timer = 0  # Reset timer sau khi đổi hướng
            except (IndexError, ValueError):
                # Nếu có lỗi truy cập pixel, đổi hướng
                self.reverse_direction()
                self.move_timer = 0  # Reset timer sau khi đổi hướng
        else:
            # Nếu ra ngoài bounds, đổi hướng
            self.reverse_direction()
            self.move_timer = 0  # Reset timer sau khi đổi hướng
            
    def reverse_direction(self):
        # Đổi hướng di chuyển
        if self.direction == Direction.EAST:
            self.direction = Direction.WEST
        else:
            self.direction = Direction.EAST
                
    def rotate_position(self, old_width, old_height):
        # Cập nhật vị trí sau khi xoay mê cung
        x, y = self.pos
        # Công thức xoay: (x, y) -> (y, old_width - 1 - x)
        new_x = y
        new_y = old_width - 1 - x
        self.pos = (new_x, new_y)
        
        # Cập nhật hướng sau khi xoay
        if self.direction == Direction.EAST:
            self.direction = Direction.SOUTH
        elif self.direction == Direction.WEST:
            self.direction = Direction.NORTH
        elif self.direction == Direction.NORTH:
            self.direction = Direction.EAST
        elif self.direction == Direction.SOUTH:
            self.direction = Direction.WEST
                
    def getPosition(self):
        return self.pos
        
    def getDirection(self):
        return self.direction

class BasePacmanGame:
    # Base class chung cho cả chế độ thủ công và AI
    
    def __init__(self, layout, is_manual=False):
        # Khởi tạo game với layout đã cho
        self.layout = layout
        # Đánh dấu chế độ thủ công để không tự động teleport
        self.layout.manual_mode = is_manual
        
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
    
    def isMagicalPie(self, pos):
        # Kiểm tra xem vị trí có phải là bánh kỳ diệu hay không.
        return pos in self.layout.magical_pies
    
    def getMagicalPies(self):
        # Trả về danh sách các bánh kỳ diệu.
        return self.layout.magical_pies
    
    def isWall(self, pos):
        # Kiểm tra xem vị trí có phải là tường hay không.
        try:
            return self.layout.walls.get_at(pos) == (255, 255, 255)
        except (IndexError, ValueError):
            return False
    
    def isGoalState(self, state):
        # Kiểm tra xem trạng thái hiện tại có phải là mục tiêu hay không.
        pos = state.getPosition()
        food_eaten = not any(self.isFood((x, y)) for y in range(self.layout.height) for x in range(self.layout.width))
        at_exit = pos in getattr(self.layout, 'exit_gates', [])
        return food_eaten and at_exit

    def update(self):
        # Cập nhật trạng thái game
        # KHÔNG giảm power_timer ở đây vì update() được gọi mỗi frame
        # power_timer sẽ được giảm trong move_pacman() khi thực sự di chuyển
        
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
        
        # Nếu có power, ăn tường khi Pacman đi qua trong 5 bước
        if self.power_timer > 0:
            # Ăn tường tại vị trí hiện tại nếu có
            self.try_eat_wall_at_current_position(pos)
        
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

    def rotate_maze_and_update_coordinates(self):
        # Xoay ma trận 90 độ và cập nhật tọa độ thức ăn, magical_pies
        
        # Lưu kích thước cũ trước khi xoay
        old_width = self.layout.width
        old_height = self.layout.height
        
        # Lưu trữ tọa độ hiện tại của thức ăn và magical_pies
        current_food_positions = []
        current_magical_pie_positions = []
        
        # Thu thập tọa độ thức ăn hiện tại
        for y in range(self.layout.height):
            for x in range(self.layout.width):
                try:
                    if self.layout.food.get_at((x, y)) == (255, 255, 255):
                        current_food_positions.append((x, y))
                except (IndexError, ValueError):
                    continue
        
        # Thu thập tọa độ magical_pies hiện tại
        current_magical_pie_positions = list(self.layout.magical_pies)
        
        # Xoay ma trận
        self.layout.rotate_maze_simple()
        
        # Cập nhật tọa độ thức ăn sau khi xoay
        self.update_food_coordinates_after_rotation(current_food_positions, old_width, old_height)
        
        # Cập nhật tọa độ magical_pies sau khi xoay
        self.update_magical_pie_coordinates_after_rotation(current_magical_pie_positions, old_width, old_height)
        
        # Cập nhật vị trí Pacman sau khi xoay
        self.update_pacman_position_after_rotation(old_width, old_height)
        
        # Cập nhật các góc teleport sau khi xoay
        self.update_teleport_corners_after_rotation(old_width, old_height)
        # --- THÊM DÒNG NÀY ---
        self.update_opposite_corners_after_rotation(old_width, old_height)

    
    # Trong file base_pacman.py, bên trong class BasePacmanGame

    def update_opposite_corners_after_rotation(self, old_width, old_height):
        # Cập nhật các cổng dịch chuyển (opposite_corners) trong layout
        # sau khi xoay 90 độ theo chiều kim đồng hồ.
        print("Updating opposite corners...")
        old_corners = self.layout.opposite_corners
        new_corners = {}

        # Công thức xoay: (x, y) -> (new_x, new_y)
        # new_x = old_height - 1 - y
        # new_y = x

        for (x1, y1), (x2, y2) in old_corners.items():
            # Xoay vị trí key (x1, y1)
            new_x1 = old_height - 1 - y1
            new_y1 = x1

            # Xoay vị trí value (x2, y2)
            new_x2 = old_height - 1 - y2
            new_y2 = x2

            # Thêm vào dict mới
            new_key = (new_x1, new_y1)
            new_value = (new_x2, new_y2)

            # Đảm bảo key/value nằm trong bounds mới
            if (0 <= new_key[0] < self.layout.width and 0 <= new_key[1] < self.layout.height and
                0 <= new_value[0] < self.layout.width and 0 <= new_value[1] < self.layout.height):
                new_corners[new_key] = new_value

        # Cập nhật dict corners trong layout
        self.layout.opposite_corners = new_corners
        print(f"New opposite corners: {self.layout.opposite_corners}")


    def update_food_coordinates_after_rotation(self, old_food_positions, old_width, old_height):
        # Cập nhật tọa độ thức ăn sau khi xoay ma trận 90 độ
        # Xóa tất cả thức ăn cũ
        self.layout.food.fill((0, 0, 0))
        
        # Cập nhật tọa độ thức ăn theo công thức xoay 90 độ theo chiều kim đồng hồ
        for x, y in old_food_positions:
            # Xoay tọa độ 90 độ theo chiều kim đồng hồ
            new_x = old_height - 1 - y
            new_y = x
            
            # Đảm bảo tọa độ mới trong bounds của ma trận mới
            if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
                self.layout.food.set_at((new_x, new_y), (255, 255, 255))

    def update_magical_pie_coordinates_after_rotation(self, old_magical_pie_positions, old_width, old_height):
        # Cập nhật tọa độ magical_pies sau khi xoay ma trận 90 độ
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
        # Cập nhật vị trí Pacman sau khi xoay ma trận 90 độ
        old_pos = self.state.getPosition()
        old_x, old_y = old_pos
        
        # Xoay tọa độ 90 độ theo chiều kim đồng hồ
        new_x = old_height - 1 - old_y
        new_y = old_x
        
        # Đảm bảo tọa độ mới trong bounds của ma trận mới
        if 0 <= new_x < self.layout.width and 0 <= new_y < self.layout.height:
            self.state.pos = (new_x, new_y)

    def update_teleport_corners_after_rotation(self, old_width, old_height):
        # Cập nhật các góc teleport sau khi xoay ma trận 90 độ
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

    def eat_wall_at_position(self, pos):
        # Ăn tường tại vị trí hiện tại khi có power
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

    def try_eat_wall_at_current_position(self, pos):
        # Chỉ ăn tường tại vị trí hiện tại khi có power (không ăn xung quanh)
        x, y = pos
        
        # Chỉ ăn tường tại vị trí hiện tại nếu có
        if self.isWall(pos):
            self.eat_wall_at_position(pos)

    def show_win_effect(self):
        # Hiệu ứng thắng cuộc
        self.layout.renderer.draw_win_message()
        pygame.display.flip()
        time.sleep(2)

    def show_game_over_effect(self):
        # Hiệu ứng thua cuộc
        self.layout.renderer.draw_game_over_message()
        pygame.display.flip()
        time.sleep(2)
