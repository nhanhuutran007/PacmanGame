
import sys
import os

# Thêm thư mục src vào Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, SRC_DIR)

def check_dependencies():
  
    missing_deps = []
    
    try:
        import pygame
    except ImportError:
        missing_deps.append("pygame")
    
    if missing_deps:
        error_msg = f"Thiếu các thư viện cần thiết: {', '.join(missing_deps)}\n\n"
        error_msg += "Vui lòng cài đặt bằng lệnh:\n"
        if "pygame" in missing_deps:
            error_msg += "pip install pygame\n"
        
        # Hiển thị lỗi trong console
        print("=" * 60)
        print("LOI: Thieu thu vien can thiet!")
        print("=" * 60)
        print(error_msg)
        print("=" * 60)
        return False
    
    return True

def main():
  
    print("Dang khoi dong Pacman Game...")
    print("Su dung giao dien GUI hien dai!")
    
    # Kiểm tra dependencies
    if not check_dependencies():
        input("Nhấn Enter để thoát...")
        return
    
    try:
        # Import và chạy Integrated Game Manager
        from src.game import main as run_integrated_game
        
        print("Da tai thanh cong integrated game manager!")
        print("Dang mo giao dien game...")
        
        # Chạy integrated game
        run_integrated_game()
        
    except ImportError as e:
        error_msg = f"Không thể tải game launcher: {str(e)}\n\n"
        error_msg += "Vui lòng kiểm tra:\n"
        error_msg += "1. File src/game_launcher.py có tồn tại\n"
        error_msg += "2. Tất cả dependencies đã được cài đặt\n"
        error_msg += "3. Cấu trúc thư mục đúng"
        
        print("=" * 60)
        print("LỖI: Không thể tải game launcher!")
        print("=" * 60)
        print(error_msg)
        print("=" * 60)
        input("Nhấn Enter để thoát...")
        
    except Exception as e:
        error_msg = f"Lỗi không mong muốn: {str(e)}"
        
        print("=" * 60)
        print("LỖI: Có lỗi xảy ra!")
        print("=" * 60)
        print(error_msg)
        print("=" * 60)
        input("Nhấn Enter để thoát...")

if __name__ == '__main__':
    # Chỉ chạy GUI mode
    main()
