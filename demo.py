
import matplotlib.pyplot as plt
from matplotlib.animation import FuncAnimation
import numpy as np

from grid import Grid
from drone import Drone
from coverage import CoveragePlanner
from visualize import Dashboard


class LiveDemo:
    """
    This class runs a live animated demonstration of the drone path optimizer
    It shows the drone moving through the grid in real-time
    """
    
    def __init__(self, grid_size=20, battery=200, seed=None):
        """
        Initialize the live demo
        
        Parameters:
            grid_size: Size of the grid (creates grid_size x grid_size grid)
            battery: Battery capacity for the drone
            seed: Random seed for reproducible results
        """
        # Create the grid environment
        self.grid = Grid(
            size=grid_size,
            obstacle_prob=0.12,  # 12% chance of obstacles
            no_fly_zone=0.06,    # 6% chance of no-fly zones (Fix: name is no_fly_zone)
            seedling=seed        # Fix: name is seedling
        )
        
        # Make sure starting position is clear
        # Fix: name is setstartposition
        self.grid.setstartposition((0, 0))
        
        # Create the drone
        # Fix: names are startposition, batteryCapacity
        self.drone = Drone(startposition=(0, 0), batteryCapacity=battery)
        
        # Create the coverage planner
        self.planner = CoveragePlanner(self.grid, self.drone)
        
        # Generate the full coverage path
        # Keep 20 units of battery as reserve
        # Fix: name is plan_adaptiveCoverage
        self.full_path = self.planner.plan_adaptiveCoverage(battery_limit=20)
        
        # Track which step we're on
        self.current_step = 0
        
        # Create the dashboard for visualization
        self.dashboard = Dashboard(self.grid, self.drone)
        
        # Animation control variables
        self.paused = False
        self.speed = 1  # How many steps to execute per frame
    
    def step(self):
        """
        Execute one step of the simulation
        Moves the drone to the next position in the path
        
        Returns:
            True if step was successful, False if path is complete
        """
        # Check if there are more steps to execute
        if self.current_step < len(self.full_path):
            # Get the next position from the path
            next_pos = self.full_path[self.current_step]
            
            # Try to move the drone to this position
            move_successful = self.drone.move(next_pos)
            
            if move_successful:
                # Move was successful, advance to next step
                self.current_step = self.current_step + 1
                return True
        
        # No more steps or move failed
        return False
    
    def animate(self, frame):
        """
        Animation update function called for each frame
        This is called automatically by matplotlib's animation system
        
        Parameters:
            frame: Frame number (provided by FuncAnimation)
        """
        # Only update if not paused
        if not self.paused:
            # Execute multiple steps per frame based on speed setting
            for i in range(self.speed):
                # Try to execute a step
                step_result = self.step()
                
                # If step failed, stop trying more steps
                if not step_result:
                    break
        
        # Update the dashboard to show current state
        self.dashboard.update()
        
        # Check if mission is complete
        if self.current_step >= len(self.full_path):
            # Get final drone status
            # Fix: name is gettingStatus
            status = self.drone.gettingStatus()
            
            # Calculate final coverage percentage
            total_safe = 0
            for i in range(self.grid.size):
                for j in range(self.grid.size):
                    if self.grid.grid[i][j] == 0:
                        total_safe = total_safe + 1
            
            # Fix: key is coverage
            coverage_pct = (status['coverage'] / total_safe) * 100
            
            # Create completion message
            completion_text = f"""
            ✅ MISSION COMPLETE!
            Coverage: {coverage_pct:.1f}% | Battery: {status['battery_percentage']:.1f}%
            Path: {status['path_length']} steps | Cells: {status['coverage']}/{total_safe}
            """
            
            # Display completion message on the grid
            # Fix: axe_grid
            self.dashboard.axe_grid.text(
                self.grid.size / 2,  # X position (center)
                -1.5,  # Y position (above grid)
                completion_text,
                ha='center',  # Horizontal alignment
                color='#00ff88',  # Green color
                fontsize=10,
                fontweight='bold',
                bbox=dict(
                    boxstyle='round',
                    facecolor='#0a0a0a',
                    alpha=0.8
                )
            )
    
    def run(self, interval=50, save_gif=False):
        """
        Run the live animated demo
        
        Parameters:
            interval: Milliseconds between animation frames
            save_gif: Whether to save the animation as a GIF file
        """
        # Print initial statistics
        print("DRONE PATH OPTIMIZER - LIVE DEMO")
        print("=" * 50)
        print(f"Grid Size: {self.grid.size}x{self.grid.size}")
        print(f"Battery Capacity: {self.drone.batteryCapacity}")
        print(f"Planned Path Length: {len(self.full_path)} steps")
        
        # Get and display grid statistics
        # Fix: statistics
        grid_stats = self.grid.statistics()
        print(f"\\nGrid Statistics:")
        # Fix: safe% key (check grid.py)
        print(f"  Safe Cells: {grid_stats['safe']} ({grid_stats['safe%']:.1f}%)")
        print(f"  Obstacles: {grid_stats['obstacles']}")
        print(f"  No-Fly Zones: {grid_stats['no_fly']}")
        
        # Calculate expected coverage
        # Fix: estimatecoveragePercent
        estimated_coverage = self.planner.estimatecoveragePercent(self.full_path)
        print(f"\\nExpected Coverage: {estimated_coverage:.1f}%")
        print("\\nStarting animation...")
        print("-" * 50)
        
        # Set up the dashboard
        # Fix: setupPlot
        self.dashboard.setupPlot()
        
        # Create the animation
        # Calculate total frames (path length + extra frames to show completion)
        total_frames = len(self.full_path) + 10
        
        anim = FuncAnimation(
            self.dashboard.fig,  # Figure to animate
            self.animate,  # Update function
            interval=interval,  # Time between frames in milliseconds
            blit=False,  # Don't use blitting (redraw everything)
            frames=total_frames
        )
        
        # Save as GIF if requested
        if save_gif:
            print("Saving animation as 'drone_demo.gif'...")
            anim.save('drone_demo.gif', writer='pillow', fps=20)
            print("Saved!")
        
        # Show the animation window
        plt.show()


def static_demo():
    """
    Run a quick static demonstration (no animation)
    This is faster for testing purposes
    """
    print("Static Demo (Quick Preview)")
    print("-" * 40)
    
    # Create grid
    # Fix: seedling
    grid = Grid(size=15, obstacle_prob=0.15, seedling=42)
    # Fix: setstartposition
    grid.setstartposition((0, 0))
    
    # Create drone
    # Fix: startposition, batteryCapacity
    drone = Drone(startposition=(0, 0), batteryCapacity=150)
    
    # Plan coverage path
    planner = CoveragePlanner(grid, drone)
    # Fix: plan_adaptiveCoverage
    path = planner.plan_adaptiveCoverage(battery_limit=15)
    
    # Execute path (limit to 100 steps for quick demo)
    max_steps = min(len(path), 100)
    for i in range(max_steps):
        pos = path[i]
        drone.move(pos)
    
    # Show final result
    dashboard = Dashboard(grid, drone)
    # Fix: setupPlot, show
    dashboard.setupPlot()
    dashboard.drawingGrid()
    dashboard.show()


def comparison_demo():
    """
    Compare different coverage strategies to see which performs better
    """
    print("Strategy Comparison Demo")
    print("-" * 40)
    
    # List of strategies to compare
    strategies = ['adaptive', 'greedy']
    results = []
    
    # Test each strategy
    for strategy in strategies:
        # Create fresh components for each test
        # Fix: seedling
        grid = Grid(size=15, obstacle_prob=0.15, seedling=42)
        # Fix: setstartposition
        grid.setstartposition((0, 0))
        # Fix: startposition, batteryCapacity
        drone = Drone(startposition=(0, 0), batteryCapacity=120)
        planner = CoveragePlanner(grid, drone)
        
        # Plan path using selected strategy
        if strategy == 'adaptive':
            # Fix: plan_adaptiveCoverage
            path = planner.plan_adaptiveCoverage(battery_limit=15)
        else:
            # Fix: planGreedyCoverage
            path = planner.planGreedyCoverage(look_ahead=5)
        
        # Execute the path
        for pos in path:
            # Try to move, stop if battery runs out
            move_successful = drone.move(pos)
            if not move_successful:
                break
        
        # Get final statistics
        # Fix: gettingStatus
        status = drone.gettingStatus()
        
        # Calculate coverage percentage
        total_safe = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.grid[i][j] == 0:
                    total_safe = total_safe + 1
        
        # Fix: coverage key
        coverage = (status['coverage'] / total_safe) * 100
        
        # Store results
        # Fix: batteryCapacity
        battery_used = drone.batteryCapacity - status['battery']
        results.append({
            'strategy': strategy,
            'coverage': coverage,
            'battery_used': battery_used,
            'path_length': status['path_length']
        })
        
        # Print results for this strategy
        print(f"\\n{strategy.upper()} Strategy:")
        print(f"  Coverage: {coverage:.1f}%")
        print(f"  Battery Used: {battery_used}")
        print(f"  Path Length: {status['path_length']}")


# This code runs when the file is executed directly
if __name__ == "__main__":
    import sys
    
    # Check if user provided command line arguments
    if len(sys.argv) > 1:
        # Get the mode from command line
        mode = sys.argv[1]
        
        # Run appropriate demo based on mode
        if mode == "static":
            static_demo()
        elif mode == "compare":
            comparison_demo()
        else:
            print(f"Unknown mode: {mode}")
            print("Usage: python demo.py [static|compare]")
    else:
        # Default: Run the full live animated demo
        demo = LiveDemo(grid_size=20, battery=200, seed=42)
        demo.run(interval=50, save_gif=False)
