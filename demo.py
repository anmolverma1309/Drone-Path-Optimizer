
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
    
    def __init__(self, grid_size=20, seed=None, interactive=True):
        """
        Initialize the live demo
        
        Parameters:
            grid_size: Size of the grid (creates grid_size x grid_size grid)
            seed: Random seed for reproducible results
            interactive: If True, enable interactive controls for destination/obstacles
        """
        # Calculate battery to cover entire grid with safety margin
        battery = grid_size * grid_size * 2
        
        # Create the grid environment
        self.grid = Grid(
            size=grid_size,
            obstacle_prob=0.12,  # 12% chance of obstacles
            no_fly_zone=0.06,    # 6% chance of no-fly zones
            seedling=seed
        )
        
        # Make sure starting position is clear
        self.grid.setstartposition((0, 0))
        
        # Create the drone
        self.drone = Drone(startposition=(0, 0), battery_capacity=battery)
        
        # Create the coverage planner
        self.planner = CoveragePlanner(self.grid, self.drone)
        
        # Interactive mode settings
        self.interactive = interactive
        self.destination = None
        self.optimal_path = None
        self.full_path = None
        self.is_started = False
        
        # Track which step we're on
        self.current_step = 0
        
        # Create the dashboard for visualization
        self.dashboard = Dashboard(self.grid, self.drone)
        
        # Animation control variables
        self.paused = False
        self.speed = 1  # How many steps to execute per frame
    
    def generate_path(self):
        """Generate the coverage path based on current settings"""
        # Use dashboard destination as the source of truth
        destination = self.dashboard.destination
        
        # Generate the full coverage path with optional destination
        # Keep 20 units of battery as reserve
        self.full_path = self.planner.plan_adaptive_coverage(
            battery_limit=20, 
            end_point=destination
        )
        
        # If destination is set, calculate optimal path for visualization
        if destination:
            from a_star import a_star_search
            self.optimal_path = a_star_search(self.grid, (0, 0), destination)
            self.dashboard.optimal_path = self.optimal_path
        
        self.current_step = 0
    
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
        # Only update if not paused and simulation is started (for interactive mode)
        if not self.paused and (not self.interactive or self.is_started):
            # Only execute if we have a path
            if self.full_path:
                # Execute multiple steps per frame based on speed setting
                for i in range(self.speed):
                    # Try to execute a step
                    step_result = self.step()
                    
                    # If step failed, stop trying more steps
                    if not step_result:
                        break
        
        # Update the dashboard to show current state
        self.dashboard.update()
        
        # Check if mission is complete (only if we have a path)
        if self.full_path and self.current_step >= len(self.full_path):
            # Get final drone status
            status = self.drone.get_status()
            
            # Calculate final coverage percentage
            total_safe = 0
            for i in range(self.grid.size):
                for j in range(self.grid.size):
                    if self.grid.grid[i][j] == 0:
                        total_safe = total_safe + 1
            
            coverage_pct = (status['coverage'] / total_safe) * 100
            
            # Create completion message
            completion_text = f"""
            ✅ MISSION COMPLETE!
            Coverage: {coverage_pct:.1f}% | Battery: {status['battery_percentage']:.1f}%
            Path: {status['path_length']} steps | Cells: {status['coverage']}/{total_safe}
            """
            
            # Display completion message on the grid
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
        
        # Draw optimal path if available
        if self.is_started and self.dashboard.destination:
            self.dashboard.draw_optimal_path()
    
    
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
        print(f"Battery Capacity: {self.drone.battery_capacity}")
        print(f"Planned Path Length: {len(self.full_path)} steps")
        
        # Get and display grid statistics
        grid_stats = self.grid.statistics()
        print(f"\nGrid Statistics:")
        print(f"  Safe Cells: {grid_stats['safe']} ({grid_stats['safe%']:.1f}%)")
        print(f"  Obstacles: {grid_stats['obstacles']}")
        print(f"  No-Fly Zones: {grid_stats['no_fly']}")
        
        # Calculate expected coverage
        estimated_coverage = self.planner.estimate_coverage_percent(self.full_path)
        print(f"\nExpected Coverage: {estimated_coverage:.1f}%")
        print("\nStarting animation...")
        print("-" * 50)
        
        # Set up the dashboard
        self.dashboard.setup_plot()
        
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
    
    def run_interactive(self, interval=50):
        """
        Run the demo in interactive mode with user controls
        """
        print("DRONE PATH OPTIMIZER - INTERACTIVE MODE")
        print("=" * 50)
        print(f"Grid Size: {self.grid.size}x{self.grid.size}")
        print(f"Battery Capacity: {self.drone.battery_capacity}")
        
        # Get grid statistics
        grid_stats = self.grid.statistics()
        print(f"\nGrid Statistics:")
        print(f"  Safe Cells: {grid_stats['safe']} ({grid_stats['safe%']:.1f}%)")
        print(f"  Obstacles: {grid_stats['obstacles']}")
        print(f"  No-Fly Zones: {grid_stats['no_fly']}")
        
        print("\n" + "=" * 50)
        print("INSTRUCTIONS:")
        print("  > Click on grid to set DESTINATION")
        print("  > Hover over cell + Press 'o' to TOGGLE OBSTACLE")
        print("  > Press 's' to START simulation")
        print("  > Press 'r' to RESET")
        print("=" * 50 + "\n")
        
        # Set up the dashboard
        self.dashboard.setup_plot()
        
        # Draw the initial grid so user can see and interact with it
        self.dashboard.draw_grid()
        
        # Add key handler for start
        # Add key handler for start
        def on_key_start(event):
            if event.key == 's':
                if not self.is_started:
                    if self.dashboard.destination:
                        print(f"\n[STARTED] Simulation starting... Target: {self.dashboard.destination}")
                        self.generate_path()
                        if self.full_path:
                            self.is_started = True
                            print(f"[INFO] Path found: {len(self.full_path)} steps")
                            
                            # Calculate expected coverage
                            estimated_coverage = self.planner.estimate_coverage_percent(self.full_path)
                            print(f"[INFO] Expected Coverage: {estimated_coverage:.1f}%")
                        else:
                            print("[ERROR] Could not generate a valid path!")
                    else:
                        print("\n[!] Please click on the grid to set a DESTINATION first.")
                        # Visual feedback on graph
                        self.dashboard.axe_grid.text(
                            self.grid.size / 2, self.grid.size / 2, 
                            "CLICK TO SET DESTINATION", 
                            color='red', fontsize=14, fontweight='bold', ha='center',
                            bbox=dict(facecolor='black', alpha=0.7)
                        )
                        self.dashboard.fig.canvas.draw_idle()
                else:
                    print("\n[INFO] Simulation is already running.")

            elif event.key == 'r':
                print("\n[RESET] Simulation reset.")
                self.is_started = False
                self.current_step = 0
                self.drone.reset()
                self.dashboard.destination = None  # Clear destination
                self.dashboard.draw_grid()
                print("[INFO] Destination cleared.")
                self.dashboard.fig.canvas.draw_idle()
                
            elif event.key == 'q':
                print("\n[QUIT] Exiting...")
                plt.close(self.dashboard.fig)
        
        # Connect the start handler
        self.dashboard.fig.canvas.mpl_connect('key_press_event', on_key_start)
        
        # Create the animation
        total_frames = 10000  # Large number so it runs until completion
        
        anim = FuncAnimation(
            self.dashboard.fig,
            self.animate,
            interval=interval,
            blit=False,
            frames=total_frames
        )
        
        # Show the window
        plt.show()


def static_demo():
    """
    Run a quick static demonstration (no animation)
    This is faster for testing purposes
    """
    print("Static Demo (Quick Preview)")
    print("-" * 40)
    
    # Create grid
    grid = Grid(size=15, obstacle_prob=0.15, seedling=42)
    grid.setstartposition((0, 0))
    
    # Create drone
    drone = Drone(startposition=(0, 0), battery_capacity=150)
    
    # Plan coverage path
    planner = CoveragePlanner(grid, drone)
    path = planner.plan_adaptive_coverage(battery_limit=15)
    
    # Execute path (limit to 100 steps for quick demo)
    max_steps = min(len(path), 100)
    for i in range(max_steps):
        pos = path[i]
        drone.move(pos)
    
    # Show final result
    dashboard = Dashboard(grid, drone)
    dashboard.setup_plot()
    dashboard.draw_grid()
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
        grid = Grid(size=15, obstacle_prob=0.15, seedling=42)
        grid.setstartposition((0, 0))
        drone = Drone(startposition=(0, 0), battery_capacity=120)
        planner = CoveragePlanner(grid, drone)
        
        # Plan path using selected strategy
        if strategy == 'adaptive':
            path = planner.plan_adaptive_coverage(battery_limit=15)
        else:
            path = planner.plan_greedy_coverage(look_ahead=5)
        
        # Execute the path
        for pos in path:
            # Try to move, stop if battery runs out
            move_successful = drone.move(pos)
            if not move_successful:
                break
        
        # Get final statistics
        status = drone.get_status()
        
        # Calculate coverage percentage
        total_safe = 0
        for i in range(grid.size):
            for j in range(grid.size):
                if grid.grid[i][j] == 0:
                    total_safe = total_safe + 1
        
        coverage = (status['coverage'] / total_safe) * 100
        
        # Store results
        battery_used = drone.battery_capacity - status['battery']
        results.append({
            'strategy': strategy,
            'coverage': coverage,
            'battery_used': battery_used,
            'path_length': status['path_length']
        })
        
        # Print results for this strategy
        print(f"\n{strategy.upper()} Strategy:")
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
        # Default: Run interactive mode
        demo = LiveDemo(grid_size=20, seed=42, interactive=True)
        demo.run_interactive(interval=50)
