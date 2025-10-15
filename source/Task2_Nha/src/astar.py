import heapq
from heuristic import Heuristic

class AStar:
    def __init__(self, initial_node, heuristic_name):
        self.initial_node = initial_node  # Pacman ban đầu (đã là Node)
        self.heuristic_name = heuristic_name  
        self.nodes_explored = [] # Danh sách các node đã được khám phá

    def solve(self):
        frontier = [] # Danh sách chứa các trạng thái đang chờ được thực hiện (priority queue)

        heuristic_func = getattr(Heuristic, self.heuristic_name)
        h_value = heuristic_func(self.initial_node.get_state(), self.initial_node.remaining_food)
        self.initial_node.h = h_value
        self.initial_node.f = self.initial_node.g + h_value
        heapq.heappush(frontier, (self.initial_node.f, self.initial_node))
        closed_set = set()

        while frontier:
            _, current = heapq.heappop(frontier)
            if current.get_state() in closed_set:
                continue
            self.nodes_explored.append(current)
            closed_set.add(current.get_state())

            if current.is_goal():
                return self.reconstruct_path(current)

            for successor in current.get_successors():
                h_value = heuristic_func(successor.get_state(), successor.remaining_food)
                successor.h = h_value
                successor.f = successor.g + h_value
                if successor.get_state() not in closed_set:
                    heapq.heappush(frontier, (successor.f, successor))

        return None

    def reconstruct_path(self, node):
        path = []
        actions = []
        current = node
        while current.parent:  # Dừng khi current.parent là None (trạng thái ban đầu)
            # Xác định hành động từ parent đến current
            dx = current.x - current.parent.x
            dy = current.y - current.parent.y
            
            if (dx, dy) == (-1, 0):
                action = "North"
            elif (dx, dy) == (1, 0):
                action = "South"
            elif (dx, dy) == (0, -1):
                action = "West"
            elif (dx, dy) == (0, 1):
                action = "East"
            else:
                action = "Stop" 
            
            actions.append(action)
            path.append((current.x, current.y))
            current = current.parent
        
        # Thêm trạng thái ban đầu
        path.append((current.x, current.y))
        
        # Đảo ngược để có thứ tự từ start đến goal
        path = path[::-1]
        actions = actions[::-1]  # Hành động từ start đến goal
        
        total_cost = node.g  # Tổng chi phí là node.g của goal
        
        return {
            "path": path,          # Đường đi (tọa độ)
            "actions": actions,    # Danh sách hành động
            "total_cost": total_cost  # Tổng chi phí
        }