

import numpy as np
from a_star import a_star_search, findTheNearestUnvisited

class CoveragePlanner:

    def __Planner__(plan, grid, drone):

        plan.grid = grid
        plan.drone = drone


    def gettingUnvisitedSafeCells(safe):


        unvisited = set()
        for i in range (safe.grid.size):
            for j in range(safe.grid.size):
                pos = (i, j)
                if safe.grid.isvalid(pos) and pos not in safe.drone.visited:
                    unvisited.add(pos)
        return unvisited
    
    def plan_zigzag_coverage(self):
         

        coveragePath = []

        for row in range(self.grid.size):
            if row % 2 == 0: 
                cols = range(self.grid.size)
            else: 
                cols = range (self.grid.size - 1, -1, -1)

            for col in cols:
                target = (row, col)
                if self.grid.isvalid(target):
                    coveragePath.append(target)
        return coveragePath
    
    def plan_adaptiveCoverage(plan, battery_limit = None):
        

        if battery_limit is None:
            bettery_limit = plan.drone.battery_capacity * 0.2 

        fullPath = []
        unvisited = plan.gettingUnvisitedSafeCells()

        while unvisited and plan.drone.battery > battery_limit:

            target_pos, path = findTheNearestUnvisited( plan.grid, plan.drone, unvisited)

            if path is None:
                break

            path_cost = len(path) -1 
            if plan.drone.battery < path_cost + battery_limit:
                break 

            fullPath.extend(path[1:])

            
            for pos in path:
                if pos in unvisited:
                    unvisited.remove(pos)

        return fullPath
    def planGreedyCoverage(self, look_ahead = 5):
        
        

        
        unvisited = self.gettingUnvisitedSafeCells()
        path = []

        while unvisited and self.drone.can_move():
            
            best_cell = None
            best_score = -1
            best_path = None

           

            current_pos = self.drone.position 
            candidates = [cell for cell in unvisited
                          if abs (cell[0] - current_pos[0]) + abs(cell[1] - current_pos[1]) <= look_ahead]
            
            for cell in candidates[:20]: 
                
                cell_path = a_star_search(self.grid , self.drone.position, cell)
                if not cell_path:
                    continue

                
                score = sum(1 for surrounding in self.grid.get_surroundings(cell)
                            if surrounding in unvisited)
                
               
                score = score - len(cell_path) * 0.1

                if score > best_score:
                    best_score = score
                    best_cell = cell
                    best_path = cell_path

            if best_path is None:
                break

            
            path.extend(best_path[1:])  
           
            for pos in best_path:
                if pos in unvisited:
                    unvisited.remove(pos)

        return path
    
    def estimatecoveragePercent(self, path):
        
        visited = set(path)
        total_safe = np.sum(self.grid.grid == 0)

        if total_safe == 0:
            return 0.0
        
        return (len(visited) / total_safe) * 100
    

if __name__ == "__main__":
   
    from grid import Grid
    from drone import Drone

    print("=== Coverage Planner Demo ===")
    print("-" * 40)

    
    grid = Grid(size = 10, obstacle_prob = 0.15, seedling =42)
    grid.setstartposition((0, 0))
    drone = Drone(startposition=(0,0), batteryCapacity = 150)

    
    planner = CoveragePlanner(grid, drone)

    print("Testing adaptive coverage....")
    path = planner.plan_adaptivecoverage(battery_limit = 20)


    print(f"[OK] Generated path with {len(path)} steps")
    coverage = planner.estimatecoveragePercent(path)
    print(f"Estimated coverage: {coverage:.1f}%")
    print(f"Battery needed: {len(path)}units")

    total_safe = np.sum(grid.grid == 0)
    print(f"\nGrid stats: {total_safe} safe cells")