# this is going our second step in which we are creating a sort of agent means
#now we have the grid or the map hence we create the drone here
# our drone needs  to know the position, battery and its move

"""
drone classs
models position , battery and the movement
"""

class Drone:

    def __init__(ownself, startposition, batteryCapacity = 100, movingCost = 1):

        ownself.startposition = startposition
        ownself.position = startposition
        ownself.batteryCapacity = batteryCapacity
        ownself.battery = batteryCapacity
        ownself.movingCost = movingCost
        ownself.pathHistory = [startposition]
        ownself.visited = {startposition}

    def move(changepos, nextpos):
        """this will mvoe the drone and give true if move success else false"""

        if changepos.battery < changepos.movingCost:
            return False
        
        changepos.position = nextpos
        changepos.battery -= changepos.movingCost
        changepos.pathHistory.append(nextpos)
        changepos.visited.add(nextpos)

        return True
    
    def canDroneMove (move):
        """this check whether the drone has the battery to move or not"""
        return (move.battery >= move.movingCost)
    
    def gettingBatterylife(getbattery):
        """this give the battery life in percentage"""

        return(getbattery.battery / getbattery.batteryCapacity)*100
    
    def getCoverageCount(coverage):
        """give the number of unique cells visited"""
        return len(coverage.visited)
    
    def gettingPathLength(length):
        # give total path length
        return len(length.pathHistory) -1 #1 coz we dont want to count starting block
    
    def reset(reboot):
        """this will start the game"""

        reboot.position = reboot.startposition
        reboot.battery = reboot.batteryCapacity
        reboot.pathHistory = [reboot.startposition]
        reboot.visited = {reboot.startposition}

    def gettingStatus(status):
        #give the drone status summary

        return{
            'position': status.position,
            'battery': status.battery,
            'battery_percentage': status.gettingBatterylife(),
            'coverage' : status.getCoverageCount(),
            'path_length': status.gettingPathLength()
        }
    

if __name__ == "__main__":
    #we get the demo for the drone movement
    print("===Drone Model demo")
    print("-" *40)

    drone = Drone (startposition = (0, 0), batteryCapacity = 100, movingcost = 1)

    print (f"Start Position: {drone.position}")
    print(f"Battery: {drone.battery}%")

    #simulation of some movements
    moves = [(0, 1), (1, 1), (1, 2), (2, 2)]
    for themove in moves:
        if drone.move(themove):
            print (f"Moved to {themove} - Battery: {drone.gettingBatterylife():.1f}%")

    status = drone.gettingStatus()
    print("\n=== Final Status ===")
    print(f"Position: {status['position']}")
    print(f"Battery : {status['Batterylife']:.1f}%")
    print(f"Coverage: {status['Coverage']}cells")
    print(f"Path Length: {status['PathLength']}steps")