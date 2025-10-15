import pygame
import time
import ast

# Khởi tạo Pygame
pygame.init()

# Kích thước ô
CELL_SIZE = 30
WIDTH = 36  # Số cột
HEIGHT = 18  # Số hàng

# Màu sắc
WHITE = (0,0,0)
GREEN = (0, 255, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 255, 0)
TEXT_COLOR = (255, 255, 255)

# Tải hình ảnh tường
wall_image = pygame.transform.scale(pygame.image.load("../assets/wall.png"), (CELL_SIZE, CELL_SIZE))
bery = pygame.transform.scale(pygame.image.load("../assets/pngwing.com.png"), (CELL_SIZE, CELL_SIZE))
God_cake = pygame.transform.scale(pygame.image.load("../assets/8dc940a2-bbe6-463a-8ba2-4ab535ee61da-removebg-preview.png"), (CELL_SIZE, CELL_SIZE))

# Khởi tạo cửa sổ game
screen = pygame.display.set_mode((WIDTH * CELL_SIZE, HEIGHT * CELL_SIZE + 50))
pygame.display.set_caption("Pacman A* Visualization")

# Tải hình ảnh Pacman theo hướng
pacman_images = {
    "RIGHT": [pygame.transform.scale(pygame.image.load(f"../assets/player_images/{i}.png"), (CELL_SIZE, CELL_SIZE)) for i in range(1, 5)],
    "LEFT": [pygame.transform.flip(pygame.transform.scale(pygame.image.load(f"../assets/player_images/{i}.png"), (CELL_SIZE, CELL_SIZE)), True, False) for i in range(1, 5)],
    "UP": [pygame.transform.rotate(pygame.transform.scale(pygame.image.load(f"../assets/player_images/{i}.png"), (CELL_SIZE, CELL_SIZE)), 90) for i in range(1, 5)],
    "DOWN": [pygame.transform.rotate(pygame.transform.scale(pygame.image.load(f"../assets/player_images/{i}.png"), (CELL_SIZE, CELL_SIZE)), -90) for i in range(1, 5)],
}

# Đọc file bản đồ
def load_maze(filename):
    with open(filename, "r") as f:
        maze = [list(line.strip()) for line in f]
    
    pacman_pos = None
    food_count = 0
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            if cell == "P":
                pacman_pos = (i, j)
                maze[i][j] = " "  # Xóa ký hiệu P khỏi bản đồ
            elif cell == ".":
                food_count += 1
    
    return maze, pacman_pos, food_count

# Đọc đường đi của Pacman từ file
def load_pacman_path(filename):
    with open(filename, "r") as f:
        return ast.literal_eval(f.read().strip())

# Vẽ mê cung
def draw_maze(maze, pacman_x, pacman_y, frame_index, direction, food_count, wall_passes):
    screen.fill(WHITE)
    # Hiển thị thông tin thức ăn còn lại, số bước xuyên tường và vị trí Pacman
    font = pygame.font.Font(None, 30)
    screen_width = WIDTH * CELL_SIZE
    
    food_text = font.render(f" Food Remaining: {food_count}", True, TEXT_COLOR)
    wall_pass_text = font.render(f" Wall Passes: {wall_passes}", True, TEXT_COLOR)
    pacman_pos_text = font.render(f" Pacman Position: ({pacman_x // CELL_SIZE}, {pacman_y // CELL_SIZE})", True, TEXT_COLOR)
    
    screen.blit(food_text, (10, 10))  # Căn trái
    screen.blit(wall_pass_text, ((screen_width - wall_pass_text.get_width()) // 2, 10))  # Căn giữa
    screen.blit(pacman_pos_text, (screen_width - pacman_pos_text.get_width() - 10, 10))  # Căn phải
    
    for i, row in enumerate(maze):
        for j, cell in enumerate(row):
            x, y = j * CELL_SIZE, i * CELL_SIZE + 50
            if cell == "%":
                screen.blit(wall_image, (x, y))
            elif cell == ".":
                screen.blit(bery, (x, y))
            elif cell == "O":
                screen.blit(God_cake, (x, y))
    
    # Vẽ Pacman với hoạt ảnh theo hướng di chuyển
    pacman_image = pacman_images[direction][frame_index % len(pacman_images[direction])]
    screen.blit(pacman_image, (pacman_y, pacman_x + 50))
    pygame.display.flip()
    
# Chạy chương trình
def run():
    maze, pacman_pos, food_count = load_maze("../input/task02_pacman_example_map.txt")
    pacman_path = load_pacman_path("../output/Path.txt")
    clock = pygame.time.Clock()
    running = True
    paused = False
    frame_index = 0
    prev_px, prev_py = pacman_pos
    direction = "RIGHT"  # Hướng mặc định
    wall_passes = 0  # Chỉ có thể xuyên tường sau khi ăn bánh thần
    
    for px, py in pacman_path:
        while paused:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                    paused = False
                elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                    paused = not paused
            clock.tick(10)
        dx, dy = px - prev_px, py - prev_py
        prev_px, prev_py = px, py
        
        if dx == 1:
            direction = "DOWN"
        elif dx == -1:
            direction = "UP"
        elif dy == 1:
            direction = "RIGHT"
        elif dy == -1:
            direction = "LEFT"
        
        if maze[px][py] == ".":
            maze[px][py] = " "
            food_count -= 1
        elif maze[px][py] == "O":
            maze[px][py] = " "
            wall_passes = 6
        
        if maze[px][py] == "%" or maze[px][py] == " " and wall_passes > 0:
            wall_passes -= 1
        
        draw_maze(maze, px * CELL_SIZE, py * CELL_SIZE, frame_index, direction, food_count, wall_passes)
        frame_index += 1
        clock.tick(3)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                break
            elif event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE:
                paused = not paused
        
        if not running:
            break
    
    print("🎉 Pacman đã hoàn thành nhiệm vụ!")
    time.sleep(2)
    pygame.quit()

if __name__ == "__main__":
    run()