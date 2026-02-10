

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from drone import Drone

def testDroneCreation():
    
    drone = Drone(startposition = (0, 0), batteryCapacity = 100)
    assert drone.position == (0, 0)
    assert drone.battery == 100
    assert drone.startposition ==(0, 0)
    print("[OK] Drone creation test passed")

def testDroneMovement():
    """testing drone initialization"""
    drone = Drone(startposition = (0, 0), batteryCapacity = 100, move_cost = 1)

    initial_battery = drone.battery
    success = drone.move((0, 1))

    assert success == True
    assert drone.position == (0, 1)
    assert drone.battery == initial_battery -1
    assert len(drone.pathHistory) == 2

    print("[OK] Drone movement test passed")


def testBatteryDepletion():
    
    drone = Drone(startposition = (0, 0), batteryCapacity = 3, move_cost = 1)

    

    assert drone.move((0, 1)) == True
    assert drone.move((0, 2)) == True
    assert drone.move((0, 3)) == True

    
    assert drone.can_move() == False

    print ("[Ok] Battery depletion test passed")


def testVisitedTracking():
    
    drone = Drone(startposition = (0, 0), batteryCapacity = 100)

    drone.move((0, 1))
    drone.move((1, 1))

    assert (0, 0) in drone.visited
    assert(0, 1) in drone.visited
    assert (1, 1) in drone.visited
    assert len(drone.visited) == 3

    print("[OK] Visiteed tracking test passed")


def testDroneReset():
    
    drone = Drone(startposition = (0, 0),  batteryCapacity = 100)

    drone.move((0, 1))
    drone.move((1, 1))

    drone.reset()

    assert drone.position == (0, 0)
    assert drone.battery == 100
    assert len(drone.pathHistory) == 1
    assert len(drone.visited) == 1

    print("[OK] Drone reset test passed")


if __name__ == "__main__":
    print("=== Running Drone Tests ===")
    print("-" * 40)

    testDroneCreation()
    testDroneMovement()
    testBatteryDepletion()
    testVisitedTracking()
    testDroneReset()

    print("\n[OK] All Drone tests passed!")
