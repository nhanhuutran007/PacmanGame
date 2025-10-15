import heapq
import time
import random
from collections import deque
from state import State
from action import Direction
from game import Layout

class AStarDynamicSearch:
    """
    A* động: mỗi bước chạy A* với heuristic Manhattan đơn giản
    để tìm đường ngắn nhất tới thức ăn gần nhất (hết thức ăn thì tới exit).
    """
    def __init__(self, problem, corners):
        self.problem = problem
        self.corners = corners

    def find_next_action(self, current_state, ghosts):
        """
        Tính đường đi ngắn nhất (BFS) từ vị trí hiện tại đến mục tiêu gần nhất
        rồi trả về hành động đầu tiên trong đường đi đó.
        """
        path = self._a_star_to_goal(current_state)
        return path[0] if path else Direction.STOP

    # --------------------------
    #  A* core
    # --------------------------
    def _a_star_to_goal(self, current_state):
        start = current_state.pos
        # Luôn dùng lưới thức ăn mới nhất từ game (tránh lệch trạng thái)
        food_grid = self.problem.getFoodGrid()

        # Tập mục tiêu: tất cả food còn lại; nếu không còn thì exit
        food_targets = [(x, y)
                        for y in range(len(food_grid))
                        for x in range(len(food_grid[y])) if food_grid[y][x]]
        if food_targets:
            def h(pos):
                # Heuristic không dùng Manhattan: dùng số lượng thức ăn còn lại (hằng số theo pos)
                return len(food_targets)
            def is_goal(pos):
                return food_grid[pos[1]][pos[0]]
        else:
            exits = getattr(self.problem.layout, 'exit_gates', [])
            if not exits:
                return []
            def h(pos):
                # Không dùng Manhattan: heuristic 0 (Dijkstra) khi tìm đến exit
                return 0
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
                new_f = new_g + h(next_pos)
                # Khuyến khích di chuyển khi ăn được food ở bước tới
                if ate_food_bonus:
                    new_f -= 0.5
                heapq.heappush(frontier, (new_f, new_g, next_pos, path + [direction]))

        # Fallback: không tìm thấy đường (rất hiếm). Chọn bước hợp lệ đầu tiên.
        for next_pos, direction, step_cost in self.problem.getSuccessors(start):
            if direction != Direction.STOP and not self.problem.isWall(next_pos):
                return [direction]
        return []

    # Heuristic đã tích hợp trực tiếp trong _a_star_to_goal

    # Loại bỏ toàn bộ cơ chế chống kẹt/escape/fallback để tập trung ngắn nhất

