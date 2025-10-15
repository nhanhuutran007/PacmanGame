import heapq
from state import State
from action import Direction
from game import Layout

def simulate_ghost_states(layout: Layout, ghosts, step: int):
    """Mô phỏng trạng thái ma (x, y, direction) sau 'step' bước với phản xạ ở tường.
    Giả định ma chỉ di chuyển ngang (EAST/WEST) như hiện tại.
    Trả về list các tuple (x, y, direction) ở bước 'step'.
    """
    states = []
    width, height = layout.width, layout.height
    for ghost in ghosts:
        try:
            x, y = ghost.getPosition()
            direction = ghost.getDirection()
            dx, dy = Direction._directions[direction]
            for _ in range(step):
                nx, ny = x + dx, y + dy
                within = (0 <= nx < width and 0 <= ny < height)
                is_wall = False
                if within:
                    try:
                        is_wall = layout.walls.get_at((nx, ny)) == (255, 255, 255)
                    except (IndexError, ValueError):
                        is_wall = True
                if (not within) or is_wall:
                    # reverse direction
                    direction = Direction.WEST if direction == Direction.EAST else Direction.EAST
                    dx, dy = Direction._directions[direction]
                    nx, ny = x + dx, y + dy
                    within2 = (0 <= nx < width and 0 <= ny < height)
                    if within2:
                        try:
                            if layout.walls.get_at((nx, ny)) == (255, 255, 255):
                                # stay in place if still wall
                                nx, ny = x, y
                        except (IndexError, ValueError):
                            nx, ny = x, y
                    else:
                        nx, ny = x, y
                x, y = nx, ny
            states.append((x, y, direction))
        except Exception:
            continue
    return states

def simulate_single_ghost_state(layout: Layout, ghost, step: int):
    """Mô phỏng 1 con ma sau 'step' bước, trả về (x, y, direction)."""
    width, height = layout.width, layout.height
    try:
        x, y = ghost.getPosition()
        direction = ghost.getDirection()
        dx, dy = Direction._directions[direction]
        for _ in range(step):
            nx, ny = x + dx, y + dy
            within = (0 <= nx < width and 0 <= ny < height)
            is_wall = False
            if within:
                try:
                    is_wall = layout.walls.get_at((nx, ny)) == (255, 255, 255)
                except (IndexError, ValueError):
                    is_wall = True
            if (not within) or is_wall:
                direction = Direction.WEST if direction == Direction.EAST else Direction.EAST
                dx, dy = Direction._directions[direction]
                nx, ny = x + dx, y + dy
                within2 = (0 <= nx < width and 0 <= ny < height)
                if within2:
                    try:
                        if layout.walls.get_at((nx, ny)) == (255, 255, 255):
                            nx, ny = x, y
                    except (IndexError, ValueError):
                        nx, ny = x, y
                else:
                    nx, ny = x, y
            x, y = nx, ny
        return (x, y, direction)
    except Exception:
        return None

def compute_safe_entry_step(layout: Layout, ghost, cell, start_step: int, horizon: int = 20):
    """Tính bước s_safe tối thiểu để Pacman đi vào 'cell' an toàn:
    - s_hit: bước đầu tiên ma chiếm ô cell (nếu có)
    - s_safe: bước đầu tiên SAU s_hit khi ma đã chạm tường và đảo chiều (đi khỏi làn)
    Trả về s_safe, hoặc None nếu không cần chờ.
    """
    cx, cy = cell
    prev_dir = None
    s_hit = None
    for s in range(start_step, start_step + horizon + 1):
        state = simulate_single_ghost_state(layout, ghost, s)
        if state is None:
            continue
        gx, gy, gdir = state
        if gx == cx and gy == cy and s_hit is None:
            s_hit = s
        if prev_dir is not None and gdir != prev_dir:
            # phát hiện đảo chiều tại bước s
            if s_hit is not None and s > s_hit:
                return s
        prev_dir = gdir
    # nếu không bao giờ chạm cell, không cần chờ
    return None

def count_remaining_food(food_grid):
    """Đếm số lượng thức ăn còn lại"""
    return sum(sum(row) for row in food_grid)

def count_remaining_magical_pies(pos, magical_pies):
    """Đếm số lượng bánh kỳ diệu còn lại"""
    return len(magical_pies)

def calculate_maze_connectivity_factor(pos, corners):
    """Tính hệ số kết nối của mê cung dựa trên vị trí hiện tại"""
    # Kiểm tra xem có ở gần cổng dịch chuyển không
    for corner in corners:
        if abs(pos[0] - corner[0]) <= 2 and abs(pos[1] - corner[1]) <= 2:
            return 0.5  # Giảm chi phí nếu gần cổng dịch chuyển
    return 1.0

def find_nearest_food_distance(pos, food_grid):
    """Tìm khoảng cách đến thức ăn gần nhất"""
    min_distance = float('inf')
    for y in range(len(food_grid)):
        for x in range(len(food_grid[y])):
            if food_grid[y][x]:  # Nếu có thức ăn ở vị trí này
                distance = abs(pos[0] - x) + abs(pos[1] - y)
                min_distance = min(min_distance, distance)
    return min_distance if min_distance != float('inf') else 0

def find_nearest_magical_pie_distance(pos, magical_pies):
    """Tìm khoảng cách đến bánh kỳ diệu gần nhất"""
    if not magical_pies:
        return 0
    min_distance = min(abs(pos[0] - pie[0]) + abs(pos[1] - pie[1]) 
                      for pie in magical_pies)
    return min_distance

def calculate_magical_pie_value(pos, magical_pies, ghosts):
    """Tính giá trị của magical pie dựa trên vị trí và mức độ nguy hiểm từ ma"""
    if not magical_pies:
        return 0
    
    # Tìm magical pie gần nhất
    nearest_pie = min(magical_pies, key=lambda pie: abs(pos[0] - pie[0]) + abs(pos[1] - pie[1]))
    distance_to_pie = abs(pos[0] - nearest_pie[0]) + abs(pos[1] - nearest_pie[1])
    
    # Tính mức độ nguy hiểm hiện tại
    current_danger = calculate_ghost_danger_level(pos, ghosts, 3)
    
    # Nếu đang trong tình huống nguy hiểm, magical pie có giá trị cao hơn
    if current_danger > 10:
        return distance_to_pie * 0.3  # Ưu tiên cao khi nguy hiểm
    elif current_danger > 5:
        return distance_to_pie * 0.5  # Ưu tiên trung bình
    else:
        return distance_to_pie * 0.8  # Ưu tiên thấp khi an toàn

def predict_ghost_positions(ghosts, steps_ahead=3):
    """Dự đoán vị trí ma trong tương lai"""
    predicted_positions = []
    
    for ghost in ghosts:
        ghost_pos = ghost.getPosition()
        ghost_dir = ghost.getDirection()
        
        # Dự đoán vị trí ma trong các bước tiếp theo
        for step in range(1, steps_ahead + 1):
            dx, dy = Direction._directions[ghost_dir]
            predicted_x = ghost_pos[0] + dx * step
            predicted_y = ghost_pos[1] + dy * step
            predicted_positions.append((predicted_x, predicted_y))
    
    return predicted_positions

def calculate_ghost_danger_level(pos, ghosts, steps_ahead=7):
    """Tính mức độ nguy hiểm từ ma với dự đoán chính xác hơn và tránh tuyệt đối"""
    danger_level = 0
    
    for ghost in ghosts:
        ghost_pos = ghost.getPosition()
        ghost_dir = ghost.getDirection()
        
        # Dự đoán vị trí ma trong tương lai với nhiều bước hơn
        for step in range(1, steps_ahead + 1):
            dx, dy = Direction._directions[ghost_dir]
            predicted_x = ghost_pos[0] + dx * step
            predicted_y = ghost_pos[1] + dy * step
            
            # Kiểm tra bounds (giả sử kích thước mê cung)
            if (0 <= predicted_x < 50 and 0 <= predicted_y < 17):
                distance = abs(pos[0] - predicted_x) + abs(pos[1] - predicted_y)
            
            # Tăng mức độ nguy hiểm theo khoảng cách dự đoán
            if distance <= 1:
                danger_level += 100  # Cực kỳ nguy hiểm - tránh tuyệt đối
            elif distance <= 2:
                danger_level += 80   # Rất nguy hiểm
            elif distance <= 3:
                danger_level += 60   # Nguy hiểm
            elif distance <= 4:
                danger_level += 40   # Cảnh báo
            elif distance <= 5:
                danger_level += 20   # Chú ý
            elif distance <= 6:
                danger_level += 10   # Cảnh giác
            elif distance <= 7:
                danger_level += 5    # Theo dõi
    
    return danger_level

def find_safe_paths(pos, problem, steps_ahead=2):
    """Tìm các đường đi an toàn tránh ma"""
    safe_paths = []
    directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
    
    for direction in directions:
        dx, dy = Direction._directions[direction]
        new_pos = (pos[0] + dx, pos[1] + dy)
        
        # Kiểm tra bounds và tường
        if (0 <= new_pos[0] < problem.layout.width and 
            0 <= new_pos[1] < problem.layout.height and
            not problem.isWall(new_pos)):
            
            # Tính mức độ nguy hiểm của đường đi này
            danger_level = calculate_ghost_danger_level(new_pos, problem.layout.ghosts, steps_ahead)
            safe_paths.append((new_pos, direction, danger_level))
    
    # Sắp xếp theo mức độ an toàn (nguy hiểm thấp nhất trước)
    safe_paths.sort(key=lambda x: x[2])
    return safe_paths

def find_wall_eating_opportunities(pos, problem, magical_pies):
    """Tìm cơ hội ăn tường để tạo đường đi ngắn hơn"""
    opportunities = []
    
    if not magical_pies:
        return opportunities
    
    # Tìm magical pie gần nhất
    nearest_pie = min(magical_pies, key=lambda pie: abs(pos[0] - pie[0]) + abs(pos[1] - pie[1]))
    pie_distance = abs(pos[0] - nearest_pie[0]) + abs(pos[1] - nearest_pie[1])
    
    # Nếu magical pie quá xa, không ưu tiên
    if pie_distance > 8:
        return opportunities
    
    # Kiểm tra các tường xung quanh magical pie có thể ăn để tạo đường đi ngắn hơn
    directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
    
    for direction in directions:
        dx, dy = Direction._directions[direction]
        wall_pos = (nearest_pie[0] + dx, nearest_pie[1] + dy)
        
        # Kiểm tra bounds
        if (0 <= wall_pos[0] < problem.layout.width and 
            0 <= wall_pos[1] < problem.layout.height):
            
            # Nếu là tường và có thể tạo đường đi ngắn hơn
            if problem.isWall(wall_pos):
                # Tính giá trị của việc ăn tường này
                value = calculate_wall_eating_value(wall_pos, pos, problem)
                if value > 0:
                    opportunities.append((wall_pos, direction, value))
    
    # Sắp xếp theo giá trị (cao nhất trước)
    opportunities.sort(key=lambda x: x[2], reverse=True)
    return opportunities

def calculate_wall_eating_value(wall_pos, pacman_pos, problem):
    """Tính giá trị của việc ăn tường"""
    # Tính khoảng cách từ Pacman đến tường
    distance_to_wall = abs(pacman_pos[0] - wall_pos[0]) + abs(pacman_pos[1] - wall_pos[1])
    
    # Nếu tường quá xa, giá trị thấp
    if distance_to_wall > 6:
        return 0
    
    # Kiểm tra xem tường này có tạo đường đi ngắn hơn không
    # Bằng cách kiểm tra các ô xung quanh tường
    directions = [Direction.NORTH, Direction.SOUTH, Direction.EAST, Direction.WEST]
    accessible_areas = 0
    
    for direction in directions:
        dx, dy = Direction._directions[direction]
        check_pos = (wall_pos[0] + dx, wall_pos[1] + dy)
        
        # Kiểm tra bounds
        if (0 <= check_pos[0] < problem.layout.width and 
            0 <= check_pos[1] < problem.layout.height):
            
            # Nếu không phải tường, có thể tạo đường đi mới
            if not problem.isWall(check_pos):
                accessible_areas += 1
    
    # Giá trị dựa trên số vùng có thể tiếp cận và khoảng cách
    value = accessible_areas * 2 - distance_to_wall * 0.5
    return max(0, value)

def calculate_ghost_avoidance_factor(pos, ghosts):
    """Tính hệ số tránh ma dựa trên vị trí hiện tại và dự đoán tương lai"""
    avoidance_factor = 1.0
    
    # Tính mức độ nguy hiểm từ ma hiện tại
    current_danger = calculate_ghost_danger_level(pos, ghosts, 2)
    avoidance_factor += current_danger * 0.3
    
    # Kiểm tra từng ma riêng lẻ
    for ghost in ghosts:
        ghost_pos = ghost.getPosition()
        distance = abs(pos[0] - ghost_pos[0]) + abs(pos[1] - ghost_pos[1])
        
        # Nếu quá gần ma, tăng chi phí đáng kể
        if distance <= 1:
            avoidance_factor += 2.0  # Rất nguy hiểm
        elif distance <= 2:
            avoidance_factor += 1.0  # Nguy hiểm
        elif distance <= 3:
            avoidance_factor += 0.5  # Cảnh báo
    
    return avoidance_factor

# Hàm Heuristic mới không sử dụng Manhattan/Euclidean distance
def custom_heuristic(state, problem, corners):
    """
    Heuristic function dựa trên:
    1. Số lượng thức ăn còn lại
    2. Số lượng bánh kỳ diệu còn lại  
    3. Hệ số kết nối mê cung
    4. Hệ số tránh ma
    5. Trạng thái power của Pacman
    6. Khoảng cách đến cổng exit khi đã ăn hết thức ăn
    """
    pos = state.pos
    food_grid = state.food_grid
    power_steps = state.power_steps
    
    # Đếm số lượng thức ăn còn lại
    remaining_food = count_remaining_food(food_grid)
    
    # Đếm số lượng bánh kỳ diệu còn lại
    remaining_pies = count_remaining_magical_pies(pos, problem.getMagicalPies())
    
    # Tính hệ số kết nối mê cung
    connectivity_factor = calculate_maze_connectivity_factor(pos, corners)
    
    # Tính hệ số tránh ma
    ghost_factor = calculate_ghost_avoidance_factor(pos, problem.layout.ghosts)
    
    # Nếu không còn thức ăn, tính khoảng cách đến cổng exit gần nhất
    if remaining_food == 0:
        exit_gates = problem.layout.exit_gates
        if exit_gates:
            min_exit_distance = min(abs(pos[0] - exit[0]) + abs(pos[1] - exit[1]) 
                                  for exit in exit_gates)
            return min_exit_distance
        else:
            return 0
    
    # Tính khoảng cách đến thức ăn gần nhất
    nearest_food_distance = find_nearest_food_distance(pos, food_grid)
    
    # Tính giá trị của bánh kỳ diệu dựa trên tình huống hiện tại
    magical_pie_value = calculate_magical_pie_value(pos, problem.getMagicalPies(), problem.layout.ghosts)
    
    # Tìm cơ hội ăn tường để tạo đường đi ngắn hơn
    wall_eating_opportunities = find_wall_eating_opportunities(pos, problem, problem.getMagicalPies())
    wall_eating_bonus = 0
    if wall_eating_opportunities:
        # Ưu tiên ăn tường nếu có thể tạo đường đi ngắn hơn
        wall_eating_bonus = -wall_eating_opportunities[0][2] * 0.5
    
    # Tính heuristic dựa trên khoảng cách và số lượng
    base_cost = remaining_food * 2  # Chi phí cơ bản cho mỗi thức ăn
    
    # Thêm khoảng cách đến thức ăn gần nhất
    food_distance_cost = nearest_food_distance * 0.5
    
    # Thêm giá trị bánh kỳ diệu thông minh (ưu tiên dựa trên tình huống)
    pie_distance_cost = magical_pie_value
    
    # Giảm chi phí nếu có power (có thể đi xuyên tường)
    power_bonus = 0
    if power_steps > 0:
        power_bonus = -power_steps * 0.5
    
    # Áp dụng các hệ số
    final_cost = (base_cost + food_distance_cost + pie_distance_cost + power_bonus + wall_eating_bonus) * connectivity_factor * ghost_factor
    
    return max(0, final_cost)  # Đảm bảo heuristic không âm

# Hàm A* tìm kiếm các hành động tốt nhất cho game
def aStarSearch(problem, corners):
    # Khởi tạo trạng thái bắt đầu với food_grid và power hiện tại của game
    current_food = problem.getFoodGrid()
    current_power = getattr(problem, 'power_timer', 0)
    start_state = State(problem.getStartState(), Direction.STOP, current_food, current_power)
    
    frontier = []  # Danh sách các trạng thái chờ xử lý (dùng heap để lưu trữ theo chi phí)
    visited = {}  # Lưu các trạng thái đã thăm qua

    # Đưa trạng thái ban đầu vào trong frontier với chi phí 0
    heapq.heappush(frontier, (0, start_state, [], 0))  

    # Tiến hành duyệt frontier cho đến khi tìm thấy trạng thái mục tiêu
    while frontier:
        _ , current_state, actions, current_cost = heapq.heappop(frontier)
        
        # Nếu tìm được trạng thái mục tiêu (không còn thực phẩm)
        if problem.isGoalState(current_state):
            return actions, current_cost
        
        # Lưu lại trạng thái hiện tại đã thăm qua
        state_key = (current_state.pos, tuple(tuple(row) for row in current_state.food_grid), 
                    current_state.power_steps)
        
        # Nếu trạng thái đã thăm và chi phí hiện tại không tốt hơn trước đó, bỏ qua
        if state_key in visited and visited[state_key] <= current_cost:
            continue
            
        visited[state_key] = current_cost
        
        # Sử dụng hàm getSuccessors để lấy các trạng thái tiếp theo, truyền thêm food_grid và power_steps
        for next_pos, direction, step_cost in problem.getSuccessors(
            current_state.pos):
            # Nếu là tường và không có power_steps, bỏ qua
            if problem.isWall(next_pos) and not current_state.power_steps > 0:
                continue

            # Tránh ma theo thời gian: nếu va chạm ở bước kế tiếp, bỏ qua; nếu ở gần, phạt
            k = len(actions) + 1  # bước sẽ tới khi di chuyển tới next_pos
            
            # Giới hạn tìm kiếm để tăng tốc: chỉ kiểm tra va chạm trong tầm ngắn
            if k <= 15:  # chỉ kiểm tra trong 15 bước đầu
                predicted_states = simulate_ghost_states(problem.layout, problem.layout.ghosts, k)
                predicted = {(gx, gy) for (gx, gy, _dir) in predicted_states}
                if next_pos in predicted:
                    # va chạm trực tiếp với ma ở bước k
                    continue
                # Tránh va chạm đối đầu (swap): Pacman đi vào vị trí ma_k, ma đi vào vị trí Pacman_k-1
                prev_pacman_pos = current_state.pos
                predicted_prev = set()
                if k > 0:
                    predicted_prev = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(problem.layout, problem.layout.ghosts, k - 1)}
                for (gx, gy) in predicted:
                    # nếu ma ở bước k-1 tại next_pos, và ở bước k tại prev_pacman_pos -> hoán đổi đầu
                    if (next_pos in predicted_prev) and ((prev_pacman_pos[0], prev_pacman_pos[1]) == (gx, gy)):
                        continue  # bỏ successor này
                # phạt khi ở khoảng cách 1 tại bước k
                if predicted:
                    min_future_dist = min(abs(next_pos[0] - gx) + abs(next_pos[1] - gy) for (gx, gy) in predicted)
                    if min_future_dist == 1:
                        step_cost += 80
                    elif min_future_dist == 2:
                        step_cost += 30

            # NEW: nếu Pacman đang nằm trên tuyến di chuyển của ma trong 2 bước tới (chiếu theo hướng), phạt rất lớn
            danger_on_path = False
            if k <= 15:  # chỉ kiểm tra trong 15 bước đầu
                for (gx, gy, gdir) in predicted_states:
                    dx, dy = Direction._directions[gdir]
                    # Vị trí 1 bước trước (bước k-1) theo hướng ma đang đi ở bước k
                    bx, by = gx - dx, gy - dy
                    # Toán tử chiếu: kiểm tra nếu next_pos trùng bx,by hoặc trùng cùng hàng và giữa bx->gx (cho dy==0)
                    if dy == 0 and next_pos[1] == gy:
                        left = min(bx, gx)
                        right = max(bx, gx)
                        if left <= next_pos[0] <= right and abs(next_pos[0] - gx) <= 2:
                            danger_on_path = True
                            break
                if danger_on_path:
                    step_cost += 120  # ép tìm đường khác/ngưng chờ khi ma đang lao tới cách ~2 ô

            # Nếu đi vào tuyến đường của ma sớm (cell nằm trên hàng của ghost và trong hướng ghost đi),
            # tính bước an toàn s_safe để vào cell sau khi ma đảo chiều, và thêm WAIT tương đương bằng cách
            # cộng thêm chi phí chờ (s_safe - k) nếu cần
            # Giới hạn kiểm tra tuyến đường ma để tăng tốc
            if k <= 10:  # chỉ kiểm tra trong 10 bước đầu
                for ghost in problem.layout.ghosts:
                    state_k = simulate_single_ghost_state(problem.layout, ghost, k)
                    if not state_k:
                        continue
                    gx, gy, gdir = state_k
                    dxg, dyg = Direction._directions[gdir]
                    # chỉ xét cùng hàng ngang (dyg == 0). Nếu ghost đang đi TỚI cell, chờ tới lúc đảo chiều
                    if dyg == 0 and gy == next_pos[1]:
                        going_towards = (dxg > 0 and gx <= next_pos[0]) or (dxg < 0 and gx >= next_pos[0])
                        if going_towards:
                            s_safe = compute_safe_entry_step(problem.layout, ghost, next_pos, k)
                            if s_safe is not None and s_safe > k:
                                wait_steps = s_safe - k
                                step_cost += wait_steps  # chi phí chờ (không chèn STOP)
    
            # Cập nhật food_grid sau khi ăn thực phẩm
            new_food_grid = [list(row) for row in current_state.food_grid]
            if (next_pos[1] < len(new_food_grid) and 
                next_pos[0] < len(new_food_grid[0]) and 
                new_food_grid[next_pos[1]][next_pos[0]]):
                new_food_grid[next_pos[1]][next_pos[0]] = False
            new_food_grid = tuple(tuple(row) for row in new_food_grid)
                        
            # Kiểm tra nếu có ăn bánh ma thuật và cập nhật power_steps
            new_power_steps = (5 if next_pos in problem.getMagicalPies() 
                            else max(0, current_state.power_steps - 1))

            # Tạo trạng thái mới sau khi di chuyển
            next_state = State(next_pos, direction, new_food_grid, new_power_steps)
            new_cost = current_cost + step_cost  # Tính chi phí mới
            h_score = custom_heuristic(next_state, problem, corners)  # Tính heuristic cho trạng thái mới
            
            # Đưa trạng thái mới vào frontier
            heapq.heappush(frontier, (new_cost + h_score, next_state, actions + [direction], new_cost))
    
    # Nếu không tìm được đường đi tới mục tiêu
    return [], float('inf')