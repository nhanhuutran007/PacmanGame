class Heuristic:
    def manhattan(state, remaining_food):
        """
        Tính khoảng cách Manhattan từ vị trí hiện tại đến thức ăn gần nhất.
        Admissible và consistent.
        """
        x, y = state[0], state[1]  # Lấy tọa độ từ state
        if not remaining_food:
            return 0
        return min(abs(x - fx) + abs(y - fy) for fx, fy in remaining_food)