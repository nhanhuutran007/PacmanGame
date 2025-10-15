import heapq
from collections import deque
from action import Direction
from search import simulate_ghost_states, simulate_single_ghost_state

class AStarDynamicSearch:
    """
    Tìm kiếm A* động theo từng bước với heuristic không dựa trên Manhattan,
    kết hợp đánh giá rủi ro từ ma và bộ nhớ vị trí để tránh lặp.
    """
    def __init__(self, problem, corners):
        self.problem = problem
        self.corners = corners
        # Bộ nhớ vị trí gần đây để tránh lặp qua lại
        self.recent_positions = deque(maxlen=10)
        self.last_selected_action = None

    def find_next_action(self, current_state, ghosts):
        """
        Tính đường đi (A*) từ vị trí hiện tại đến mục tiêu gần nhất
        rồi trả về hành động đầu tiên trong đường đi đó.
        """
        # Cập nhật bộ nhớ vị trí gần đây
        if not self.recent_positions or self.recent_positions[-1] != current_state.pos:
            self.recent_positions.append(current_state.pos)

        path = self.aStarToGoal(current_state, ghosts)
        if not path:
            return Direction.STOP

        # Phân tích rủi ro cho bước đầu tiên; nếu rủi ro cao, chọn hướng vòng an toàn hơn
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

    # --------------------------
    #  A* core
    # --------------------------
    def aStarToGoal(self, current_state, ghosts):
        start = current_state.pos
        # Luôn dùng lưới thức ăn mới nhất từ game (tránh lệch trạng thái)
        food_grid = self.problem.getFoodGrid()

        # Tập mục tiêu: tất cả food còn lại; nếu không còn thì exit
        food_targets = [(x, y)
                        for y in range(len(food_grid))
                        for x in range(len(food_grid[y])) if food_grid[y][x]]
        if food_targets:
            def h(pos):
                # Heuristic dựa trên mật độ thức ăn lân cận
                px, py = pos
                local_count = 0
                radius = 2  # cửa sổ 5x5
                for yy in range(max(0, py - radius), min(len(food_grid), py + radius + 1)):
                    row = food_grid[yy]
                    for xx in range(max(0, px - radius), min(len(row), px + radius + 1)):
                        if row[xx]:
                            local_count += 1
                base = len(food_targets)
                score = base - 0.3 * local_count
                return max(0, score)
            def is_goal(pos):
                return food_grid[pos[1]][pos[0]]
        else:
            exits = getattr(self.problem.layout, 'exit_gates', [])
            if not exits:
                return []
            def h(pos):
                # Heuristic dùng Chebyshev tới cổng exit gần nhất
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

            for next_pos, direction, step_cost in self.problem.getSuccessors(pos):
                if direction == Direction.STOP:
                    # Bỏ đứng yên trừ khi đó là teleport (step_cost == 0)
                    if step_cost != 0:
                        continue
                if self.problem.isWall(next_pos):
                    continue
                if next_pos in visited:
                    continue

                # Nếu có food tại next_pos, giả lập ăn để heuristic "len(food_targets)" giảm dần
                ate_food_bonus = 0
                try:
                    if food_grid[next_pos[1]][next_pos[0]]:
                        ate_food_bonus = 1
                except Exception:
                    pass

                new_g = g + 1

                # Né ma: loại bỏ successor nếu va chạm trực tiếp/đối đầu tại bước k=new_g
                k = new_g
                predicted_k = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, k)}
                if next_pos in predicted_k:
                    # va chạm trực tiếp tại bước k
                    continue
                # Né hoán đổi đầu (Pacman<->Ghost) giữa bước k-1 và k
                if k > 0:
                    predicted_km1 = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, k - 1)}
                    if (next_pos in predicted_km1) and (pos in predicted_k):
                        # Ghost vào pos, Pacman vào next_pos
                        continue

                # Phạt rủi ro nếu tiến quá sát đường đi của ma
                step_risk = 0
                if predicted_k:
                    min_future_dist = min(abs(next_pos[0] - gx) + abs(next_pos[1] - gy) for (gx, gy) in predicted_k)
                    if min_future_dist == 1:
                        step_risk += 80
                    elif min_future_dist == 2:
                        step_risk += 30

                # Phạt mạnh nếu đang đi vào làn ma đang lao tới trong cùng hàng ngang trong 2 ô
                danger_on_path = False
                for (gx, gy, gdir) in simulate_ghost_states(self.problem.layout, ghosts, k):
                    dxg, dyg = Direction._directions[gdir]
                    if dyg == 0 and gy == next_pos[1]:
                        # nếu ghost ở cùng hàng và hướng về phía next_pos trong phạm vi 2 ô
                        going_towards = (dxg > 0 and gx <= next_pos[0]) or (dxg < 0 and gx >= next_pos[0])
                        if going_towards and abs(gx - next_pos[0]) <= 2:
                            danger_on_path = True
                            break
                if danger_on_path:
                    step_risk += 60

                # Giảm lắc lư: phạt nhẹ khi đảo hướng so với bước trước
                last_dir = path[-1] if path else current_state.direction
                if self.isReverseDirection(last_dir, direction):
                    step_risk += 2

                # Tránh quay lại ô vừa đi: phạt mạnh nếu next_pos == vị trí trước đó
                prev_pos = self.recent_positions[-1] if self.recent_positions else None
                if prev_pos is not None and next_pos == prev_pos:
                    step_risk += 6
                # Tránh lặp lại các ô rất gần đây
                if next_pos in self.recent_positions:
                    step_risk += 2

                new_f = new_g + h(next_pos) + step_risk
                # Khuyến khích di chuyển khi ăn được food ở bước tới
                if ate_food_bonus:
                    new_f -= 0.5
                heapq.heappush(frontier, (new_f, new_g, next_pos, path + [direction]))

        # Fallback: không tìm thấy đường (rất hiếm). Chọn bước hợp lệ đầu tiên.
        for next_pos, direction, step_cost in self.problem.getSuccessors(start):
            if direction != Direction.STOP and not self.problem.isWall(next_pos):
                return [direction]
        return []

    # Heuristic tích hợp trực tiếp trong aStarToGoal

    # --------------------------
    #  Helpers: đánh giá rủi ro và chọn đường vòng an toàn
    # --------------------------
    def isStepDangerous(self, from_pos, to_pos, ghosts, step: int) -> bool:
        try:
            # va chạm trực tiếp ở bước 'step'
            predicted = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, step)}
            if to_pos in predicted:
                return True
            # hoán đổi đầu: ghost vào from_pos còn Pacman vào to_pos
            if step > 0:
                predicted_prev = {(gx, gy) for (gx, gy, _d) in simulate_ghost_states(self.problem.layout, ghosts, step - 1)}
                if (to_pos in predicted_prev) and (from_pos in predicted):
                    return True
            # cận kề nguy hiểm
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
            # đánh giá rủi ro tại bước 1
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

