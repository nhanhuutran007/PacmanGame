from action import Direction

class Ghost:
    def __init__(self, pos, direction=Direction.EAST):
        self.pos = pos
        self.direction = direction  # Ghost chỉ di chuyển ngang (EAST hoặc WEST)
        self.move_timer = 0  # Timer để kiểm soát tốc độ di chuyển
        self.move_delay = 2  # Số frame cần chờ giữa các lần di chuyển (càng lớn càng chậm)
        
    def move(self, layout):
        """Di chuyển ghost theo hướng hiện tại, đổi hướng khi gặp tường"""
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
                    self._reverse_direction()
                    self.move_timer = 0  # Reset timer sau khi đổi hướng
            except (IndexError, ValueError):
                # Nếu có lỗi truy cập pixel, đổi hướng
                self._reverse_direction()
                self.move_timer = 0  # Reset timer sau khi đổi hướng
        else:
            # Nếu ra ngoài bounds, đổi hướng
            self._reverse_direction()
            self.move_timer = 0  # Reset timer sau khi đổi hướng
            
    def _reverse_direction(self):
        """Đổi hướng di chuyển"""
        if self.direction == Direction.EAST:
            self.direction = Direction.WEST
        else:
            self.direction = Direction.EAST
                
    def rotate_position(self, old_width, old_height):
        """Cập nhật vị trí sau khi xoay mê cung"""
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
