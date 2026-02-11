
import numpy as np
from a_star import a_star_search, findTheNearestUnvisited

class CoveragePlanner:

    def __init__(planning, griding, drone):

        planning.grid = griding
        planning.drone = drone


    def gettingUnvisitedSafeCells(safe):


        unvisited = set()
        for i in range (safe.grid.size):
            for j in range(safe.grid.size):
                posture = (i, j)
                if safe.grid.isvalid(posture) and posture not in safe.drone.visited:
                    unvisited.add(posture)
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
            # Fix variable name typo
            battery_limit = plan.drone.batteryCapacity * 0.2 

        fullPath = []
        unvisited = plan.gettingUnvisitedSafeCells()

        while unvisited and plan.drone.battery > battery_limit:

            target_posture, path = findTheNearestUnvisited( plan.grid, plan.drone, unvisited)

            if path is None:
                break

            path_cost = len(path) -1 
            if plan.drone.battery < path_cost + battery_limit:
                break 

            fullPath.extend(path[1:])

            
            for posture in path:
                if posture in unvisited:
                    unvisited.remove(posture)

        return fullPath
    def planGreedyCoverage(self, look_ahead = 5):
        
        

        
        unvisited = self.gettingUnvisitedSafeCells()
        path = []

        while unvisited and self.drone.canDroneMove():
            
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

                # Fix: call grid.surroundings
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
    # Fix method name call case sensitivity
    path = planner.plan_adaptiveCoverage(battery_limit = 20)


    print(f"[OK] Generated path with {len(path)} steps")
    coverage = planner.estimatecoveragePercent(path)
    print(f"Estimated coverage: {coverage:.1f}%")
    print(f"Battery needed: {len(path)}units")

    total_safe = np.sum(grid.grid == 0)
    print(f"\nGrid stats: {total_safe} safe cells")