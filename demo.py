

import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from grid import Grid
from drone import Drone 
from coverage import CoveragePlanner
from visualize import Dashboard










class LiveDemo:
    

    def __init__ (self, gridSize = 20, battery = 200, seedling = None):
        

       
        self.grid = Grid(size = gridSize, obstacle_prob = 0.12,
                         no_fly_zone = 0.06, seedling = seedling)
        self.grid.setstartposition((0, 0))

        self.drone = Drone(startposition = (0, 0), batteryCapacity = battery)
        self.planner = CoveragePlanner(self.grid, self.drone)

       
        self.full_path = self.planner.plan_adaptiveCoverage(battery_limit = 20)
        self.current_step = 0

      
        self.dashboard = Dashboard(self.grid, self.drone)

      
        self.paused = False
        self.speed = 1 


    def stepping(self):
        

        if self.current_step < len(self.full_path):
            next_pos = self.full_path[self.current_step]
            if self.done.move(next_pos):
                self.current_step += 1
                return True
            return False
        

        def amimator(anime, frame):
            
            if not self.paused:
                
                for _ in range(anime.speed):
                    if not anime.step():
                        break

            #updating the dashboard
            self.dashboard.update()

            #add the completion message
            if anime.current_step >= len(self.full_path):
                status = self.drone.get_status()
                total_safe = np.sum(self.grid.grid == 0)
                coverage_part = (status['coverage'] / total_safe) *100

                completion_text = f"""
                Mission Complete!
                Coverage: {coverage_part:.1f}% | Battery: { status['batter_percent']:.1f}%
                Path: {status['path_length']} steps | Cells: {status['coverage']} / {total_safe}
                """

                anime.dashboard.axe_grid.text(anime.grid.size / 2, -1.5, completion_text,
                                              haa = 'center', color = '#00ff88',
                                               fontsize = 10, fontweight = 'bold',
                                                bbox = dict(boxstyle = 'round', facecolor = '#0a0a0a', alpha = 0.8))
    def execution(exe, interval = 50, save_gif = False):

        """
       we will run the live demo here in this block only
       here the inerval give the animation interval in millisecodns
       where as the save gif give whether to safe as the gif or not 
        """

        #here we are going to print initial stats which will give the configures of the drone for it better optimization
        print ("Drone Path Optimizer - live demo")
        print("=" * 50)
        print(f"Grid Size: {exe.grid.size}x{exe.grid.size}")
        print(f"Battery Capacity: {exe.drone.batteryCapacity}")
        print(f"Planned Path Length: {len(exe.full_path)}steps")

        grid_stats = exe.grid.get_stats()
        print(f"\nGrid Statistics:")
        print(f" Safe Cells: {grid_stats['safe']} ({grid_stats['safe_percent']:.1f}%)")
        print(f" obstacles: {grid_stats['obstacles']}")
        print(f" No-Fly Zones: {grid_stats['no_fly']}")


        estimated_coverage = exe.planner.estimatecoveragePercent(exe.full_path)
        print(f"\nExpected Coverage: {estimated_coverage:.1f}%")
        print("\nStarting animationsss......")

        #setup and running the environment of the animation
        exe.dashboard.setupPlot()

        anim = FuncAnimation(exe.dashboard.fig, exe.animate,
                             interval = interval, blit = False,
                             frames = len(exe.full_path) + 10) #this will provides the extra frames to show completion
        
        if save_gif:
            print("Saving animation as 'drone_demo.gif'...")
            anim.save('drone_demo.gif', writer = 'pillow', fps = 20)

            print("Saved!")

        plt.show()


def static_demo():
    """quick static visulalization for testing the drone here """
    print("static demo.(quick previeww)")
    print("-" * 40)

    #creating the components
    grid = Grid(size = 15, obstacle_prob = 0.015, seedling =42)
    grid.setstartposition((0, 0))
    drone = Drone(startposition = (0, 0), batteryCapacity = 150)

    #plan and execute path
    planner = CoveragePlanner(grid, drone)
    path = planner.plan_adaptiveCoverage(battery_limit = 15)

    #execute path 
    for pos in path [:min(len(path), 100)]: # limit for thje static demo
        drone.movew(pos)


    #showing the dashboard
    dashboard = Dashboard(grid, drone)
    dashboard.show()


def comparison_demo():
    """"it compares different coverage strategies"""
    print("strategy comparison demo")
    print("-" * 40)

    strategies = ['adaptive', 'greedy']
    results = []

    for strategy in  strategies:
        #reset for each strategy
        grid = Grid(size  =15, obstacle_prob= 0.15, seedling = 42)
        grid.setstartposition((0, 0))
        drone = Drone(startposition = (0, 0), batteryCapacity = 120)
        planner = CoveragePlanner(grid, drone)

        #path planning of the drone will execute  here
        if strategy == 'adaptive':
            path = planner.path_adaptiveCoverage(battery_limit = 15)
        else:
            path = planner.planGreedyCoverage( look_ahead = 5)

        # execution of the path 
        for pos in path:
            if not drone.move(pos):
                break


        #getting of with the stats
        status = drone.gettingStatus()
        total_safe = np.sum(grid.grid == 0)
        coverage = (status['covearage'] / total_safe) * 100

        results.append({
            'strategy': strategy,
            'coverage': coverage,
            'battery_used': drone.battery_capacity - status['battery'],
            'path_length': status['path_length']
        })

        print(f"\n{strategy.upper()} strategy:")
        print(f" Coverage: {coverage:.1f}%")
        print(f" battery used:{drone.battery_capacity - status['battery']}")
        print(f"  Path Length: {status['path_length']}")
        


if __name__ == "__main__":
    import sys

    #check command line arguments
    if len(sys.argv) > 1:
        mode = sys.argv[1]

        if mode == "static":
            static_demo()
        elif mode == "compare":
            comparison_demo()
        else:
            print(f"unknown mode: {mode}")
            print("Usage: python demo.py [static| compare]")

    else:
        #default: run live animated demo 
        demo = LiveDemo(gridSize = 20, battery = 200, seedling= 42)
        demo.run(interval = 50, save_gif = False)

        #to save as gif, uncomment:
        #demo.run (interval = 100, savw_gif = True)
        


                





