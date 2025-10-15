import pygame
import os
from action import Direction

class PacmanAnimation:
    FRAME_SIZE = (25, 25)  # Kích thước của mỗi khung hình (frame) animation.
    FRAME_REPEAT = 1  # Số lần lặp lại mỗi khung hình trong animation.
    ANIMATION_SPEED = 0.05  # Thời gian giữa các lần cập nhật khung hình (s).

    def __init__(self):
        # Khởi tạo các thuộc tính của đối tượng PacmanAnimation.
        self.images = self._load_images()  
        self.animation_frames = self._create_animation_frames()  # Tạo danh sách các khung hình animation.
        self.current_frame = 0  
        self.last_update = 0  # Thời gian của lần cập nhật khung hình trước.

    def _load_images(self):
        # Tải tất cả hình ảnh Pacman từ thư mục pacman_images.
        base_dir = os.path.dirname(os.path.abspath(__file__))
        images_dir = os.path.normpath(os.path.join(base_dir, "..", "assets", "pacman_images"))
        return [
            pygame.transform.scale(
                pygame.image.load(os.path.join(images_dir, f"{i}.png")), 
                self.FRAME_SIZE  
            ) 
            for i in range(1, 5)  # Lặp qua các tệp hình ảnh từ "1.png" đến "4.png".
        ]

    def _create_animation_frames(self):
        # Tạo danh sách các khung hình animation. Mỗi hình ảnh được lặp lại FRAME_REPEAT lần.
        return [img for img in self.images for _ in range(self.FRAME_REPEAT)]

    def get_current_frame(self, current_time, direction):
        # Trả về khung hình hiện tại sau khi kiểm tra thời gian cập nhật và hướng di chuyển của Pacman.
        if current_time - self.last_update >= self.ANIMATION_SPEED:
            self.current_frame = (self.current_frame + 1) % len(self.animation_frames)
            self.last_update = current_time  

        # Xoay khung hình hiện tại theo hướng di chuyển của Pacman.
        return self._rotate_image(self.animation_frames[self.current_frame], direction)

    def _rotate_image(self, image, direction):
        # Xoay hình ảnh theo hướng di chuyển (hướng của Pacman).
        angles = {
            Direction.EAST: 0,  
            Direction.NORTH: 90,  
            Direction.WEST: 180,  
            Direction.SOUTH: 270,  
            Direction.STOP: 0  
        }
        return pygame.transform.rotate(image, angles.get(direction, 0))  
