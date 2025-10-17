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
        
        # Định nghĩa 4 góc và mapping
        corners = {
            (1, 1): 1,      # Góc trái trên
            (34, 1): 2,     # Góc phải trên  
            (1, 16): 3,     # Góc trái dưới
            (34, 16): 4     # Góc phải dưới
        }
        
        # Chỉ xử lý teleport nếu ở vị trí teleport hợp lệ
        if current_pos not in corners:
            return
        
        current_corner = corners[current_pos]
        
        # Shift + T: Dịch chuyển chéo góc
        if keys[pygame.K_LSHIFT] and keys[pygame.K_t]:
            if current_corner == 1:  # (1,1) -> (34,16)
                self.state.pos = (34, 16)
            elif current_corner == 4:  # (34,16) -> (1,1)
                self.state.pos = (1, 1)
            elif current_corner == 2:  # (34,1) -> (1,16)
                self.state.pos = (1, 16)
            elif current_corner == 3:  # (1,16) -> (34,1)
                self.state.pos = (34, 1)
        
        # T + 1: Dịch chuyển đến góc 1 (1,1)
        elif keys[pygame.K_t] and keys[pygame.K_1]:
            if current_corner != 1:  # Không dịch chuyển nếu đã ở góc 1
                self.state.pos = (1, 1)
        
        # T + 2: Dịch chuyển đến góc 2 (34,1)
        elif keys[pygame.K_t] and keys[pygame.K_2]:
            if current_corner != 2:  # Không dịch chuyển nếu đã ở góc 2
                self.state.pos = (34, 1)
        
        # T + 3: Dịch chuyển đến góc 3 (1,16)
        elif keys[pygame.K_t] and keys[pygame.K_3]:
            if current_corner != 3:  # Không dịch chuyển nếu đã ở góc 3
                self.state.pos = (1, 16)
        
        # T + 4: Dịch chuyển đến góc 4 (34,16)
        elif keys[pygame.K_t] and keys[pygame.K_4]:
            if current_corner != 4:  # Không dịch chuyển nếu đã ở góc 4
                self.state.pos = (34, 16)

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
        
        # Lưu hành động và vị trí
        self.actions_log.append(self.current_direction)
        self.position_log.append(f"Step {self.step_count + 1}: {self.current_direction} at {self.state.getPosition()}")
        
        self.step_count += 1

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

    def get_speed_description(self):
        """Trả về mô tả tốc độ hiện tại"""
        if self.move_delay == 0:
            return "Cuc nhanh (delay=0)"
        elif self.move_delay == 1:
            return "Nhanh (delay=1)"
        elif self.move_delay == 2:
            return "Trung binh (delay=2)"
        elif self.move_delay == 3:
            return "Cham (delay=3)"
        elif self.move_delay == 4:
            return "Rat cham (delay=4)"
        else:
            return f"Rat rat cham (delay={self.move_delay})"

    def show_win_effect(self):
        """Hiệu ứng thắng cuộc"""
        print("\n" + "="*60)
        print("*** CHUC MUNG! BAN DA HOAN THANH GAME! ***")
        print("="*60)
        print(f"DIEM SO: {self.score}")
        print(f"SO BUOC: {self.step_count}")
        print(f"THUC AN DA AN: {self.calculate_food_eaten()}")
        print(f"BANH KY DIEU DA AN: {self.calculate_pies_eaten()}")
        print("="*60)
        print("*** CAM ON BAN DA CHOI! ***")
        print("="*60)
        
        # Hiệu ứng đóng game với delay
        self.close_game_with_effect("WIN")

    def show_game_over_effect(self):
        """Hiệu ứng thua cuộc"""
        print("\n" + "="*60)
        print("*** GAME OVER! PACMAN DA BI MA BAT! ***")
        print("="*60)
        print(f"DIEM SO: {self.score}")
        print(f"SO BUOC: {self.step_count}")
        print(f"THUC AN DA AN: {self.calculate_food_eaten()}")
        print(f"BANH KY DIEU DA AN: {self.calculate_pies_eaten()}")
        print("="*60)
        print("*** CHUC BAN MAY MAN LAN SAU! ***")
        print("="*60)
        
        # Hiệu ứng đóng game với delay
        self.close_game_with_effect("GAME_OVER")

    def calculate_food_eaten(self):
        """Tính số thức ăn đã ăn"""
        total_food = 0
        remaining_food = 0
        
        # Đếm tổng số thức ăn ban đầu
        for y in range(self.layout.height):
            for x in range(self.layout.width):
                if (y < len(self.layout.layoutData) and 
                    x < len(self.layout.layoutData[y]) and 
                    self.layout.layoutData[y][x] == '.'):
                    total_food += 1
        
        # Đếm thức ăn còn lại
        for y in range(self.layout.height):
            for x in range(self.layout.width):
                try:
                    if (0 <= x < self.layout.food.get_width() and 
                        0 <= y < self.layout.food.get_height() and 
                        self.layout.food.get_at((x, y)) == (255, 255, 255)):
                        remaining_food += 1
                except (IndexError, ValueError):
                    continue
        
        return total_food - remaining_food

    def calculate_pies_eaten(self):
        """Tính số bánh kỳ diệu đã ăn"""
        total_pies = 0
        for y in range(self.layout.height):
            for x in range(self.layout.width):
                if (y < len(self.layout.layoutData) and 
                    x < len(self.layout.layoutData[y]) and 
                    self.layout.layoutData[y][x] == 'o'):
                    total_pies += 1
        
        return total_pies - len(self.layout.magical_pies)

    def close_game_with_effect(self, effect_type):
        """Đóng game với hiệu ứng"""
        import time
        
        # Hiệu ứng nhấp nháy màn hình
        for i in range(3):
            try:
                current_pos = self.state.getPosition()
                if effect_type == "WIN":
                    # Hiệu ứng thắng: màu xanh lá
                    self.layout.renderer.clear_screen()
                    self.layout.renderer.draw_walls(self.layout.walls, True)
                    self.layout.renderer.draw_food(self.layout.food)
                    self.layout.renderer.draw_magical_pies(self.layout.magical_pies)
                    self.layout.renderer.draw_ghosts(self.layout.ghosts)
                    self.layout.renderer.draw_exit_gates(self.layout.exit_gates)
                    # Tạo một Surface đơn giản cho Pacman
                    pacman_surface = pygame.Surface((20, 20))
                    pacman_surface.fill((255, 255, 0))
                    self.layout.renderer.draw_pacman(current_pos, pacman_surface, True)
                    self.layout.renderer.draw_win_message()
                else:
                    # Hiệu ứng thua: màu đỏ
                    self.layout.renderer.clear_screen()
                    self.layout.renderer.draw_walls(self.layout.walls, False)
                    self.layout.renderer.draw_food(self.layout.food)
                    self.layout.renderer.draw_magical_pies(self.layout.magical_pies)
                    self.layout.renderer.draw_ghosts(self.layout.ghosts)
                    self.layout.renderer.draw_exit_gates(self.layout.exit_gates)
                    # Tạo một Surface đơn giản cho Pacman
                    pacman_surface = pygame.Surface((20, 20))
                    pacman_surface.fill((255, 255, 0))
                    self.layout.renderer.draw_pacman(current_pos, pacman_surface, False)
                    self.layout.renderer.draw_game_over_message()
                
                self.layout.renderer.update_display()
                time.sleep(0.5)
                
                # Màn hình tối
                self.layout.renderer.clear_screen()
                self.layout.renderer.update_display()
                time.sleep(0.3)
                
            except pygame.error:
                break
        
        # Đóng game
        pygame.quit()

    def run(self):
        """Chạy game với điều khiển thủ công"""
        clock = pygame.time.Clock()
        running = True
        
        print("=== CHE DO DIEU KHIEN THU CONG ===")
        print("Su dung phim mui ten hoac WASD de di chuyen")
        print("Phim SPACE de dung")
        print("Phim ESC de thoat")
        print("")
        print("DIEU KHIEN CAI TIEN:")
        print("- Di chuyen lien tuc: Giu phim de di chuyen")
        print("- Re nhanh: Nhan phim huong truoc khi den nga re")
        print("- + / -: Tang/giam toc do di chuyen (mac dinh: vua phai)")
        print("- Toc do mac dinh da duoc dieu chinh de can bang hon")
        print("")
        print("TINH NANG DAC BIET:")
        print("- An banh ky dieu (o): Co the an tuong trong 5 buoc")
        print("- Di qua tuong: Tuong se bien mat va co them 5 diem")
        print("- Chi hoat dong khi co power (5 buoc sau khi an banh ky dieu)")
        print("")
        print("TELEPORT THU CONG:")
        print("- Shift + T: Dich chuyen cheo goc")
        print("  + (1,1) <-> (34,16)")
        print("  + (34,1) <-> (1,16)")
        print("- T + 1: Dich chuyen den goc 1 (1,1)")
        print("- T + 2: Dich chuyen den goc 2 (34,1)")
        print("- T + 3: Dich chuyen den goc 3 (1,16)")
        print("- T + 4: Dich chuyen den goc 4 (34,16)")
        print("- Chi hoat dong tai cac goc teleport")
        print("- Khong dich chuyen neu dang o goc dich")
        print("")
        print("Muc tieu: An het thuc an va den cong exit (mau xanh)")
        print("=" * 50)
        
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
