
import numpy as np
from a_star import a_star_search, find_the_nearest_unvisited

class CoveragePlanner:

    def __init__(self, grid, drone):
        self.grid = grid
        self.drone = drone


    def get_unvisited_safe_cells(self):
        unvisited = set()
        for i in range(self.grid.size):
            for j in range(self.grid.size):
                posture = (i, j)
                if self.grid.isvalid(posture) and posture not in self.drone.visited:
                    unvisited.add(posture)
        return unvisited
    
    def plan_zigzag_coverage(self):
        coverage_path = []

        for row in range(self.grid.size):
            if row % 2 == 0: 
                cols = range(self.grid.size)
            else: 
                cols = range(self.grid.size - 1, -1, -1)

            for col in cols:
                target = (row, col)
                if self.grid.isvalid(target):
                    coverage_path.append(target)
        return coverage_path
    
    def plan_adaptive_coverage(self, battery_limit=None, end_point=None):
        if battery_limit is None:
            battery_limit = self.drone.battery_capacity * 0.2 

        full_path = []
        unvisited = self.get_unvisited_safe_cells()

        while unvisited and self.drone.battery > battery_limit:
            # If we have an endpoint, reserve battery to reach it
            if end_point:
                from a_star import distance, a_star_search
                # Calculate distance to endpoint
                dist_to_end = distance(self.drone.position, end_point)
                # Reserve battery with safety margin
                reserve = dist_to_end * 1.5
                
                # If we're running low on battery, navigate to endpoint
                if self.drone.battery < reserve + battery_limit + 10:
                    path_to_end = a_star_search(self.grid, self.drone.position, end_point)
                    if path_to_end and len(path_to_end) > 1:
                        full_path.extend(path_to_end[1:])
                    break
            
            target_posture, path = find_the_nearest_unvisited(self.grid, self.drone, unvisited)

            if path is None:
                break

            path_cost = len(path) - 1 
            
            # Check if we have enough battery (including endpoint reserve if applicable)
            effective_limit = battery_limit
            if end_point:
                from a_star import distance
                dist_to_end = distance(self.drone.position, end_point)
                effective_limit = battery_limit + dist_to_end * 1.5
            
            if self.drone.battery < path_cost + effective_limit:
                break 

            full_path.extend(path[1:])

            for posture in path:
                if posture in unvisited:
                    unvisited.remove(posture)

        return full_path


    def plan_greedy_coverage(self, look_ahead=5):
        unvisited = self.get_unvisited_safe_cells()
        path = []

        while unvisited and self.drone.can_move():
            best_cell = None
            best_score = -1
            best_path = None

            current_pos = self.drone.position 
            candidates = [cell for cell in unvisited
                          if abs(cell[0] - current_pos[0]) + abs(cell[1] - current_pos[1]) <= look_ahead]
            
            for cell in candidates[:20]: 
                cell_path = a_star_search(self.grid, self.drone.position, cell)
                if not cell_path:
                    continue

                score = sum(1 for surrounding in self.grid.surroundings(cell)
                            if surrounding in unvisited)
                
                score = score - len(cell_path) * 0.1

                if score > best_score:
                    best_score = score
                    best_cell = cell
                    best_path = cell_path

            if best_path is None:
                break

            path.extend(best_path[1:])  
           
            for posture in best_path:
                if posture in unvisited:
                    unvisited.remove(posture)

        return path
    
    def estimate_coverage_percent(self, path):
        visited = set(path)
        total_safe = int(np.sum(self.grid.grid == 0))

        if total_safe == 0:
            return 0.0
        
        return (len(visited) / total_safe) * 100
    

if __name__ == "__main__":
    from grid import Grid
    from drone import Drone

    print("=== Coverage Planner Demo ===")
    print("-" * 40)

    grid = Grid(size=10, obstacle_prob=0.15, seedling=42)
    grid.setstartposition((0, 0))
    drone = Drone(startposition=(0,0), battery_capacity=150)

    planner = CoveragePlanner(grid, drone)

    print("Testing adaptive coverage....")
    path = planner.plan_adaptive_coverage(battery_limit=20)


    print(f"[OK] Generated path with {len(path)} steps")
    coverage = planner.estimate_coverage_percent(path)
    print(f"Estimated coverage: {coverage:.1f}%")
    print(f"Battery needed: {len(path)} units")

    total_safe = int(np.sum(grid.grid == 0))
    print(f"\nGrid stats: {total_safe} safe cells")