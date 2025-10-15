from action import Direction
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
        # Xử lý teleport trước khi áp dụng vector
        if (x, y) in opposite_corners:
            x, y = opposite_corners[(x, y)]
            
        dx, dy = vector
        direction = next((d for d, v in Direction._directions.items() if v == (dx, dy)), Direction.STOP)
        if direction == Direction.STOP:
            direction = self.direction
        
        # Tính vị trí mới và kiểm tra giới hạn
        new_x, new_y = x + dx, y + dy
        new_pos = (new_x, new_y)
        return State(new_pos, direction, self.food_grid, self.power_steps)

    def __lt__(self, other):
        return (self.pos, self.food_grid, self.power_steps) < (other.pos, other.food_grid, other.power_steps)