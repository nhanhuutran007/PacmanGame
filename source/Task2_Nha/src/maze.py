import os
from utils.path_manager import get_input_file, get_output_file

class Maze:
    def __init__(self, filename):
        file_path = filename  # Đường dẫn đến tệp mê cung
        print(f"Loading maze from file: {file_path}")
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File {file_path} not found! Check your input folder.")
        
        self.grid = []
        self.food_positions = []
        self.wall_positions = []

        with open(file_path, "r") as f:
            for i, line in enumerate(f):
                row = list(line.strip())
                self.grid.append(row)
                for j, cell in enumerate(row):
                    if cell == '.':
                        self.food_positions.append((i, j))
                    elif cell == '%':
                        self.wall_positions.append((i, j))
                    elif cell not in ['.', '%', 'P', 'O', ' ']:
                        raise ValueError(f"Invalid character '{cell}' in maze file at ({i}, {j})")
        
    #Tìm vị trí pacman
    def find_pacman(self):
        for i, row in enumerate(self.grid):
            for j, cell in enumerate(row):
                if cell == 'P':
                    return (i, j)
        return None
    #Tìm vị trí thức ăn
    def find_food(self):
        return self.food_positions
    #Tìm vị trí tường
    def find_walls(self):
        return self.wall_positions
    #Kiểm tra có phải là tường không
    def is_wall(self, x, y):
        return (x, y) in self.wall_positions
    #Tìm vị trí dịch chuyển
    def find_teleports(self):
        return {
            (1, 1): (self.x_max(), self.y_max()),
            (self.x_max(), self.y_max()): (1, 1),
            (1, self.y_max()): (self.x_max(), 1),
            (self.x_max(), 1): (1, self.y_max())
        }
    #Kiểm tra bánh thần
    def is_pie(self, x, y):
        if 0 <= x <= self.x_max() and 0 <= y <= self.y_max():
            return self.grid[x][y] == 'O'
        return False
    
    def x_max(self):
        return len(self.grid) - 2 
    
    def y_max(self):
        return len(self.grid[0]) - 2  

    def print_maze(self):
        for row in self.grid:
            print("".join(row))

