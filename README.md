# 🎮 Pacman Game - Trí Tuệ Nhân Tạo

## 📋 Tổng quan đề tài

**Pacman Game** là một dự án game cổ điển được phát triển bằng Python và Pygame, áp dụng các thuật toán tìm kiếm trong Trí Tuệ Nhân Tạo. Dự án bao gồm hai chế độ chơi: **Tự động (AI)** và **Thủ công (Manual)**, với các tính năng đặc biệt như xoay ma trận động và điều khiển linh hoạt.

## 🎯 Mục tiêu dự án

- **Nghiên cứu thuật toán tìm kiếm:** Áp dụng các thuật toán BFS, DFS, A* trong việc tìm đường đi tối ưu
- **Phát triển game engine:** Xây dựng hệ thống game hoàn chỉnh với đồ họa và âm thanh
- **Tối ưu hóa trải nghiệm:** Tạo ra giao diện thân thiện và điều khiển mượt mà
- **Tính năng đặc biệt:** Xoay ma trận động, teleport thủ công, và các hiệu ứng đặc biệt

## 🏗️ Cấu trúc dự án

```
PacmanGame/
├── source/
│   └── Task2_Trong/
│       ├── assets/                    # Tài nguyên đồ họa
│       │   ├── Ghost_image/          # Hình ảnh ma
│       │   └── pacman_images/         # Hình ảnh Pacman
│       ├── input/                     # File đầu vào
│       │   └── task02_pacman_example_map.txt
│       ├── output/                    # File đầu ra
│       │   ├── output.txt            # Kết quả chế độ AI
│       │   ├── output_manual.txt    # Kết quả chế độ thủ công
│       │   ├── Path.txt             # Đường đi AI
│       │   └── Path_manual.txt      # Đường đi thủ công
│       ├── src/                      # Mã nguồn chính
│       │   ├── action.py            # Định nghĩa hướng di chuyển
│       │   ├── animation.py         # Xử lý hoạt ảnh
│       │   ├── game.py              # Quản lý layout và game state
│       │   ├── ghost.py             # Logic ma
│       │   ├── manual_pacman.py     # Game thủ công
│       │   ├── movement.py          # Xử lý di chuyển
│       │   ├── pacman.py            # Game AI
│       │   ├── renderer.py          # Vẽ đồ họa
│       │   ├── search.py            # Thuật toán tìm kiếm
│       │   └── state.py              # Quản lý trạng thái
│       ├── main.py                  # Chương trình chính (AI)
│       ├── main_manual.py           # Chương trình thủ công
│       └── main_menu.py              # Menu lựa chọn
└── README.md
```

## 📁 Mô tả chi tiết các file

### 🎮 File chương trình chính

#### `main.py`
- **Chức năng:** Chạy game ở chế độ tự động (AI)
- **Thuật toán:** Sử dụng các thuật toán tìm kiếm (BFS, DFS, A*)
- **Đầu vào:** File map từ thư mục `input/`
- **Đầu ra:** Kết quả và đường đi trong thư mục `output/`

#### `main_manual.py`
- **Chức năng:** Chạy game ở chế độ điều khiển thủ công
- **Tính năng:** Điều khiển bằng phím, xoay ma trận động
- **Đặc biệt:** Teleport thủ công, ăn tường khi có power

#### `main_menu.py`
- **Chức năng:** Menu lựa chọn chế độ chơi
- **Giao diện:** Console menu thân thiện
- **Tích hợp:** Kết nối các chế độ chơi khác nhau

### 🧠 File logic game (src/)

#### `game.py` - Layout Manager
- **Chức năng:** Quản lý layout mê cung, tường, thức ăn, ma
- **Tính năng:** Xoay ma trận 90 độ, quản lý teleport
- **Thuộc tính:** `walls`, `food`, `ghosts`, `magical_pies`, `exit_gates`

#### `manual_pacman.py` - Manual Game Controller
- **Chức năng:** Điều khiển game thủ công
- **Tính năng đặc biệt:**
  - Xoay ma trận mỗi 30 bước
  - Teleport thủ công giữa các góc
  - Ăn tường khi có power (magical pie)
  - Tự động điều chỉnh kích thước cửa sổ

#### `pacman.py` - AI Game Controller
- **Chức năng:** Điều khiển game tự động
- **Thuật toán:** Tích hợp các thuật toán tìm kiếm
- **Tối ưu:** Tìm đường đi ngắn nhất và hiệu quả nhất

#### `search.py` - Search Algorithms
- **Chức năng:** Triển khai các thuật toán tìm kiếm
- **Thuật toán:** BFS, DFS, A*, Greedy Search
- **Tối ưu:** Heuristic functions cho A*

#### `renderer.py` - Graphics Engine
- **Chức năng:** Vẽ đồ họa game
- **Tính năng:**
  - Vẽ mê cung, Pacman, ma, thức ăn
  - Hiệu ứng thắng/thua
  - Tự động điều chỉnh kích thước cửa sổ
  - Scale Pacman theo kích thước mê cung

#### `state.py` - State Management
- **Chức năng:** Quản lý trạng thái game
- **Thuộc tính:** Vị trí Pacman, hướng di chuyển, thức ăn còn lại

#### `action.py` - Movement Actions
- **Chức năng:** Định nghĩa các hướng di chuyển
- **Hướng:** NORTH, SOUTH, EAST, WEST, STOP

#### `animation.py` - Animation System
- **Chức năng:** Xử lý hoạt ảnh Pacman
- **Tính năng:** Chuyển đổi frame, tạo hiệu ứng mượt mà

#### `movement.py` - Movement Controller
- **Chức năng:** Xử lý di chuyển và interpolation
- **Tính năng:** Làm mượt chuyển động, xử lý teleport

#### `ghost.py` - Ghost AI
- **Chức năng:** Logic điều khiển ma
- **AI:** Thuật toán di chuyển thông minh của ma

### 🎨 File tài nguyên

#### `assets/`
- **`Ghost_image/`:** Hình ảnh ma
- **`pacman_images/`:** Các frame hoạt ảnh Pacman

#### `input/`
- **`task02_pacman_example_map.txt`:** File map mẫu

#### `output/`
- **`output.txt`:** Kết quả chế độ AI
- **`output_manual.txt`:** Kết quả chế độ thủ công
- **`Path.txt`:** Đường đi AI
- **`Path_manual.txt`:** Đường đi thủ công

## 🚀 Cách chạy chương trình

### 📋 Yêu cầu hệ thống
- **Python:** 3.8 trở lên
- **Thư viện:** pygame, numpy
- **OS:** Windows, macOS, Linux

### 🔧 Cài đặt
```bash
# Cài đặt pygame
pip install pygame

# Cài đặt numpy (nếu cần)
pip install numpy
```

### 🎮 Cách chạy

#### 1. **Chế độ Menu (Khuyến nghị)**
```bash
cd source/Task2_Trong
python main_menu.py
```
- Chọn chế độ chơi từ menu
- Tự động chuyển đổi giữa AI và Manual

#### 2. **Chế độ AI (Tự động)**
```bash
cd source/Task2_Trong
python main.py
```
- Game tự động chạy với thuật toán AI
- Kết quả được lưu trong `output/`

#### 3. **Chế độ Thủ công**
```bash
cd source/Task2_Trong
python main_manual.py
```
- Điều khiển bằng phím mũi tên hoặc WASD
- Tính năng đặc biệt: xoay ma trận, teleport, ăn tường

### 🎯 Điều khiển (Chế độ thủ công)

#### **Di chuyển cơ bản:**
- **↑↓←→** hoặc **WASD:** Di chuyển Pacman
- **SPACE:** Dừng di chuyển
- **ESC:** Thoát game

#### **Tính năng đặc biệt:**
- **+/-:** Tăng/giảm tốc độ di chuyển
- **Shift + T:** Teleport chéo góc
- **T + 1/2/3/4:** Teleport đến góc cụ thể
- **Magical Pie (o):** Ăn để có khả năng ăn tường

#### **Tính năng động:**
- **Xoay ma trận:** Tự động xoay 90° mỗi 30 bước
- **Tự động resize:** Cửa sổ tự động điều chỉnh kích thước
- **Scale Pacman:** Kích thước Pacman tự động điều chỉnh

## 🎯 Mục tiêu game

### **Mục tiêu chính:**
1. **Ăn hết thức ăn** (dấu chấm trắng)
2. **Đến cửa thoát** (ô xanh lá)
3. **Tránh ma** (trừ khi có power)

### **Điểm số:**
- **Thức ăn thường:** 1 điểm
- **Magical Pie:** 5 điểm + khả năng ăn tường
- **Ăn tường:** 5 điểm (khi có power)

## 🔧 Tính năng kỹ thuật

### **Thuật toán AI:**
- **BFS (Breadth-First Search):** Tìm đường ngắn nhất
- **DFS (Depth-First Search):** Tìm kiếm sâu
- **A* (A-Star):** Tìm kiếm tối ưu với heuristic
- **Greedy Search:** Tìm kiếm tham lam

### **Tính năng đặc biệt:**
- **Xoay ma trận động:** Mỗi 30 bước
- **Teleport thủ công:** Giữa các góc mê cung
- **Ăn tường:** Khi có power từ magical pie
- **Tự động resize:** Cửa sổ thích ứng với kích thước mê cung

### **Tối ưu hóa:**
- **OOP Design:** Code được tổ chức theo hướng đối tượng
- **Clean Code:** Loại bỏ code thừa, tối ưu performance
- **Memory Management:** Quản lý bộ nhớ hiệu quả
- **Error Handling:** Xử lý lỗi robust

## 📊 Kết quả và đánh giá

### **Chế độ AI:**
- Tìm đường đi tối ưu
- Kết quả được lưu trong file
- Phân tích hiệu suất thuật toán

### **Chế độ thủ công:**
- Trải nghiệm game mượt mà
- Tính năng đặc biệt độc đáo
- Giao diện thân thiện

## 🤝 Đóng góp

Dự án này được phát triển cho mục đích học tập và nghiên cứu về Trí Tuệ Nhân Tạo. Mọi đóng góp và phản hồi đều được chào đón!

## 📝 License

Dự án được phát triển cho mục đích giáo dục và nghiên cứu.

---

**🎮 Chúc bạn chơi game vui vẻ! 🎮**