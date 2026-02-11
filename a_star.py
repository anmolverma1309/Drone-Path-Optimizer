# path = pathing
import heapq

class Node:

    def __init__ (pathing, posture, goals = 0, h = 0, parentzz = None):


        pathing.posture = posture
        pathing.goals = goals
        pathing.h = h 
        pathing.f = goals+h 
        pathing.parent = parentzz


    def __lt__(prior, other):
        return prior.f < other.f
    

    def __eq__(equal, other):
        return equal.posture == other.posture
    
    def __hash__ (hashoperation):
        return hash(hashoperation.posture)
    
def distance(posture1, posture2):
    
    return abs(posture1[0] - posture2[0]) + abs(posture1[1] - posture2[1])


def a_star_search(grid, start, goal):

    
    if not grid.isvalid(start) or not grid.isvalid(goal):
        return None
    
   
    start_node = Node(start, goals = 0, h= distance(start,goal))
    openset = []
    heapq.heappush (openset, start_node)

    
    visited = set()
    costsofar = {start: 0}

    while openset:
        current = heapq.heappop(openset)

        if current.posture == goal:
            return reconstruct_path(current)
        
        
        if current.posture in visited:
            continue

        visited.add(current.posture)

        
        for surroundingposture in grid.surroundings(current.posture):
            newcost = current.goals + 1 

            if surroundingposture in costsofar and newcost >= costsofar[surroundingposture]:
                continue

            h = distance(surroundingposture, goal)
            surrounding_node = Node(surroundingposture, goals = newcost, h = h , parentzz = current)

            costsofar[surroundingposture] = newcost
            heapq.heappush(openset, surrounding_node)

    
    return None

def reconstruct_path(node):
    

    path = []
    current = node

    while current is not None:
        path.append(current.posture)
        current = current.parent

    path.reverse()
    return path

def findTheNearestUnvisited(grid, drone, unvisited_cells):
    


    if not unvisited_cells:
        return None, None
    current_position = drone.position
    best_position = None
    best_path = None
    best_distance = float('inf')

    sorted_cells = sorted(unvisited_cells,
                          key = lambda posture: distance (current_position, posture))
    

    for target in sorted_cells[:10]:
        path = a_star_search (grid, current_position, target)
        if path and len(path) < best_distance:
            best_distance = len(path)
            best_position = target
            best_path = path

    return best_position, best_path


if __name__ == "__main__":

    from grid import Grid
    
    print("=== A* Pathfinding Demo ===")
    print("-" * 40)

    grid = Grid (size = 10, obstacle_prob = 0.2, seedling = 42)
    grid.setstartposition((0, 0))

    start = (0, 0)
    goal = (9, 9)

    print(f"Finding path from {start} to {goal}")
    path = a_star_search(grid, start, goal)

    if path:
        print(f"[Ok] Path found! Length: {len(path)} steps")
        print(f"Path: {' -> '.join(str(p) for p in path[:5])}...")

    else:
        print("[Fail] No path exists!")


    print("\nGrid (X=obstacle, S=start, Goals=goal, *=path):")
    for i in range (grid.size):
        rowstr = ""
        for j in range(grid.size):
            posture = (i, j)
            if posture == start:
                rowstr += "S "
            elif posture == goal:
                rowstr += "Goals "
            elif path and posture in path:
                rowstr += "* "
            elif grid.grid[i][j]  == 1:
                rowstr += "X "
            else: 
                rowstr += ". "
        print(rowstr)
