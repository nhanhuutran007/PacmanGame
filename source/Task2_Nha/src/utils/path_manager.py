import os

def get_project_root():
    """Lấy đường dẫn tuyệt đối đến thư mục gốc của dự án (/pacman_project)."""
    return os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_input_file(filename):
    """Lấy đường dẫn tuyệt đối đến file trong thư mục /input."""
    return os.path.join(get_project_root(), "input", filename)

def get_output_file(filename):
    """Lấy đường dẫn tuyệt đối đến file trong thư mục /output, tạo thư mục nếu chưa tồn tại."""
    output_dir = os.path.join(get_project_root(), "output")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    return os.path.join(output_dir, filename)