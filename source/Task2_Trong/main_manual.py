import sys
import os
import re

# Thêm thư mục src vào Python path
SRC_DIR = os.path.join(os.path.dirname(__file__), 'src')
sys.path.insert(0, SRC_DIR)

from game import Layout
from manual_pacman import ManualPacmanGame


def main(input_filename="task02_pacman_example_map.txt", output_filename="output_manual.txt", path_filename="Path_manual.txt"):
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
        return

    game = ManualPacmanGame(layout)
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


if __name__ == '__main__':
    main()
