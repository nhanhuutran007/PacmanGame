from maze import Maze

class Pacman:
    def __init__(self, x, y, remaining_food, pie_steps, g, parent, maze: Maze):
        self.x = x  # Hàng (row)
        self.y = y  # Cột (column)
        self.remaining_food = remaining_food  # Tập hợp thức ăn còn lại (set)
        self.pie_steps = pie_steps  # Số bước xuyên tường còn lại
        self.g = g  # Chi phí từ trạng thái ban đầu
        self.parent = parent  # Node cha để truy vết
        self.maze = maze  # Tham chiếu đến Maze để kiểm tra logic
        self.state = (self.x, self.y, frozenset(self.remaining_food), self.pie_steps)  # Trạng thái duy nhất
        
        # Tính heuristic trong hàm riêng nếu cần, hiện tại để AStar xử lý
        self.h = 0
        self.f = 0

    def __lt__(self, other):
        return self.f < other.f  # Để heapq so sánh dựa trên f

    # Kiểm tra vị trí có hợp lệ không
    def is_valid(self, x, y):
        return 0 <= x <= self.maze.x_max() + 1 and 0 <= y <= self.maze.y_max() + 1

    # Kiểm tra tường
    def is_wall(self, x, y):
        return (x, y) in self.maze.find_walls()

    def get_successors(self):
            successors = []
            directions =  {"North": (-1, 0),"South": (1, 0),"West": (0, -1),"East": (0, 1),"Stop": (0, 0)}
            teleports = self.maze.find_teleports()


            for action, (dx, dy) in directions.items():
                new_x, new_y = self.x + dx, self.y + dy
                
                if not self.is_valid(new_x, new_y):
                    continue
                
                if self.is_wall(new_x, new_y) and self.pie_steps <= 0:
                    continue
                
                new_remaining_food = set(self.remaining_food)
                new_pie_steps = self.pie_steps - 1 if self.pie_steps > 0 else 0

                if self.maze.is_pie(new_x, new_y):
                    new_pie_steps = max(new_pie_steps, 5)

                if (new_x, new_y) in new_remaining_food:
                    new_remaining_food.remove((new_x, new_y))

                if (new_x, new_y) in teleports and action== 'Stop':
                    teleport_x, teleport_y = teleports[(new_x, new_y)]

                    intermediate_successor = Pacman(new_x, new_y, new_remaining_food, new_pie_steps, self.g , self, self.maze)
                    successors.append(intermediate_successor)


                    new_x, new_y = teleport_x, teleport_y
                                


                successor = Pacman(new_x, new_y, new_remaining_food, new_pie_steps, self.g + 1, self, self.maze)
                successors.append(successor)

            return successors



    # Kiểm tra xem có đạt mục tiêu không
    def is_goal(self):
        return not self.remaining_food  # Goal khi không còn thức ăn

    # Trả về trạng thái để dùng làm id hoặc so sánh
    def get_state(self):
        return self.state
    
'''Đã sửa'''    
# Đối tượng này cần viết lại theo đúng định dạng
# không gọi từ file maze, lớp này độc lập
'''
2. Xây dựng Không gian trạng thái (State Space)
Mỗi trạng thái có dạng:
State=(x,y,remaining_food,pie_steps)State = (x, y, remaining\_food, pie\_steps)State=(x,y,remaining_food,pie_steps)
(x, y): Vị trí của Pacman.
remaining_food: Danh sách thức ăn còn lại.
pie_steps: Số bước còn lại có thể đi xuyên tường (nếu đã ăn bánh thần).
Hành động hợp lệ (Action)
Pacman có thể đi North, South, East, West.
Nếu đến vị trí có thức ăn (.), nó sẽ bị xóa khỏi remaining_food.
Nếu Pacman ăn bánh thần (O), pie_steps = 5.
Nếu pie_steps > 0, Pacman có thể đi xuyên tường (%).
Chi phí di chuyển (Cost)
Mỗi bước di chuyển có cost = 1.
Bánh thần không làm thay đổi cost, chỉ ảnh hưởng đến khả năng đi xuyên tường.
'''
