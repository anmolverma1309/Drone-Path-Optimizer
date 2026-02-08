#this is the step 3 for the drone optimizer
"""
in this the drone learn how to move and we are using A*path findings
this is the core algo which allows the drone to get from a to b intelligently
it uses the grid fn and here are the details about the drone and its configures 
"""

import heapq

class Node:

    def __init__ (path, pos, g = 0, h = 0, parent = None):

        """
        pos tell the position of row and colomn
        g is the cost from start to this point
        h is the heuristic cost to goal
        parent: parent node in path
        """

        path.pos = pos
        path.g = g #Cost from the start 
        path.h = h #heristic to goal
        path.f = g+h #total expend
        path.parent = parent


    def __priority__(prior, other):
        return prior.f < other.f
    

    def __equa__(equal, other):
        return equal.pos == other.pos
    
    def __hash__ (hashoperation):
        return hash(hashoperation.pos)
    
def distance(pos1, pos2):
    """
    calc distance heuristic
    pos 1 and pos 2 are position

    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def a_star_search(grid, start, goal):
    """
    A* pathfinding algorithm

    grid will grid object with isvalid and surroundings 
    start is the starting position
     and finally 
    list will path as list of position or None if no path exists

    """

    #check if the start and goal are valid
    if not grid.isvalid(start) or not grid.isvalid(goal):
        return None
    
    # here we are initialize this
    start_node = Node(start, g = 0, h= distance(start,goal))
    openset = []
    heapq.heappush (openset, start_node)

    # now here this will track the visited nodes and their costs

    visited = set()
    costsofar = {start: 0}

    while openset:
        # get the node with the lowest score
        current = heapq.headppop(openset)

        # here the goal reached 
        if current.pos == goal:
            return reconstruct_path(current)
        
        #skip if this is alreadt visited
        if current.pos in visited:
            continue

        visited.add(current.pos)

        #check surroundings
        for surroundingpos in grid.surroundings(current.pos):
            # this calculate the cost to surrounding
            newcost = current.g + 1 # this give the cost of  1 per move

            #skip if we found a better path to this surroundings
            if surroundingpos in costsofar and newcost >= costsofar[surroundingpos]:
                continue

            # now we will create the surrouding node 
            h = distance(surroundingpos, goal)
            surrounding_node = Node(surroundingpos, g = newcost, h = h , parent = current)

            # add to the open set 
            costsofar[surroundingpos] = newcost
            heapq.heappush(openset, surrounding_node)

    #here this return if no path will found
    return None

def reconstruct_path(node):
    """
    reconstruct path from goal to start
    and here the list will treat as the path as list of positions from start to goal
    """

    path = []
    current = node

    while current is not None:
        path.append(current.pos)
        current = current.parent

    path.reverse()
    return path

def findTheNearestUnvisited(grid, drone, unvisited_cells):
    """find the nearest unvisied call using A*
    grid means grid object
    drone means drone object for current position
    unvisited_cells means the set of unvisited positions
    
    and now will return the nearest position and path or the none, none if no reachable cells"""


    if not unvisited_cells:
        return None, None
    current_position = drone.position
    best_position = None
    best_path = None
    best_distance = float('inf')

    # now we will try to find the paths to nearby unvisited cells 
    #sort by distance for efficiency
    sorted_cells = sorted(unvisited_cells,
                          key = lambda pos: distance (current_position, pos))
    

    # check first 10 closest cells which is also called the optimization
    for target in sorted_cells[:10]:
        path = a_star_search (grid, current_position, target)
        if path and len(path) < best_distance:
            best_distance = len(path)
            best_position = target
            best_path = path

    return best_position, best_path


if __name__ == "__main__":
    #this will give a demo A8 pathfinding

    from grid import Grid
    
    print("=== A* Pathfinding Demo ===")
    print("-" * 40)

    # now this will create the simple grid
    grid = Grid (size = 10, obstacle_prob = 0.2, seedling = 42)
    grid.setstartposition((0, 0))

    #now here we find the path
    start = (0, 0)
    goal = (9, 9)

    print(f"Finding path from {start} to {goal}")
    path = a_star_search(grid, start, goal)

    if path:
        print(f"[Ok] Path found! Length: {len(path)} steps")
        print(f"Path: {' -> '.join(str(p) for p in path[:5])}...")

    else:
        print("[Fail] No path exists!")


    #vosia;ize grid 
    print("\nGrid (X=obstacle, S=start, G=goal, *=path):")
    for i in range (grid.size):
        rowstr = ""
        for j in range(grid.size):
            pos = (i, j)
            if pos == start:
                rowstr += "S "
            elif pos == goal:
                rowstr += "G "
            elif path and pos in path:
                rowstr += "* "
            elif grid.grid[i][j]  == 1:
                rowstr += "X "
            else: 
                rowstr += ". "
        print(rowstr)
