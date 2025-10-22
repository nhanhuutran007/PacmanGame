Trí Tuệ Nhân Tạo

## 📋 Tổng quan đề tài

Dự án **Pacman Game** bao gồm hai phần chính nghiên cứu về các thuật toán tìm kiếm trong Trí Tuệ Nhân Tạo:

### 🧩 **Task 1: 8-Puzzle Problem**
- **Mục tiêu:** Giải bài toán 8-puzzle sử dụng các thuật toán tìm kiếm
- **Thuật toán:** BFS, A* với Manhattan Distance và Misplaced Tiles heuristics
- **Tính năng:** So sánh hiệu quả giữa các thuật toán, visualization cây tìm kiếm

### 🎮 **Task 2: Pacman Game**
- **Mục tiêu:** Game Pacman với hai chế độ chơi: **Tự động (AI)** và **Thủ công (Manual)**
- **Thuật toán:** A* search cho AI, điều khiển thủ công với tính năng đặc biệt
- **Tính năng:** Xoay ma trận động, teleport, ăn tường, đồ họa với Pygame

## 🎯 Mục tiêu dự án

- **Nghiên cứu thuật toán tìm kiếm:** Áp dụng BFS, A* trong các bài toán thực tế
- **So sánh hiệu quả:** Đánh giá hiệu suất giữa các thuật toán và heuristic khác nhau
- **Phát triển game engine:** Xây dựng hệ thống game hoàn chỉnh với đồ họa
- **Tối ưu hóa trải nghiệm:** Giao diện thân thiện và điều khiển mượt mà

## 🏗️ Cấu trúc dự án

```
midterm_06_52300235/
├── source/
│   ├── Task1/                        # 8-Puzzle Problem
│   │   └── Task1.ipynb              # Jupyter notebook với thuật toán BFS, A*
│   └── Task2/                        # Pacman Game
│       ├── assets/                   # Tài nguyên đồ họa
│       │   ├── Ghost_image/         # Hình ảnh ma
│       │   │   └── unnamed.png
│       │   └── pacman_images/        # Hình ảnh Pacman
│       │       ├── 1.png, 2.png, 3.png, 4.png
│       ├── input/                    # File đầu vào
│       │   └── task02_pacman_example_map.txt
│       ├── output/                   # File đầu ra
│       │   ├── output.txt           # Kết quả chế độ AI
│       │   ├── output_manual.txt   # Kết quả chế độ thủ công
│       │   ├── Path.txt            # Đường đi AI
│       │   └── Path_manual.txt     # Đường đi thủ công
│       ├── src/                     # Mã nguồn chính
│       │   ├── agent.py            # AI Agent - Trí tuệ nhân tạo
│       │   ├── base_pacman.py      # Base class + Ghost class
│       │   ├── game.py             # Layout Manager - Tạo mê cung
│       │   ├── pacman.py           # Manual Pacman - Điều khiển thủ công
│       │   ├── search.py           # Thuật toán tìm kiếm A*
│       │   ├── state.py            # Quản lý trạng thái game
│       │   └── visualize.py        # Visualization Engine - Đồ họa
│       ├── main.py                 # Entry point chính
│       └── README.md               # Hướng dẫn sử dụng
└── README.md                        # README tổng quan
```

## 📁 Mô tả chi tiết các file

### 🧩 **Task 1: 8-Puzzle Problem**

#### `Task1.ipynb` - Jupyter Notebook
- **Chức năng:** Nghiên cứu và so sánh các thuật toán tìm kiếm cho bài toán 8-puzzle
- **Thuật toán được implement:**
  - **BFS (Breadth-First Search):** Tìm kiếm theo chiều rộng
  - **A* với Manhattan Distance:** Heuristic dựa trên khoảng cách Manhattan
  - **A* với Misplaced Tiles:** Heuristic dựa trên số ô sai vị trí
- **Tính năng:**
  - So sánh hiệu quả giữa các thuật toán
  - Visualization cây tìm kiếm bằng Graphviz
  - Thống kê số node được mở rộng, thời gian thực thi
  - Tạo state ngẫu nhiên để test
  - Multiple goal states (4 trạng thái đích khác nhau)

#### **Classes chính:**
- **`Node`:** Đại diện cho một trạng thái trong 8-puzzle
- **`A_star`:** Thuật toán A* với heuristic tùy chỉnh
- **`BFS`:** Thuật toán tìm kiếm theo chiều rộng
- **`ManhattanHeuristic`:** Heuristic Manhattan Distance
- **`MisplacedHeuristic`:** Heuristic Misplaced Tiles

#### **Kết quả thực nghiệm:**
- **A* Manhattan:** Hiệu quả cao nhất (142 nodes, 45.65ms)
- **A* Misplaced:** Hiệu quả trung bình (162 nodes, 28.78ms)  
- **BFS:** Chậm nhất (14,464 nodes, 3710.29ms)

### 🎮 **Task 2: Pacman Game**

#### `main.py` - Entry Point chính
- **Chức năng:** Entry point chính của ứng dụng
- **Tính năng:** Kiểm tra dependencies, khởi động game
- **Tích hợp:** Tự động import và chạy integrated game manager
- **Cách chạy:** `python main.py`

### 🧠 File logic game (src/)

#### `game.py` - Layout Manager (Tạo mê cung)
- **Chức năng:** Tạo và quản lý mê cung từ file text
- **Tính năng:** 
  - Đọc file mê cung từ thư mục `input/`
  - Phân tích ký tự để tạo thành phần game
  - Xoay ma trận 90 độ mỗi 30 bước
  - Quản lý teleport và cổng thoát
- **Thuộc tính:** `walls`, `food`, `ghosts`, `magical_pies`, `exit_gates`

#### `agent.py` - AI Agent (Trí tuệ nhân tạo)
- **Chức năng:** Điều khiển game tự động với AI
- **Thuật toán:** Tích hợp A* search algorithm
- **Tính năng:**
  - Tìm đường đi tối ưu
  - Tránh ma thông minh
  - Ăn thức ăn và bánh kỳ diệu
  - Xử lý xoay ma trận động

#### `pacman.py` - Manual Pacman (Điều khiển thủ công)
- **Chức năng:** Điều khiển game thủ công
- **Tính năng đặc biệt:**
  - Điều khiển bằng phím mũi tên/WASD
  - Teleport thủ công giữa các góc
  - Ăn tường khi có power (magical pie)
  - Tự động điều chỉnh kích thước cửa sổ
  - Xoay ma trận mỗi 30 bước

#### `base_pacman.py` - Base Game Logic + Ghost
- **Chức năng:** Lớp cơ sở chung cho cả AI và Manual
- **Tính năng:**
  - Logic game chung (ăn thức ăn, power, game over)
  - Xoay ma trận và cập nhật tọa độ
  - Ghost class với AI di chuyển
  - Teleport và ăn tường
- **Classes:** `BasePacmanGame`, `Ghost`

#### `visualize.py` - Visualization Engine (Đồ họa)
- **Chức năng:** Tất cả xử lý đồ họa và hiển thị
- **Tính năng:**
  - Vẽ mê cung, Pacman, ma, thức ăn
  - Animation system cho Pacman
  - Movement controller với interpolation
  - Hiệu ứng thắng/thua
  - Tự động resize cửa sổ
  - Scale Pacman theo kích thước mê cung
- **Classes:** `Direction`, `PacmanAnimation`, `Movement`, `GameVisualizer`

#### `search.py` - A* Search Algorithm
- **Chức năng:** Thuật toán tìm kiếm A* cho AI
- **Tính năng:**
  - A* search với heuristic thông minh
  - Tìm đường đi tối ưu
  - Tránh ma và tối ưu hóa pathfinding
  - Xử lý teleport và rotation

#### `state.py` - State Management
- **Chức năng:** Quản lý trạng thái game
- **Thuộc tính:** Vị trí Pacman, hướng di chuyển, thức ăn còn lại

### 🎨 File tài nguyên

#### `assets/` - Tài nguyên đồ họa
- **`Ghost_image/`:** Hình ảnh ma (unnamed.png)
- **`pacman_images/`:** Các frame hoạt ảnh Pacman (1.png, 2.png, 3.png, 4.png)

#### `input/` - File đầu vào
- **`task02_pacman_example_map.txt`:** File map mẫu cho game

#### `output/` - File đầu ra
- **`output.txt`:** Kết quả chế độ AI
- **`output_manual.txt`:** Kết quả chế độ thủ công
- **`Path.txt`:** Đường đi AI
- **`Path_manual.txt`:** Đường đi thủ công

#### `src/` - Mã nguồn chính
- **`__pycache__/`:** Cache Python
- **`agent.py`:** AI Agent - Trí tuệ nhân tạo
- **`base_pacman.py`:** Base class + Ghost class
- **`game.py`:** Layout Manager - Tạo mê cung
- **`pacman.py`:** Manual Pacman - Điều khiển thủ công
- **`search.py`:** Thuật toán tìm kiếm A*
- **`state.py`:** Quản lý trạng thái game
- **`visualize.py`:** Visualization Engine - Đồ họa

## 🚀 Cách chạy chương trình

### 📋 Yêu cầu hệ thống
- **Python:** 3.8 trở lên
- **Thư viện:** pygame, numpy, graphviz, jupyter
- **OS:** Windows, macOS, Linux

### 🔧 Cài đặt
```bash
# Cài đặt các thư viện cần thiết
pip install pygame numpy graphviz jupyter

# Hoặc cài đặt từng thư viện riêng lẻ
pip install pygame      # Cho Task2 (Pacman Game)
pip install numpy       # Cho Task1 (8-Puzzle)
pip install graphviz    # Cho visualization
pip install jupyter     # Cho Task1 notebook
```

### 🧩 **Task 1: 8-Puzzle Problem**

#### **Cách chạy Task1:**
```bash
# Mở Jupyter notebook
cd source/Task1
jupyter notebook Task1.ipynb
```

#### **Nội dung Task1:**
- **Cell 1-2:** Định nghĩa Node class và A* algorithm
- **Cell 3:** Tách heuristic riêng biệt (Manhattan, Misplaced)
- **Cell 4:** BFS algorithm
- **Cell 5:** Visualization function
- **Cell 6-14:** Test cases và so sánh hiệu quả

#### **Kết quả mong đợi:**
- So sánh hiệu quả giữa BFS, A* Manhattan, A* Misplaced
- Visualization cây tìm kiếm
- Thống kê số node được mở rộng và thời gian thực thi

### 🎮 **Task 2: Pacman Game**

#### **Cách chạy Task2:**
```bash
# Chạy entry point chính (Khuyến nghị)
cd source/Task2
python main.py
```

#### **Các chế độ chơi:**
- **Chế độ AI:** Game tự động với thuật toán A*
- **Chế độ Manual:** Điều khiển thủ công với phím
- **Tính năng đặc biệt:** Xoay ma trận, teleport, ăn tường

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
- **A* (A-Star):** Thuật toán chính với heuristic thông minh
- **Dynamic Search:** Tìm kiếm động thích ứng với môi trường
- **Ghost Avoidance:** Tránh ma thông minh
- **Path Optimization:** Tối ưu hóa đường đi

### **Tính năng đặc biệt:**
- **Xoay ma trận động:** Mỗi 30 bước
- **Teleport thủ công:** Giữa các góc mê cung
- **Ăn tường:** Khi có power từ magical pie
- **Tự động resize:** Cửa sổ thích ứng với kích thước mê cung

### **Tối ưu hóa:**
- **OOP Design:** Code được tổ chức theo hướng đối tượng với inheritance
- **Code Consolidation:** Gom các file liên quan vào một file duy nhất
- **Clean Code:** Loại bỏ tên có gạch chân, tối ưu performance
- **Memory Management:** Quản lý bộ nhớ hiệu quả
- **Error Handling:** Xử lý lỗi robust
- **File Organization:** Giảm từ 10 file xuống 7 file



## 🤝 Đóng góp

Dự án này được phát triển cho mục đích học tập và nghiên cứu về Trí Tuệ Nhân Tạo. Mọi đóng góp và phản hồi đều được chào đón!

## 📝 License

Dự án được phát triển cho mục đích giáo dục và nghiên cứu.

---

**🎮 Chúc bạn chơi game vui vẻ! 🎮**
