#here is the 4th step of the project
"""in this we are making it smart that means implement coverage logic
also here we are combine the drone , grid , and a* which was their  from step  1 to step 3
the drone decides where to go next based on the unvisited cells and battery

coverage planner fro drone path optimizer 
"""

import numpy as np
from a_star import a_star_search, findTheNearestUnvisited

class CoveragePlanner:
    """this cover paths  for maximum area coverage"""

    def __Planner__(plan, grid, drone):
        # grid means the grid object, drone means the drone object

        plan.grid = grid
        plan.drone = drone


    def gettingUnvisitedSafeCells(safe):
        # gettomg the set of all unvisited safe cells 

        #this returns the set of unvisited safe cell positions

        unvisited = set()
        for i in range (safe.grid.size):
            for j in range(safe.grid.size):
                pos = (i, j)
                if safe.grid.isvalid(pos) and pos not in safe.drone.visited:
                    unvisited.add(pos)
        return unvisited
    
    def plan_zigzag_coverage(self):
        # this generate coverage pattern adapts to obstacles using a* pathfinding
         
         #this retrun list as complete path as list of positions

        coveragePath = []
        #this generate the zigzag target points 

        for row in range(self.grid.size):
            if row % 2 == 0: #move from left to right
                cols = range(self.grid.size)
            else: #right to left 
                cols = range (self.grid.size - 1, -1, -1)

            for col in cols:
                target = (row, col)
                if self.grid.isvalid(target):
                    coveragePath.append(target)
        return coveragePath
    
    def plan_adaptiveCoverage(plan, battery_limit = None):
        # this considers battery and obstacles uses nesrest surround with a* pathfinding

        #battery limit i.e the optional battery limit which stops if the battery gets low
        
        #and in final returns the list as path as list of positions

        if battery_limit is None:
            bettery_limit = plan.drone.battery_capacity * 0.2 #this will stop the drone at 20%

        fullPath = []
        unvisited = plan.gettingUnvisitedSafeCells()

        while unvisited and plan.drone.battery > battery_limit:

            target_pos, path = findTheNearestUnvisited( plan.grid, plan.drone, unvisited)

            if path is None:
                break

            path_cost = len(path) -1 #subtract one as path include the initial position
            if plan.drone.battery < path_cost + battery_limit:
                break # means not enough battery

            fullPath.extend(path[1:])

            #updating the visited cells
            for pos in path:
                if pos in unvisited:
                    unvisited.remove(pos)

        return fullPath
    def planGreedyCoverage(self, look_ahead = 5):
        #this prioritizes cells with most unvisited neighbors
        # lookahead gives the number of steps to look ahead

        #returns the list as path as list of positions 

        unvisited = self.gettingUnvisitedSafeCells()
        path = []

        while unvisited and self.drone.can_move():
            #gives the scoring to eachh unvisited cell by number of unvisited surroundings
            best_cell = None
            best_score = -1
            best_path = None

            #check the nearby cells within the look ahead distance

            current_pos = self.drone.position 
            candidates = [cell for cell in unvisited
                          if abs (cell[0] - current_pos[0]) + abs(cell[1] - current_pos[1]) <= look_ahead]
            
            for cell in candidates[:20]: 
                #here we find the path to the cell
                cell_path = a_star_search(self.grid , self.drone.position, cell)
                if not cell_path:
                    continue

                #score based on unvisited surrounding
                score = sum(1 for surrounding in self.grid.get_surroundings(cell)
                            if surrounding in unvisited)
                
                #prefer close cells or break ties
                score = score - len(cell_path) * 0.1

                if score > best_score:
                    best_score = score
                    best_cell = cell
                    best_path = cell_path

            if best_path is None:
                break

            #add path 
            path.extend(best_path[1:])  #skips the current position

            #update unvisited
            for pos in best_path:
                if pos in unvisited:
                    unvisited.remove(pos)

        return path
    
    def estimatecoveragePercent(self, path):
        """estimate coverage percentage for a given path
        path: list of positions
        return the float which estimate coverage percentage (0-100)"""

        visited = set(path)
        total_safe = np.sum(self.grid.grid == 0)

        if total_safe == 0:
            return 0.0
        
        return (len(visited) / total_safe) * 100
    

if __name__ == "__main__":
    # this will give the demo which means coverage planning
    from grid import Grid
    from drone import Drone

    print("=== Coverage Planner Demo ===")
    print("-" * 40)

    #here creating the grid and the drone
    grid = Grid(size = 10, obstacle_prob = 0.15, seedling =42)
    grid.setstartposition((0, 0))
    drone = Drone(startposition=(0,0), batteryCapacity = 150)

    #plan coverage
    planner = CoveragePlanner(grid, drone)

    print("Testing adaptive coverage....")
    path = planner.plan_adaptivecoverage(battery_limit = 20)


    print(f"[OK] Generated path with {len(path)} steps")
    coverage = planner.estimatecoveragePercent(path)
    print(f"Estimated coverage: {coverage:.1f}%")
    print(f"Battery needed: {len(path)}units")

    total_safe = np.sum(grid.grid == 0)
    print(f"\nGrid stats: {total_safe} safe cells")