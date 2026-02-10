#this is the next step we are going to do in this we are going to test suite for the drone module

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))


from drone import Drone

def testDroneCreation():
    #here testing the drone initialization
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

    assert