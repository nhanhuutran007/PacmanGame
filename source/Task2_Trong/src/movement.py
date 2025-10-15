class Movement:
    def __init__(self):
        # Khởi tạo các thuộc tính của đối tượng Movement.
        self.move_progress = 0  # Tiến độ di chuyển, giá trị từ 0 đến 1.
        self.last_pos = None  # Vị trí trước đó của đối tượng.
        self.current_pos = None  # Vị trí hiện tại của đối tượng.
        self.teleport_target = None  # Mục tiêu chuyển động (nếu có) nếu đối tượng di chuyển qua cổng dịch chuyển.

    def update_position(self, new_pos, opposite_corners=None):
        if self.current_pos != new_pos:
            # Lưu lại vị trí cũ (nếu có) và cập nhật vị trí mới.
            self.last_pos = self.current_pos if self.current_pos else new_pos
            self.current_pos = new_pos
            self.move_progress = 0  # Reset tiến độ di chuyển về 0.
            self.teleport_target = (opposite_corners[new_pos] if new_pos in opposite_corners else None)

    def get_interpolated_position(self):
        if not self.last_pos or not self.current_pos:
            return self.current_pos

        if self.teleport_target:
            return self.teleport_target
        
        # Tính toán tiến độ di chuyển và nội suy vị trí giữa last_pos và current_pos.
        self.move_progress = min(1.0, self.move_progress + 0.1)  # Tăng tiến độ di chuyển (max 1.0).
        
        # Nội suy vị trí theo công thức.
        x = self.last_pos[0] * (1 - self.move_progress) + self.current_pos[0] * self.move_progress
        y = self.last_pos[1] * (1 - self.move_progress) + self.current_pos[1] * self.move_progress
        return (x, y)
