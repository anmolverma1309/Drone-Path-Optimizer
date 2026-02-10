

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
        

        if changepos.battery < changepos.movingCost:
            return False
        
        changepos.position = nextpos
        changepos.battery -= changepos.movingCost
        changepos.pathHistory.append(nextpos)
        changepos.visited.add(nextpos)

        return True
    
    def canDroneMove (move):
        
        return (move.battery >= move.movingCost)
    
    def gettingBatterylife(getbattery):
        

        return(getbattery.battery / getbattery.batteryCapacity)*100
    
    def getCoverageCount(coverage):
        
        return len(coverage.visited)
    
    def gettingPathLength(length):
        
        return len(length.pathHistory) -1 #
    
    def reset(reboot):
        

        reboot.position = reboot.startposition
        reboot.battery = reboot.batteryCapacity
        reboot.pathHistory = [reboot.startposition]
        reboot.visited = {reboot.startposition}

    def gettingStatus(status):
        

        return{
            'position': status.position,
            'battery': status.battery,
            'battery_percentage': status.gettingBatterylife(),
            'coverage' : status.getCoverageCount(),
            'path_length': status.gettingPathLength()
        }
    

if __name__ == "__main__":
    
    print("===Drone Model demo")
    print("-" *40)

    drone = Drone (startposition = (0, 0), batteryCapacity = 100, movingcost = 1)

    print (f"Start Position: {drone.position}")
    print(f"Battery: {drone.battery}%")

    
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