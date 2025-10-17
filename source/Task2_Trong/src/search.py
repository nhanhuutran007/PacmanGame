import heapq
from collections import deque
from visualize import Direction
from game import Layout


def simulate_ghost_states(layout: Layout, ghosts, step: int):
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
            states.append((x, y, direction))
        except Exception:
            continue
    return states


def simulate_single_ghost_state(layout: Layout, ghost, step: int):
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


class AStarDynamicSearch:
    """
    Tìm kiếm A* động theo từng bước, né ma và tránh lặp.
    """

    def __init__(self, problem, corners):
        self.problem = problem
        self.corners = corners
        self.recent_positions = deque(maxlen=10)
        self.last_selected_action = None

    def find_next_action(self, current_state, ghosts):
        if not self.recent_positions or self.recent_positions[-1] != current_state.pos:
            self.recent_positions.append(current_state.pos)

        # Ưu tiên ăn thức ăn kề nếu an toàn
        food_grid_now = self.problem.getFoodGrid()
        cx, cy = current_state.pos
        
        # Kiểm tra magical pie trước (ưu tiên cao hơn)
        for direction, (dx, dy) in Direction._directions.items():
            if direction == Direction.STOP:
                continue
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < len(food_grid_now[0]) and 0 <= ny < len(food_grid_now)):
                try:
                    # Kiểm tra magical pie
                    if self.problem.isMagicalPie((nx, ny)):
                        if not self.isStepDangerous((cx, cy), (nx, ny), ghosts, step=1):
                            self.last_selected_action = direction
                            return direction
                except Exception:
                    pass
        
        # Kiểm tra thức ăn thường
        for direction, (dx, dy) in Direction._directions.items():
            if direction == Direction.STOP:
                continue
            nx, ny = cx + dx, cy + dy
            if (0 <= nx < len(food_grid_now[0]) and 0 <= ny < len(food_grid_now)):
                try:
                    if food_grid_now[ny][nx]:
                        if not self.isStepDangerous((cx, cy), (nx, ny), ghosts, step=1):
                            self.last_selected_action = direction
                            return direction
                except Exception:
                    pass

        path = self.aStarToGoal(current_state, ghosts)
        if not path:
            return Direction.STOP

        start_pos = current_state.pos
        first_dir = path[0]
        dx, dy = Direction._directions[first_dir]
        first_pos = (start_pos[0] + dx, start_pos[1] + dy)
        if self.isStepDangerous(start_pos, first_pos, ghosts, step=1):
            alt_dir = self.chooseSaferAlternative(start_pos, ghosts)
            self.last_selected_action = alt_dir if alt_dir is not None else first_dir
            return self.last_selected_action

        self.last_selected_action = first_dir
        return first_dir

    def aStarToGoal(self, current_state, ghosts):
        start = current_state.pos
        food_grid = self.problem.getFoodGrid()

        food_targets = [(x, y)
                        for y in range(len(food_grid))
                        for x in range(len(food_grid[y])) if food_grid[y][x]]
        if food_targets:
            def h(pos):
                px, py = pos
                local_count = 0
                radius = 3  # Tăng radius để tính toán chính xác hơn
                
                # Đếm thức ăn trong vùng lân cận
                for yy in range(max(0, py - radius), min(len(food_grid), py + radius + 1)):
                    row = food_grid[yy]
                    for xx in range(max(0, px - radius), min(len(row), px + radius + 1)):
                        if row[xx]:
                            local_count += 1
                
                # Tính khoảng cách đến thức ăn gần nhất
                min_distance = float('inf')
                for fx, fy in food_targets:
                    distance = abs(px - fx) + abs(py - fy)
                    min_distance = min(min_distance, distance)
                
                # Heuristic kết hợp: ưu tiên vùng có nhiều thức ăn và gần thức ăn
                base = len(food_targets)
                density_bonus = 0.5 * local_count  # Thưởng cho vùng có nhiều thức ăn
                distance_penalty = 0.3 * min_distance  # Phạt cho khoảng cách xa
                
                score = base - distance_penalty + density_bonus
                return max(0, score)

            def is_goal(pos):
                return food_grid[pos[1]][pos[0]]
        else:
            exits = getattr(self.problem.layout, 'exit_gates', [])
            if not exits:
                return []

            def h(pos):
                px, py = pos
                return min(max(abs(px - ex), abs(py - ey)) for (ex, ey) in exits)

            def is_goal(pos):
                return pos in exits

        frontier = []
        heapq.heappush(frontier, (h(start), 0, start, []))
        visited = set()

        while frontier:
            f, g, pos, path = heapq.heappop(frontier)
            if pos in visited:
                continue
            visited.add(pos)

            if is_goal(pos):
                return path

            k = g + 1
            predicted_k_states = simulate_ghost_states(self.problem.layout, ghosts, k)
            predicted_k_positions = {(gx, gy) for (gx, gy, _d) in predicted_k_states}
            predicted_km1_positions = set()
            if k > 0:
                predicted_km1_positions = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, k - 1)}

            for next_pos, direction, step_cost in self.problem.getSuccessors(pos):
                if direction == Direction.STOP:
                    if step_cost != 0:
                        continue
                if self.problem.isWall(next_pos):
                    continue
                if next_pos in visited:
                    continue

                ate_food_bonus = 0
                try:
                    if food_grid[next_pos[1]][next_pos[0]]:
                        ate_food_bonus = 1
                except Exception:
                    pass

                new_g = g + 1

                if next_pos in predicted_k_positions:
                    continue
                if (next_pos in predicted_km1_positions) and (pos in predicted_k_positions):
                    continue

                step_risk = 0
                if predicted_k_positions:
                    min_future_dist = min(abs(next_pos[0] - gx) + abs(next_pos[1] - gy) for (gx, gy) in predicted_k_positions)
                    if min_future_dist == 1:
                        step_risk += 80
                    elif min_future_dist == 2:
                        step_risk += 30

                danger_on_path = False
                for (gx, gy, gdir) in predicted_k_states:
                    dxg, dyg = Direction._directions[gdir]
                    if dyg == 0 and gy == next_pos[1]:
                        going_towards = (dxg > 0 and gx <= next_pos[0]) or (dxg < 0 and gx >= next_pos[0])
                        if going_towards and abs(gx - next_pos[0]) <= 2:
                            danger_on_path = True
                            break
                if danger_on_path:
                    step_risk += 60

                last_dir = path[-1] if path else current_state.direction
                if self.isReverseDirection(last_dir, direction):
                    step_risk += 2

                prev_pos = self.recent_positions[-1] if self.recent_positions else None
                if prev_pos is not None and next_pos == prev_pos:
                    step_risk += 6
                if next_pos in self.recent_positions:
                    step_risk += 2

                new_f = new_g + h(next_pos) + step_risk
                if ate_food_bonus:
                    new_f -= 3.0
                heapq.heappush(frontier, (new_f, new_g, next_pos, path + [direction]))

        for next_pos, direction, step_cost in self.problem.getSuccessors(start):
            if direction != Direction.STOP and not self.problem.isWall(next_pos):
                return [direction]
        return []

    def isStepDangerous(self, from_pos, to_pos, ghosts, step: int) -> bool:
        try:
            predicted = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, step)}
            if to_pos in predicted:
                return True
            if step > 0:
                predicted_prev = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, step - 1)}
                if (to_pos in predicted_prev) and (from_pos in predicted):
                    return True
            if predicted:
                min_dist = min(abs(to_pos[0] - gx) + abs(to_pos[1] - gy) for (gx, gy) in predicted)
                if min_dist <= 1:
                    return True
        except Exception:
            return False
        return False

    def chooseSaferAlternative(self, start_pos, ghosts):
        best_dir = None
        best_risk = float('inf')
        for next_pos, direction, step_cost in self.problem.getSuccessors(start_pos):
            if direction == Direction.STOP:
                if step_cost != 0:
                    continue
            if self.problem.isWall(next_pos):
                continue
            risk = 0
            try:
                predicted = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, 1)}
                if next_pos in predicted:
                    risk += 1000
                else:
                    if predicted:
                        min_dist = min(abs(next_pos[0] - gx) + abs(next_pos[1] - gy) for (gx, gy) in predicted)
                        if min_dist == 1:
                            risk += 200
                        elif min_dist == 2:
                            risk += 80
            except Exception:
                pass
            if risk < best_risk:
                best_risk = risk
                best_dir = direction
        return best_dir

    def isReverseDirection(self, prev_dir, new_dir):
        if prev_dir == Direction.NORTH and new_dir == Direction.SOUTH:
            return True
        if prev_dir == Direction.SOUTH and new_dir == Direction.NORTH:
            return True
        if prev_dir == Direction.EAST and new_dir == Direction.WEST:
            return True
        if prev_dir == Direction.WEST and new_dir == Direction.EAST:
            return True
        return False