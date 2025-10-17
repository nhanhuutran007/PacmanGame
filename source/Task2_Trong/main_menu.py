import sys
import os

# Thêm thư mục src vào Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, SRC_DIR)

# Import sẽ được thực hiện trong các hàm con để tránh lỗi


def show_menu():
    """Hiển thị menu lựa chọn"""
    print("=" * 50)
    print("           PACMAN GAME")
    print("=" * 50)
    print("Chon che do choi:")
    print("1. Che do tu dong (AI)")
    print("2. Che do dieu khien thu cong")
    print("3. Thoat")
    print("=" * 50)


def run_auto_mode(input_filename="task02_pacman_example_map.txt"):
    """Chạy game ở chế độ tự động"""
    print("\nDang khoi dong che do tu dong...")
    
    # Import và chạy main.py
    import subprocess
    import sys
    
    try:
        # Chạy main.py với subprocess
        result = subprocess.run([sys.executable, "main.py"], 
                              cwd=os.path.dirname(__file__), 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Game tu dong hoan thanh!")
        else:
            print(f"Loi khi chay game tu dong: {result.stderr}")
            
    except Exception as e:
        print(f"Loi: {e}")


def run_manual_mode(input_filename="task02_pacman_example_map.txt"):
    """Chạy game ở chế độ điều khiển thủ công"""
    print("\nDang khoi dong che do dieu khien thu cong...")
    
    # Import và chạy main_manual.py
    import subprocess
    import sys
    
    try:
        # Chạy main_manual.py với subprocess
        result = subprocess.run([sys.executable, "main_manual.py"], 
                              cwd=os.path.dirname(__file__), 
                              capture_output=True, text=True)
        
        if result.returncode == 0:
            print("Game thu cong hoan thanh!")
        else:
            print(f"Loi khi chay game thu cong: {result.stderr}")
            
    except Exception as e:
        print(f"Loi: {e}")


def main():
    """Hàm main chính"""
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
