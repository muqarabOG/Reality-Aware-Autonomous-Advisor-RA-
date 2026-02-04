import heapq
import numpy as np
from typing import List, Tuple

class TacticalPathfinder:
    def __init__(self, grid_size: int = 40, resolution: float = 1.0):
        """
        grid_size: size of the arena in meters (assumed square)
        resolution: meters per grid cell
        """
        self.size = int(grid_size / resolution)
        self.res = resolution
        self.offset = grid_size / 2
        self.grid = np.zeros((self.size, self.size))

    def _to_grid(self, pos: List[float]) -> Tuple[int, int]:
        gx = int((pos[0] + self.offset) / self.res)
        gy = int((pos[1] + self.offset) / self.res)
        # Clip to grid boundaries
        gx = max(0, min(gx, self.size - 1))
        gy = max(0, min(gy, self.size - 1))
        return (gx, gy)

    def _to_coord(self, grid_pos: Tuple[int, int]) -> List[float]:
        cx = (grid_pos[0] * self.res) - self.offset
        cy = (grid_pos[1] * self.res) - self.offset
        return [cx, cy]

    def update_obstacles(self, entities: List[any]):
        """Clears grid and marks obstacle zones based on detected entities."""
        self.grid = np.zeros((self.size, self.size))
        for ent in entities:
            # For Path E, we treat certain labels as obstacles
            # We don't have exact coordinates for vision entities in this mock,
            # so we'll simulate an obstacle at a known distance if it's high risk.
            # In a real system, we'd use Depth or LIDAR to place them.
            pass

    def add_manual_obstacle(self, pos: List[float], radius: float = 2.0):
        gx, gy = self._to_grid(pos)
        r_cells = int(radius / self.res)
        for i in range(gx - r_cells, gx + r_cells + 1):
            for j in range(gy - r_cells, gy + r_cells + 1):
                if 0 <= i < self.size and 0 <= j < self.size:
                    dist = ((i - gx)**2 + (j - gy)**2)**0.5
                    if dist <= r_cells:
                        self.grid[i, j] = 1 # Mark as blocked

    def find_path(self, start_pos: List[float], goal_pos: List[float]) -> List[List[float]]:
        start = self._to_grid(start_pos)
        goal = self._to_grid(goal_pos)
        
        # If start is blocked, find nearest free cell
        if self.grid[start] == 1:
            start = self._find_nearest_free(start)
            
        # If goal is blocked, find nearest free cell
        if self.grid[goal] == 1:
            goal = self._find_nearest_free(goal)

        frontier = []
        heapq.heappush(frontier, (0, start))
        came_from = {start: None}
        cost_so_far = {start: 0}

        while frontier:
            current_priority, current = heapq.heappop(frontier)

            if current == goal:
                break

            for next_node in self._get_neighbors(current):
                new_cost = cost_so_far[current] + 1
                if next_node not in cost_so_far or new_cost < cost_so_far[next_node]:
                    cost_so_far[next_node] = new_cost
                    priority = new_cost + self._heuristic(goal, next_node)
                    heapq.heappush(frontier, (priority, next_node))
                    came_from[next_node] = current

        # Reconstruct path
        path = []
        curr = goal
        if goal not in came_from:
            return [] # No path found
            
        while curr is not None:
            path.append(self._to_coord(curr))
            curr = came_from[curr]
        
        path.reverse()
        return path

    def _find_nearest_free(self, pos: Tuple[int, int]) -> Tuple[int, int]:
        """BFS to find the closest non-blocked cell."""
        q = [pos]
        visited = {pos}
        while q:
            curr = q.pop(0)
            if self.grid[curr] == 0:
                return curr
            for neighbor in self._get_neighbors_raw(curr):
                if neighbor not in visited:
                    visited.add(neighbor)
                    q.append(neighbor)
        return pos # Fallback

    def _get_neighbors_raw(self, pos):
        (x, y) = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [(nx, ny) for nx, ny in neighbors if 0 <= nx < self.size and 0 <= ny < self.size]

    def _heuristic(self, a, b):
        return abs(a[0] - b[0]) + abs(a[1] - b[1])

    def _get_neighbors(self, pos):
        (x, y) = pos
        neighbors = [(x+1, y), (x-1, y), (x, y+1), (x, y-1), 
                     (x+1, y+1), (x-1, y-1), (x+1, y-1), (x-1, y+1)]
        results = []
        for nx, ny in neighbors:
            if 0 <= nx < self.size and 0 <= ny < self.size:
                if self.grid[nx, ny] == 0: # Free
                    results.append((nx, ny))
        return results
