import heapq
from collections import deque
from visualize import Direction


# ============================ BFS metric dùng cho heuristic ============================
def bfs_metric(layout, start, passable_fn):
    q = deque([start])
    dist = {start: 0}
    while q:
        x, y = q.popleft()
        for dx, dy in ((1,0),(-1,0),(0,1),(0,-1)):
            nx, ny = x + dx, y + dy
            if 0 <= nx < layout.width and 0 <= ny < layout.height:
                if (nx, ny) not in dist and passable_fn((nx, ny)):
                    dist[(nx, ny)] = dist[(x, y)] + 1
                    q.append((nx, ny))
    return dist


def prim_mst(points, dist_cache):
    if not points:
        return 0
    used = {points[0]}
    total = 0
    while len(used) < len(points):
        best = float("inf")
        best_v = None
        for u in used:
            du = dist_cache[u]
            for v in points:
                if v in used:
                    continue
                d = du.get(v, float("inf"))
                if d < best:
                    best = d
                    best_v = v
        if best == float("inf"):
            return float("inf")
        total += best
        used.add(best_v)
    return total


# ============================ Heuristic Lower Bound ============================
class heuristic:
    def __init__(self, problem):
        self.problem = problem
        self.layout = problem.layout

        def is_wall(pos):
            x, y = pos
            try:
                return problem.isWall(pos)
            except TypeError:
                return problem.isWall(x, y)

        self.passable = lambda pos: not is_wall(pos)
        self.cache = {}

    def d(self, src):
        if src not in self.cache:
            self.cache[src] = bfs_metric(self.layout, src, self.passable)
        return self.cache[src]

    def h(self, cur, remaining_dots, exits):
        if not remaining_dots:
            if not exits:
                return 0
            dcur = self.d(cur)
            return min(dcur.get(e, float("inf")) for e in exits) or 0

        dcur = self.d(cur)
        nd = min(dcur.get(p, float("inf")) for p in remaining_dots)

        dist_cache = {p: self.d(p) for p in remaining_dots}
        mst = prim_mst(remaining_dots, dist_cache)

        if exits:
            to_exit = min(
                dist_cache[p].get(e, float("inf"))
                for p in remaining_dots
                for e in exits
            )
        else:
            to_exit = 0

        total = 0
        for v in (nd, mst, to_exit):
            if v != float("inf"):
                total += v
        return total


# ============================ A* Search Implementation ============================
class astar:
    def __init__(self, problem, corners=None):
        self.problem = problem
        self.corners = corners or {}
        self.recent_positions = deque(maxlen=8)
        self.hfun = heuristic(problem)

    def collect_game_facts(self, state):
        pos = state.getPosition()
        layout = self.problem.layout
        food_grid = self.problem.getFoodGrid()
        dots = [
            (x, y)
            for y in range(layout.height)
            for x in range(layout.width)
            if food_grid[y][x]
        ]
        exits = list(getattr(layout, "exit_gates", []))
        pies = set(self.problem.getMagicalPies())
        return pos, dots, exits, pies

    def is_goal(self, pos, dots, exits):
        return (not dots) and (pos in exits if exits else False)

    def neighbors_game(self, pos):
        for nxt, direction, cost in self.problem.getSuccessors(pos):
            if direction == Direction.STOP and nxt == pos:
                continue
            yield nxt, direction, cost

    def first_safe_or_best(self, start_pos):
        best_dir = Direction.STOP
        for nxt, direction, _ in self.problem.getSuccessors(start_pos):
            if direction != Direction.STOP:
                best_dir = direction
                break
        return best_dir

    def find_next_action(self, current_state, ghosts):
        start_pos, dots, exits, pies = self.collect_game_facts(current_state)
        if not self.recent_positions or self.recent_positions[-1] != start_pos:
            self.recent_positions.append(start_pos)

        if self.is_goal(start_pos, dots, exits):
            return Direction.STOP

        start_pie_on = 1 if start_pos in pies else 0
        start = (start_pos[0], start_pos[1], start_pie_on, frozenset(dots))

        openh = []
        gscore = {start: 0}
        first_move = {start: Direction.STOP}

        h0 = self.hfun.h(start_pos, dots, exits)
        heapq.heappush(openh, (h0, 0, start))
        visited = set()

        while openh:
            f, g, cur = heapq.heappop(openh)
            if cur in visited:
                continue
            visited.add(cur)

            x, y, pie_on, rem = cur
            cur_pos = (x, y)
            rem = set(rem)
            if cur_pos in rem:
                rem.remove(cur_pos)

            if self.is_goal(cur_pos, rem, exits):
                return first_move[cur]

            for nxt_pos, direction, step_cost in self.neighbors_game(cur_pos):
                nx, ny = nxt_pos
                nxt_pie_on = 1 if nxt_pos in pies else pie_on
                nxt_rem = rem - {nxt_pos} if nxt_pos in rem else rem
                nxt_state = (nx, ny, nxt_pie_on, frozenset(nxt_rem))

                ng = g + step_cost
                if nxt_pos in self.recent_positions:
                    ng += 2

                if nxt_state not in gscore or ng < gscore[nxt_state]:
                    gscore[nxt_state] = ng
                    h = self.hfun.h(nxt_pos, list(nxt_rem), exits)
                    if h == float("inf"):
                        h = 0
                    nf = ng + h
                    heapq.heappush(openh, (nf, ng, nxt_state))
                    if cur == start:
                        first_move[nxt_state] = direction
                    else:
                        first_move[nxt_state] = first_move[cur]

        return self.first_safe_or_best(start_pos)
