import sys
import os
import re

# Thêm thư mục src vào Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, SRC_DIR)

# Import các module cần thiết
from game import Layout
from agent import AgentGame
from pacman import PacmanGame


def show_menu():
    # Hiển thị menu lựa chọn
    print("=" * 50)
    print("           PACMAN GAME")
    print("=" * 50)
    print("Chon che do choi:")
    print("1. Che do tu dong (AI)")
    print("2. Che do dieu khien thu cong")
    print("3. Thoat")
    print("=" * 50)


def run_auto_mode(input_filename="task02_pacman_example_map.txt", output_filename="output.txt", path_filename="Path.txt"):
    # Chạy game ở chế độ tự động
    print("\nDang khoi dong che do tu dong...")
    
    try:
        # Xác định đường dẫn file vào/ra
        input_file = os.path.join(os.path.dirname(__file__), 'input', input_filename)
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, output_filename)
        path_file = os.path.join(output_dir, path_filename)

        # Tải layout và chạy game
        layout = Layout.getLayout(input_file)
        if layout is None:
            print("Khong the tai layout!")
            return

        game = AgentGame(layout)
        game.run()

        # 1) Path.txt từ game.run_log (chuỗi Step... at (x, y))
        path_coords = []
        if hasattr(game, 'run_log') and game.run_log:
            for line in game.run_log:
                m = re.search(r"\((\d+)\,\s*(\d+)\)", line)
                if m:
                    x, y = int(m.group(1)), int(m.group(2))
                    path_coords.append((x, y))
        # Fallback: nếu trống, ghi vị trí hiện tại
        if not path_coords and hasattr(game, 'final_position'):
            path_coords = [game.final_position]

        with open(path_file, 'w', encoding='utf-8') as f:
            f.write("[\n")
            for p in path_coords:
                f.write(f"  {p},\n")
            f.write("]\n")

        # 2) output.txt: Total cost + Actions từ game
        total_cost = getattr(game, 'total_cost', 0)
        actions_list = list(getattr(game, 'actions_log', []))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Total cost: {total_cost}\n")
            f.write("Actions:\n[\n")
            for a in actions_list:
                a_clean = str(a).strip("'\" ")
                f.write(f"  '{a_clean}',\n")
            f.write("]\n")
        
        print("Game tu dong hoan thanh!")
        
    except Exception as e:
        print(f"Loi khi chay game tu dong: {e}")


def run_manual_mode(input_filename="task02_pacman_example_map.txt", output_filename="output_manual.txt", path_filename="Path_manual.txt"):
    # Chạy game ở chế độ điều khiển thủ công
    print("\nDang khoi dong che do dieu khien thu cong...")
    
    try:
        # Xác định đường dẫn file vào/ra
        input_file = os.path.join(os.path.dirname(__file__), 'input', input_filename)
        output_dir = os.path.join(os.path.dirname(__file__), 'output')
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        output_file = os.path.join(output_dir, output_filename)
        path_file = os.path.join(output_dir, path_filename)

        # Tải layout và chạy game
        layout = Layout.getLayout(input_file)
        if layout is None:
            print("Khong the tai layout!")
            return

        game = PacmanGame(layout)
        game.run()

        # 1) Path.txt từ game.run_log (chuỗi Step... at (x, y))
        path_coords = []
        if hasattr(game, 'run_log') and game.run_log:
            for line in game.run_log:
                m = re.search(r"\((\d+)\,\s*(\d+)\)", line)
                if m:
                    x, y = int(m.group(1)), int(m.group(2))
                    path_coords.append((x, y))
        # Fallback: nếu trống, ghi vị trí hiện tại
        if not path_coords and hasattr(game, 'final_position'):
            path_coords = [game.final_position]

        with open(path_file, 'w', encoding='utf-8') as f:
            f.write("[\n")
            for p in path_coords:
                f.write(f"  {p},\n")
            f.write("]\n")

        # 2) output.txt: Total cost + Actions từ game
        total_cost = getattr(game, 'total_cost', 0)
        actions_list = list(getattr(game, 'actions_log', []))

        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(f"Total cost: {total_cost}\n")
            f.write("Actions:\n[\n")
            for a in actions_list:
                a_clean = str(a).strip("'\" ")
                f.write(f"  '{a_clean}',\n")
            f.write("]\n")
        
        print("Game thu cong hoan thanh!")
        
    except Exception as e:
        print(f"Loi khi chay game thu cong: {e}")


def main():
    # Hàm main chính
    while True:
        show_menu()
        
        try:
            choice = input("Nhap lua chon cua ban (1-3): ").strip()
            
            if choice == "1":
                run_auto_mode()
                input("\nNhan Enter de tiep tuc...")
                
            elif choice == "2":
                run_manual_mode()
                input("\nNhan Enter de tiep tuc...")
                
            elif choice == "3":
                print("\nCam on ban da choi! Tam biet!")
                break
                
            else:
                print("\nLua chon khong hop le! Vui long chon 1, 2 hoac 3.")
                input("Nhan Enter de tiep tuc...")
                
        except KeyboardInterrupt:
            print("\n\nCam on ban da choi! Tam biet!")
            break
        except EOFError:
            print("\n\nCam on ban da choi! Tam biet!")
            break
        except Exception as e:
            print(f"\nLoi khong mong muon: {e}")
            try:
                input("Nhan Enter de tiep tuc...")
            except EOFError:
                break


if __name__ == '__main__':
    main()
