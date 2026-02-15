
import numpy as np
import random


class Grid:

    def __init__(self, size=20, obstacle_prob=0.1, no_fly_zone=0.05, seedling=None):
        self.size = size
        self.obstacle_prob = obstacle_prob
        self.no_fly_zone = no_fly_zone

        if seedling is not None:
            np.random.seed(seedling)
            random.seed(seedling)

        self.grid = None
        self.generateTheGrid()

    def generateTheGrid(self):
        self.grid = np.zeros((self.size, self.size), dtype=int)

        for i in range(self.size):
            for j in range(self.size):
                rand_val = random.random()
                    
                if rand_val < self.obstacle_prob:
                    self.grid[i][j] = 1
                elif rand_val < self.obstacle_prob + self.no_fly_zone:
                    self.grid[i][j] = 2
    
    def load_scenario(self, scenario_type):
        """Load a specific scenario type"""
        self.grid = np.zeros((self.size, self.size), dtype=int)
        
        if scenario_type == 'Random':
            self.generateTheGrid()
            
        elif scenario_type == 'Maze':
            # recursive backtracking or just detailed noise
            for i in range(self.size):
                if i % 2 == 1:
                    for j in range(self.size - 2):
                        self.grid[i][j] = 1
                if i % 4 == 3:
                     self.grid[i][0] = 0 # opening
                     self.grid[i][self.size-3] = 1
        
        elif scenario_type == 'Narrow Passage':
            # Wall in middle with one gap
            mid = self.size // 2
            for i in range(self.size):
                self.grid[i][mid] = 1
            self.grid[mid][mid] = 0 # Gap
            
        elif scenario_type == 'Trap':
            # U-shape
            center = self.size // 2
            radius = 3
            for i in range(center-radius, center+radius+1):
                self.grid[i][center-radius] = 1 # Left
                self.grid[i][center+radius] = 1 # Right
                self.grid[center+radius][i] = 1 # Bottom
                
        elif scenario_type == 'Open':
            # Empty grid with very few obstacles
            # Just borders maybe? Na, just random low prob
            self.obstacle_prob = 0.05
            self.no_fly_zone = 0.0
            self.generateTheGrid()
            
        # Ensure start is safe
        self.setstartposition((0, 0))

        
    def isvalid(self, pos):
        row, col = pos
           
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
            
        cell_value = self.grid[row][col]
        if cell_value == 1 or cell_value == 2:
            return False

        return True
        
    def surroundings(self, pos):
        row, col = pos
        surround = []
        
        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for hori, verti in directions:
            newposition = (row + hori, col + verti)
            if self.isvalid(newposition):
                surround.append(newposition)

        return surround
    
    def typeofcall(self, pos):
        row, col = pos
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return -1
        
        return self.grid[row][col]
    

    def setstartposition(self, pos):
        row, col = pos
        if 0 <= row < self.size and 0 <= col < self.size:
            self.grid[row][col] = 0
    
    def set_cell(self, pos, value):
        """Set a specific cell to a given value (0=safe, 1=obstacle, 2=no-fly)"""
        row, col = pos
        if 0 <= row < self.size and 0 <= col < self.size:
            self.grid[row][col] = value
            return True
        return False
    
    def toggle_obstacle(self, pos):
        """Toggle a cell between safe (0) and obstacle (1)"""
        row, col = pos
        if 0 <= row < self.size and 0 <= col < self.size:
            current = self.grid[row][col]
            # Toggle between safe and obstacle
            if current == 0:
                self.grid[row][col] = 1
            elif current == 1:
                self.grid[row][col] = 0
            # Don't toggle no-fly zones
            return True
        return False
    
    def statistics(self):
        totalcells = self.size * self.size
        # Count cells
        safecells = int(np.sum(self.grid == 0))
        obstaclecells = int(np.sum(self.grid == 1))
        noflycell = int(np.sum(self.grid == 2))

        return {
            'total': totalcells,
            'safe': safecells,
            'obstacles': obstaclecells,
            'no_fly': noflycell,
            'safe%': (safecells / totalcells) * 100
        }
    
if __name__ == "__main__":
    print("=== Grid Demo===")
    print("-" * 40)

    grid = Grid(size=20, obstacle_prob=0.15, no_fly_zone=0.05, seedling=42)
    stats = grid.statistics()

    print(f"Grid Size : {grid.size}x{grid.size}")
    print(f"Total Cells: {stats['total']}")
    print(f"Safe Cells: {stats['safe']}({stats['safe%']:.1f}%)")
    print(f"Obstacles: {stats['obstacles']}")
    print(f"No-Fly Zones: {stats['no_fly']}")
    print("\\nSample grid (first 10x10)")
    print(grid.grid[:10, :10])
