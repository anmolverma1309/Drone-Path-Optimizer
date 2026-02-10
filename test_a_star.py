# this is the next step of our process in this we test suite for a* pathfinding

import sys 
import os 
sys.path.insert(0, os.path.abspath(os.path.join.dirname(__file__), '..'))

from grid import Grid
from a_star import a_star_search, distance


def testDistance():
    #test the distance calculation
    assert distance((0, 0), (3, 4)) == 7
    assert distance((0, 0), (0, 0)) == 0
    assert distance((5, 5), (2, 3)) == 5
    print("[OK] distance test passes")


def testPathonemptyGrid():
    """ testing the a* on obstacle free grid"""
    grid = Grid(size = 5, obstacle_prob = 0, no_fly_zone = 0)

    start = (0, 0)
    goal = (4, 4)

    path = a_star_search(grid, start, goal)

    assert path is not None
    assert path[0] == start
    assert path[-1] == goal
    assert len(path) == 9 #distance +1

    print("[OK] Empty grid pathfinding test passed")

def testpathwithObstacles():
    #test a* navigates around obstacles
    grid = Grid (size = 5, seedling = 42)

    #creating a clear path manually to ensure test reliabilityy

    for i in range(5):
        for j in range (5):
            grid.grid[i][j] = 0

    #add an obstacle
    grid.grid[1][1] = 1

    start = (0, 0)
    goal = (2, 2)

    path = a_star_search(grid, start, goal)

    assert path is not None
    assert path[0] == start
    assert path[-1] == goal
    assert (1, 1) not in path #this should avoid obstacle

    print("[OK] obstacle avoidance test passed")


def testnopathExists():
    # test a star returns none when nno path exists
    grid = Grid (size = 5, obstacle_prob = 0, no_fly_zone = 0)

    #block all paths by creating a wall 
    for i in range(5):
        grid.grid[2][1] = 1

    start = (0, 0)
    goal = (4, 4)

    path = a_star_search(grid, start, goal)

    assert path is None
    print("[OK] No path detection test passed")

def testinvalidStartorGoal():
    grid = Grid(size = 5, seedling = 42)

    grid.grid[0][0] = 1

    path = a_star_search(grid, (0, 0), (4, 4))
    assert path is None

    grid.grid[4][4] = 1
    grid.grid[0][0] = 1
    path = a_star_search(grid, (0, 0), (4, 4))
    assert path is None

    print("[OK] invalid positions test passed")



if __name__ =="__main__":
    print("=== Running A* Pathfinding tests ===")
    print("-" * 40)

    testDistance()
    testPathonemptyGrid()
    testpathwithObstacles()
    testnopathExists()
    testinvalidStartorGoal()

    print("\n[OK] All pathfinding tests passed")
    

