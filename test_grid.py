"""test suite
for the drone path optimizer
run with or without python"""

import sys
import os
 # add parent directory to the path 

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '...')))


from grid import Grid

def testgridcreation():
    """test basic grid creation"""

    grid = Grid(size = 10, seedling = 42)
    assert grid.size == 10
    assert grid.grid.shape == (10, 10)
    print("[OK] grid creation test passed")

def testgridcelltypes():
    """test grid contains correct cell types"""

    grid = Grid(size = 10, seed = 42)
    unique_values = set(grid.grid.flatten())

    #should only contain 0 safe , 1 is the obstacle and 2 is the no fly zone
    assert unique_values.issubset({0, 1, 2})
    print("[OK] Grid cell types test passsed")


def testisvalid():
    """"test the positional validation"""
    grid = Grid(size = 10, seedling = 42)

    #test the valid position
    grid.grid[5][5] = 0
    assert grid.isvalid((5, 5)) == True

    #test obstacle
    grid.grid[3][3] = 1
    assert grid.isvalid((3, 3)) == False

    #this will test the no fly zone
    grid.grid[2][2] = 2
    assert grid.isvalid ((2, 2)) == False

    #this will test whether the test are out of bounds or not
    assert grid.isvalid((-1, 0)) == False
    assert grid.isvalid((0, -1)) == False
    assert grid.isvalid((10, 0)) == False
    assert grid.isvalid((0, 10)) == False

    print ("[OK] Position Validation test passed successfully ")

def testgetsurroundings():
    # test surrounding geneation

    grid = Grid(size = 5, seedling = 42)

    #makea clear area for testing
    for i in range(5):
        for j in range(5):
            grid.grid[i][j] = 0

        surroundings = grid.get_surroundings((2, 2))
        assert len(surroundings) <= 4

        #corner cell 
        surroundings = grid.get_surroundings((0, 0))
        assert len(surroundings) <= 2

        print("[OK] Get surroundings test passed")

def testgridstats():
    """TEST GRID  statistics caluculation"""
    grid = Grid(size = 10, obstacle_problem = 0.2, no_fly_zone = 0.1, seedling = 42)
    stats = grid.get_stats()

    assert 'total' in stats
    assert 'safe' in stats
    assert 'obstacles' in stats 
    assert 'no_fly' in stats
    assert stats['total'] == 100
    assert stats['safe'] + stats ['obstacles'] + stats['no_fly'] == stats['total']

    print("[OK] Grid stats test passed")

if __name__ == "__main__":
    print("=== Running Grid Tests ===")
    print ("-" * 40)

    testgridcreation()
    testgridcelltypes()
    testisvalid()
    testgetsurroundings()
    testgridstats()

    print("\n[OK] All grid tests passed!")

