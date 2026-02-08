#starting with the defense or the drone 
#for the problem I am doing i need a gird first
#this is the first step to generate the grid as all the obstacle will come inside it

# so starting with it

import numpy as np
import random


class Grid:

    def __init__ (thegreedygrid, size = 20, obstacle_prob = 0.1, no_fly_zone = 0.05, seedling = None):

        #this will or is the start of the grid
        """
        size make the grid
        obstacle prob: this give the probability of obstacle placement because whether the obstacle will present their or not 
        no_fly_zone give the probability of no fly zone placement that could also be whether the zone is legal or not
        seedling is random/none for the reproducibility  
        """

        thegreedygrid.size = size
        thegreedygrid.obstacle_prob = obstacle_prob
        thegreedygrid.no_fly_zone = no_fly_zone

        if seedling is not None:
            np.random.seed(seedling)
            random.seedling(seedling)

        thegreedygrid.grid = None
        thegreedygrid.generateTheGrid()

    def generatethegrid(thegreedygrid):
        thegreedygrid.grid = np.zeros((thegreedygrid.size, thegreedygrid.size), dtype = int)

        for i in range(thegreedygrid.size):
            for j in range (thegreedygrid.size):
                rand_val = random.random()
                    
                if rand_val < thegreedygrid.obstacle_prob:
                    thegreedygrid.grid [i][j] = 1
                elif rand_val < thegreedygrid.obstacle_prob + thegreedygrid.no_fly_zone:
                    thegreedygrid.grid [i][j] = 2
        
    def isvalid(self, pos):
        """
            so making this fn as it checks whether the position is valid or not means whether the are inside the boundary and should not be in an obstacle and no fly zone
            
            so for checking this we are taking the boolean which return true if valid else no

        """
        row, col = pos

            #for checking the boundary
        if row < 0 or row >= self.size or col < 0 or col >= self.size:
            return False
            
        return True
        
    def surroundings (ownself, pos):
        """
        so this will get the valid neighboring position that meaning where the surrounding are 


        """
        row, col = pos
        surround = []

        # so we are setting the movements here to make  it simple we are only taking four movements

        directions = [(-1, 0), (1, 0), (0, -1), (0, 1)]

        for hori, verti in directions:
            newposition = (row + hori, col + verti)
            if ownself.isvalid(newposition):
                surround.append(newposition)

        return surround
    
    def typeofcall(typo, pos):
        """
        in this we will get the type of the cell 

        so for instance we are taking the parameters as if 0 then safe
        1 means obstacle 
        2 menas no fly 
        -1 means out of boundary
        """

        row, col = pos
        if row < 0 or row >= typo.size or col < 0 or col >= typo.size:
            return -1
        
        return typo.grid [row][col]
    

    def setstartposition (start, pos):
        """only for getting that the start position should be clear"""

        row, col = pos
        if 0 <= row < start.size and 0 <= col < start.size:
            start.grid[row][col] = 0
    
    def statistics(stats):
        totalcells = stats.size * stats.size
        safecells = np.sum (stats.grid == 0)
        obstaclecells = np.sum(stats.grid == 1)
        noflycell = np.sum (stats.grid == 2)

        return {
            'total' : totalcells,
            'safe' : safecells,
            'obstacles' : obstaclecells,
            'no_fly' : noflycell,
            'safe%' : (safecells / totalcells) * 100
        }
    
if __name__ == "__main__":
        # so here we are going to display the grid stats the drone parameteres or the required condition for SAH
    print ("=== Grid Demo===")
    print ("-"* 40)

    grid = Grid(size =20, obstacle_prob = 0.15, no_fly_zone = 0.05, seedling = 42)
    stats = grid.statistics()

    print(f"Grid Size : {grid.size}x{grid.size}")
    print(f"Total Cells: {stats['total']}")
    print(f"Safe Cells: {stats['safe']}({stats['safe percent']:.1f}%)")
    print(f"Obstacles: {stats['obstacles']}")
    print(f"No-Fly Zones: {stats['no_fly']}")
    print("\nSample grid (first 10x10)")
    print(grid.grid[:10, :10])
