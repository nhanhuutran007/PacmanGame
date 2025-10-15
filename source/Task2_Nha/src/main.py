from utils.path_manager import get_input_file, get_output_file
from maze import Maze
from pacman import Pacman
from astar import AStar
from visualizer import run


def main(input_filename="task02_pacman_example_map.txt", output_filename="Output.txt", path_filename="Path.txt"):

    input_file = get_input_file(input_filename)
    print(f"Loading maze from file: {input_file}")
    output_file = get_output_file(output_filename)
    print(f"Output will be saved to: {output_file}")
    path_file = get_output_file(path_filename)

    
    try:
        maze = Maze(input_file)  # Truyền tên file, Maze sẽ dùng get_input_file
        start_x, start_y = maze.find_pacman()
        initial_food = set(maze.find_food())
        initial_pacman = Pacman(start_x, start_y, initial_food, 0, 0, None, maze)
        
        astar = AStar(initial_pacman, "manhattan")
        path = astar.solve()
        if path:
            if path["path"]:
                # Ghi path vào file path.txt
                with open(path_file, "w") as path_file:
                    path_file.write("[\n")
                    for step in path["path"]:
                        path_file.write(f"  {(step)},\n")
                    path_file.write("]\n")
                
                # Ghi actions và total cost vào file output.txt
                with open(output_file, "w") as f:
                    f.write(f"Total cost: {path['total_cost']}\n")
                    f.write("Actions:\n[\n")
                    for action in path["actions"]:
                        f.write(f"  '{action}',\n")
                    f.write("]\n")
                
                print(f"Output will be saved to {output_file}")
        else:
            with open(output_file, "w") as f:
                f.write("No path found!\n")
            print("No path found!")

        run()  

    except FileNotFoundError as e:
        print(e)

main()