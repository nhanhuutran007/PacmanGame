from visualize import Direction
class State:
    def __init__(self, pos, direction, food_grid, power_steps=0):
        self.pos = pos
        self.direction = direction
        self.food_grid = food_grid
        self.power_steps = power_steps

    def getPosition(self):
        return self.pos

    def getDirection(self):
        return self.direction
    
    

    def generateState(self, vector, opposite_corners):
            x, y = self.pos
            dx, dy = vector
            
            # Lấy direction từ vector
            direction = next((d for d, v in Direction._directions.items() if v == (dx, dy)), Direction.STOP)

            # 1. Xử lý Teleport (chỉ khi AI/game chủ động gọi teleport)
            # AI (agent.py) dùng (vector=(0,0), corners=dict)
            # Manual (pacman.py) dùng (vector=(0,0), corners={}) -> không teleport
            if direction == Direction.STOP and opposite_corners and (x, y) in opposite_corners:
                # Đây là một hành động teleport
                new_x, new_y = opposite_corners[(x, y)]
                new_pos = (new_x, new_y)
                # Giữ nguyên direction cũ (hoặc set là STOP đều được, tùy game logic)
                new_direction = Direction.STOP 
            else:
                # 2. Xử lý di chuyển bình thường (không teleport)
                new_x, new_y = x + dx, y + dy
                new_pos = (new_x, new_y)
                new_direction = direction
            
            # Cập nhật direction (nếu không di chuyển thì giữ hướng cũ)
            if new_direction == Direction.STOP:
                new_direction = self.direction
                
            return State(new_pos, new_direction, self.food_grid, self.power_steps)

    

    def __lt__(self, other):
        return (self.pos, self.food_grid, self.power_steps) < (other.pos, other.food_grid, other.power_steps)