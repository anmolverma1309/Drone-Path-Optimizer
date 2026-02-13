
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
        self.smooth_animation = True
        self.visual_pos = (0.0, 0.0)
        self.interpolation_speed = 0.3 # 0.0 to 1.0 (higher = faster)
    
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
        self.visual_pos = self.drone.position # Reset visual pos
    
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
            
            # Check safety margin
            dist_to_home = abs(next_pos[0] - 0) + abs(next_pos[1] - 0)
            if not self.drone.check_safety_margin(dist_to_home) and self.current_step < len(self.full_path) - dist_to_home:
                 # If we are not already going home (roughly), and battery is low
                 pass # Warning handled by check_safety_margin in future?

            # Move the drone
            if self.drone.move(next_pos):
                self.current_step += 1
                return True
            else:
                return False
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
                
                if self.smooth_animation:
                    # Interpolation logic
                    tr, tc = self.drone.position
                    vr, vc = self.visual_pos
                    
                    # Calculate distance to target (logical position)
                    dist = ((tr - vr)**2 + (tc - vc)**2)**0.5
                    
                    if dist < self.interpolation_speed:
                        # Snap to target and take next logic step
                        self.visual_pos = (float(tr), float(tc))
                        self.step()
                        # If step moved us, we'll start interpolating to NEW target next frame
                    else:
                        # Move visual position towards target
                        dx = tr - vr
                        dy = tc - vc
                        length = (dx*dx) + (dy*dy)
                        if length > 0: # Avoid div by zero
                             length = length**0.5
                             dx, dy = dx/length, dy/length
                        
                        self.visual_pos = (vr + dx*self.interpolation_speed, vc + dy*self.interpolation_speed)

                else:
                    # Legacy step-jump logic
                    for i in range(self.speed):
                        step_result = self.step()
                        if not step_result:
                             break
            
                # Update visualization
                self.dashboard.draw_grid(show_path=True, show_drone=True, drone_pos=self.visual_pos)
                self.dashboard.draw_battery()
                self.dashboard.draw_stats()
                # Draw enhanced metrics every frame (uses caching for efficiency)
                self.dashboard.draw_enhanced_metrics()
        
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
    
    
    def handle_obstacle_update(self, pos):
        """Called when an obstacle is added/removed"""
        if not self.is_started or not self.full_path:
            return

        # Check if the new obstacle blocks our future path
        # We only care if it's ahead of us
        future_path = self.full_path[self.current_step:]
        
        if pos in future_path:
            print(f"\n[ALERT] Obstacle placed on path at {pos}! Initiating dynamic replanning...")
            self.trigger_replanning(pos)

    def trigger_replanning(self, blocked_pos):
        """
        Dynamically repair the path when blocked
        Uses A* to find a local detour to a future point on the path
        """
        # Show replanning indicator
        self.dashboard.axe_grid.text(
            self.grid.size / 2, -2.0,
            "⚠️ REPLANNING LIVE...",
            ha='center', color='#ff3333', fontsize=12, fontweight='bold',
            bbox=dict(facecolor='black', edgecolor='red', alpha=0.9),
            zorder=20
        )
        self.dashboard.fig.canvas.draw()
        
        current_pos = self.drone.position
        
        # Find a reentry point on the path after the blockage
        # Look ahead in the path to find a safe point to rejoin
        reentry_index = -1
        
        # Start looking from a bit ahead to avoid just backtracking to the immediate next step if it's blocked
        found_reentry = False
        
        # We need to find the index in full_path that corresponds to the blocked position
        # and look after that
        try:
            blockage_idx = self.full_path.index(blocked_pos, self.current_step)
        except ValueError:
            return # Blocked pos not in path? weird.
            
        # Try to rejoin path after the blockage
        for i in range(blockage_idx + 1, len(self.full_path)):
            candidate_pos = self.full_path[i]
            if self.grid.isvalid(candidate_pos):
                reentry_index = i
                found_reentry = True
                break
        
        if found_reentry:
            target_pos = self.full_path[reentry_index]
            print(f"[REPLAN] Calculating detour: {current_pos} -> {target_pos}")
            
            # importing locally to avoid circular imports if any
            from a_star import a_star_search
            
            # Find path to reentry point
            detour = a_star_search(self.grid, current_pos, target_pos)
            
            if detour:
                print(f"[REPLAN] Detour found! Length: {len(detour)}")
                
                # Construct new full path:
                # [History up to now] + [Detour] + [Rest of original path]
                
                # We need to be careful with overlaps. 
                # Current step is where we are. 
                # full_path[0...current_step-1] is history.
                # full_path[current_step] is where we were going (but we might be there or not).
                
                # Actually, simpler: 
                # 1. Keep history unchanged? No, full_path is the PLANNED path.
                # 2. We are at current_pos.
                # 3. We want new path segments: [Detour moves] + [original path from reentry_index+1:]
                
                # Correct splicing:
                # detour includes start and end. 
                # We want moves AFTER start, up to and including end.
                detour_moves = detour[1:] 
                
                remaining_original = self.full_path[reentry_index+1:]
                
                # New future path
                new_future = detour_moves + remaining_original
                
                # Update full path
                # We keep the past path for metrics distinct from the planned path?
                # The 'step' function uses 'full_path' by index. 
                # If we change full_path, we must reset index or adjust it.
                
                # Easiest way: 
                # Update full_path to be: [path_already_traveled] + [new_future]
                path_traveled = self.full_path[:self.current_step] 
                # Note: path_traveled does not include current_pos if we haven't 'stepped' out of it yet?
                # Actually, step() gets next_pos = full_path[current_step].
                # If we just moved to current_pos, current_step points to the NEXT move.
                # So full_path[:current_step] are the completed moves?
                # Let's verify: 
                # Initial: current_step = 0. Next=path[0].
                # After move: current_step = 1.
                # So path[:current_step] are the nodes we have supposedly visited/processed.
                
                # But wait, drone.position IS the current position.
                # If we use `detour` starting from `drone.position`, then `detour[0]` == `drone.position`.
                # We want the drone to move to `detour[1]`.
                
                self.full_path = path_traveled + new_future
                
                # current_step stays same, pointing to the next move (which is now detour[1] which is at path_traveled length index)
                # Wait: path_traveled length is `current_step`.
                # new full_path length = `current_step` + `len(new_future)`.
                # Next move is `self.full_path[self.current_step]`.
                # This matches `new_future[0]` which is `detour[1]`. Correct.
                
                print("[REPLAN] Path updated successfully.")
            else:
                print("[REPLAN] FAIL: No path to rejoin found.")
        else:
             print("[REPLAN] FAIL: No valid reentry point found (rest of path blocked?).")

    

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

    def trigger_emergency_return(self):
        """Abort mission and return to start"""
        from a_star import a_star_search
        
        current_pos = self.drone.position
        start_pos = (0, 0)
        
        # Plan path home
        return_path = a_star_search(self.grid, current_pos, start_pos)
        
        if return_path:
            # Join from the NEXT step
            # current path index points to next move.
            # return_path[0] is current_pos. return_path[1] is next move.
            
            self.full_path = self.full_path[:self.current_step] + return_path[1:]
            print(f"[SAFETY] Emergency path calculated: {len(return_path)} steps to home.")
            
            # Show visual alert
            self.dashboard.axe_grid.text(
                self.grid.size / 2, -2.5,
                "🚨 EMERGENCY RETURN",
                ha='center', color='red', fontsize=12, fontweight='bold',
                bbox=dict(facecolor='black', edgecolor='red', alpha=0.9),
                zorder=20
            )
        else:
            print("[CRITICAL] Cannot find path home! Drone stranded.")


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
        print("  > Press 'SPACE' to PAUSE/RESUME")
        print("  > Press '+' or '=' to INCREASE SPEED")
        print("  > Press '-' or '_' to DECREASE SPEED")
        print("  > Press 'r' to RESET")
        print("  > Press 'q' to QUIT")
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
                            
                            # Register replanning callback
                            self.dashboard.replanning_callback = self.handle_obstacle_update

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
            
            elif event.key == ' ':  # Space bar
                self.paused = not self.paused
                status = "PAUSED" if self.paused else "RESUMED"
                print(f"\n[{status}] Simulation {status.lower()}.")
                # Visual feedback
                if self.paused:
                    self.dashboard.axe_grid.text(
                        self.grid.size / 2, -1,
                        "⏸ PAUSED",
                        ha='center', color='#ffd700', fontsize=16, fontweight='bold',
                        bbox=dict(facecolor='black', alpha=0.8)
                    )
                self.dashboard.fig.canvas.draw_idle()
            
            elif event.key in ['+', '=']:  # Increase speed
                self.speed = min(self.speed + 1, 10)  # Max speed 10x
                print(f"\n[SPEED] Increased to {self.speed}x")
                self._show_speed_indicator()
            
            elif event.key in ['-', '_']:  # Decrease speed
                self.speed = max(self.speed - 1, 1)  # Min speed 1x
                print(f"\n[SPEED] Decreased to {self.speed}x")
                self._show_speed_indicator()
                
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
        
        # Setup widgets
        self.dashboard.setup_widgets(self.change_scenario)
        
        # Show the window
        plt.show()
        
    def change_scenario(self, label):
        """Handle scenario change from widget"""
        print(f"\n[SCENARIO] Switching to: {label}")
        
        # Stop any current flight
        self.is_started = False
        self.paused = False
        
        # Reset grid with new scenario
        self.grid = Grid(size=self.grid.size, obstacle_prob=0.12, no_fly_zone=0.06, seedling=None)
        # Note: We are creating a NEW grid object to reset configs cleanly
        # But we need to use the `load_scenario` method we added to Grid
        
        # Actually better to just reuse existing grid object if possible, but recreating is safer for clean slate
        # If I recreate grid, I need to reconnect it to dashboard
        self.grid.load_scenario(label)
        
        # Reset drone and planner
        self.drone = Drone(startposition=(0, 0), battery_capacity=self.drone.battery_capacity)
        self.planner = CoveragePlanner(self.grid, self.drone)
        
        # Update dashboard references
        self.dashboard.grid = self.grid
        self.dashboard.drone = self.drone
        
        # Reset state
        self.destination = None
        self.full_path = None
        self.optimal_path = None
        self.current_step = 0
        
        # Reset metrics cache
        self.dashboard.reset_metrics()
        
        # Redraw

        self.dashboard.draw_grid()
        self.dashboard.draw_battery()
        self.dashboard.draw_coverage()
        self.dashboard.draw_stats()
        self.dashboard.draw_enhanced_metrics()
        self.dashboard.fig.canvas.draw_idle()
        print(f"[SCENARIO] Loaded {label}!")

    
    def _show_speed_indicator(self):
        """Display speed indicator on the grid"""
        # Clear any existing speed text and redraw
        self.dashboard.update()
        self.dashboard.axe_grid.text(
            self.grid.size / 2, -1,
            f"Speed: {self.speed}x",
            ha='center', color='#00d4ff', fontsize=14, fontweight='bold',
            bbox=dict(facecolor='black', alpha=0.8)
        )
        self.dashboard.fig.canvas.draw_idle()


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
