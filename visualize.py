

import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class Dashboard:

    colorpalette = {
        'safe': '#1a1a2e', 
        'obstacle': '#e94560',
        'no_fly': '#ff6b35',
        'path': '#00ff88',
        'drone': '#00d4ff',
        'visited': '#0f3460',
        'visitedd': '#0f3460', # Kept for safety if used anywhere else
        'grid_lines': '#16213e',
        'optimal_path': '#0080ff',
        'destination': '#ffff00'
    }

    def __init__(self, grid, drone):
        self.grid = grid
        self.drone = drone
        self.fig = None
        self.axes = None
        self.axe_grid = None
        self.axe_battery = None
        self.axe_coverage = None
        self.axe_stats = None
        self.optimal_path = None
        self.destination = None
        self.hover_pos = None

    def setup_plot(self):
        self.fig = plt.figure(figsize=(16, 6))
        
        gridzz = self.fig.add_gridspec(2, 3, width_ratios=[2, 1, 1],
                                       height_ratios=[1, 1], hspace=0.3, wspace=0.3)
        
        self.axe_grid = self.fig.add_subplot(gridzz[:, 0])
        self.axe_battery = self.fig.add_subplot(gridzz[0, 1])
        self.axe_coverage = self.fig.add_subplot(gridzz[0, 2])
        self.axe_stats = self.fig.add_subplot(gridzz[1, 1:])

        self.fig.patch.set_facecolor('#0a0a0a')
        
        # Remove 's' from save keymap to prevent conflict
        if 's' in plt.rcParams['keymap.save']:
            plt.rcParams['keymap.save'].remove('s')

        # Connect event handlers for interactivity
        self.fig.canvas.mpl_connect('button_press_event', self.on_click)
        self.fig.canvas.mpl_connect('key_press_event', self.on_key)
        self.fig.canvas.mpl_connect('motion_notify_event', self.on_hover)

        return self.fig
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

    def draw_grid(self, show_path=True, show_drone=True):
        self.axe_grid.clear()

        grid_vis = np.zeros((self.grid.size, self.grid.size, 3))

        for thei in range(self.grid.size):
            for thej in range(self.grid.size):
                cell_type = self.grid.grid[thei][thej]

                if (thei, thej) in self.drone.visited:
                    color = self._hex_to_rgb(self.colorpalette['visited'])
                elif cell_type == 0: 
                    color = self._hex_to_rgb(self.colorpalette['safe'])
                elif cell_type == 1:
                    color = self._hex_to_rgb(self.colorpalette['obstacle'])
                elif cell_type == 2:
                    color = self._hex_to_rgb(self.colorpalette['no_fly'])
                else:
                    color = (0, 0, 0) # Fallback

                grid_vis[thei][thej] = color
        
        self.axe_grid.imshow(grid_vis, origin='upper')

        if show_path and len(self.drone.path_history) > 1:
            path_array = np.array(self.drone.path_history)
            self.axe_grid.plot(path_array[:, 1], path_array[:, 0],
                               color=self.colorpalette['path'], linewidth=2,
                               alpha=0.7, marker='o', markersize=3)
            
        if show_drone:
            drone_row, drone_col = self.drone.position
            # Fix: Circle takes (x,y) -> (col, row)
            circle = patches.Circle((drone_col, drone_row), 0.4,
                                    color=self.colorpalette['drone'], zorder=10)
            
            self.axe_grid.add_patch(circle)
            self.axe_grid.text(drone_col, drone_row, 'D',
                               ha='center', va='center', fontsize=12, fontweight='bold', color='white', zorder=11)
        
        self.axe_grid.set_xlim(-0.5, self.grid.size - 0.5)
        self.axe_grid.set_ylim(self.grid.size - 0.5, -0.5)
        self.axe_grid.set_xticks(range(self.grid.size))
        self.axe_grid.set_yticks(range(self.grid.size))
        self.axe_grid.grid(True, color=self.colorpalette['grid_lines'], linewidth=0.5)

    def update(self):
        self.draw_grid()
        self.draw_destination()  # Ensure destination is redrawn
        self.draw_optimal_path() # Ensure optimal path is redrawn
        self.draw_battery()
        self.draw_coverage()
        self.draw_stats()

    def show(self):
        self.axe_grid.set_title('Surveillance grid',
                       color='white', fontsize=14, fontweight='bold')
        self.axe_grid.set_facecolor('#0a0a0a')
        self.axe_grid.tick_params(colors='white')
        plt.show()

    def draw_battery(self):
        self.axe_battery.clear()

        battery_part = self.drone.get_battery_percentage()
    
        self.axe_battery.barh([0], [battery_part], height=0.5, color=self._get_battery_color(battery_part))
        self.axe_battery.barh([0], [100 - battery_part], left=[battery_part], height=0.5, color='#1a1a1a')

        self.axe_battery.set_xlim(0, 100)
        self.axe_battery.set_ylim(-0.5, 0.5)
        self.axe_battery.set_title(f'Battery: {battery_part:.1f}%', ha='center', va='center', color='white', fontsize=16, fontweight='bold')
        self.axe_battery.axis('off')
        self.axe_battery.set_facecolor('#0a0a0a')
        
        self.axe_battery.text(50, 0, f'{battery_part:.1f}%',
                               ha='center', va='center', color='white',
                               fontsize=16, fontweight='bold')
        
    def draw_coverage(self):
        self.axe_coverage.clear()

        total_safe = int(np.sum(self.grid.grid == 0))
        if total_safe == 0:
            coverage_part = 0
        else:
            coverage_part = (self.drone.get_coverage_count() / total_safe) * 100
        
        self.axe_coverage.barh([0], [coverage_part], height=0.5,
                               color=self.colorpalette['path'])
        self.axe_coverage.barh([0], [100 - coverage_part], left=[coverage_part],
                               height=0.5, color='#1a1a1a')
        self.axe_coverage.set_xlim(0, 100)
        self.axe_coverage.set_ylim(-0.5, 0.5)
        self.axe_coverage.set_title(f'coverage: {coverage_part:.1f}%',
                                    color='white', fontweight='bold')
        self.axe_coverage.axis('off')
        self.axe_coverage.set_facecolor('#0a0a0a')
        
        self.axe_coverage.text(50, 0, f'{coverage_part:.1f}%',
                               ha='center', va='center', color='white',
                               fontsize=16, fontweight='bold')
        
    def draw_stats(self):
        self.axe_stats.clear()

        status = self.drone.get_status()
        grid_stats = self.grid.statistics()
        total_safe = grid_stats['safe']
        
        if total_safe == 0:
             coverage_part = 0
        else:
             coverage_part = (status['coverage'] / total_safe) * 100

        statsText = f"""
        Position: {status['position']}
        Battery: {status['battery_percentage']:.1f}% ({status['battery']} / {self.drone.battery_capacity})
        Path Length: {status['path_length']} moves
        Coverage: {status['coverage']} / {total_safe} cells ({coverage_part:.1f}%)
        """

        self.axe_stats.text(0.1, 0.5, statsText, color='white',
                             fontsize=11, family='monospace', va='center')
        self.axe_stats.set_xlim(0, 1)
        self.axe_stats.set_ylim(0, 1)
        self.axe_stats.axis('off')
        self.axe_stats.set_facecolor('#0a0a0a')

    def _get_battery_color(self, battery_part):
        if battery_part > 60:
            return '#00ff88'
        elif battery_part > 30:
            return '#ffd700'
        else:
            return '#e94560'
    
    def draw_optimal_path(self):
        """Draw the optimal path from start to destination in blue"""
        if self.optimal_path and len(self.optimal_path) > 1:
            path_array = np.array(self.optimal_path)
            self.axe_grid.plot(path_array[:, 1], path_array[:, 0],
                               color=self.colorpalette['optimal_path'], 
                               linewidth=3, alpha=0.8, 
                               linestyle='--', label='Optimal Path')
    
    def draw_destination(self):
        """Draw the destination marker"""
        if self.destination:
            dest_row, dest_col = self.destination
            self.axe_grid.scatter([dest_col], [dest_row], 
                                  color=self.colorpalette['destination'],
                                  s=200, marker='*', zorder=12, 
                                  edgecolors='white', linewidths=2)
            self.axe_grid.text(dest_col, dest_row - 0.7, 'DEST',
                               ha='center', va='center', fontsize=8,
                               fontweight='bold', color='white', zorder=13)
    
    def on_click(self, event):
        """Handle mouse clicks to set destination"""
        if event.inaxes == self.axe_grid and event.button == 1:  # Left click
            col = int(round(event.xdata))
            row = int(round(event.ydata))
            
            # Check if click is within grid bounds
            if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
                # Check if cell is valid
                if self.grid.isvalid((row, col)):
                    self.destination = (row, col)
                    print(f"Destination set to: ({row}, {col})")
                    self.draw_grid()
                    self.draw_destination()
                    self.fig.canvas.draw_idle()
                else:
                    print(f"Cannot set destination on obstacle/no-fly zone at ({row}, {col})")
    
    def on_key(self, event):
        """Handle keyboard input to toggle obstacles"""
        if event.key == 'o' and self.hover_pos:
            row, col = self.hover_pos
            if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
                # Don't allow toggling start position
                if (row, col) != (0, 0):
                    self.grid.toggle_obstacle((row, col))
                    print(f"Toggled obstacle at ({row}, {col})")
                    self.draw_grid()
                    if self.destination:
                        self.draw_destination()
                    self.fig.canvas.draw_idle()
    
    def on_hover(self, event):
        """Track hover position for keyboard controls"""
        if event.inaxes == self.axe_grid:
            col = int(round(event.xdata))
            row = int(round(event.ydata))
            if 0 <= row < self.grid.size and 0 <= col < self.grid.size:
                self.hover_pos = (row, col)
        
if __name__ == "__main__":
    from grid import Grid
    from drone import Drone

    print(" === visualization demo is being displayed here")
    print("-" * 40)
     
    grid = Grid(size=20, obstacle_prob=0.15, no_fly_zone=0.05, seedling=42)

    drone = Drone(startposition=(0, 0), battery_capacity=100)

    test_path = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 3)]
    for pos in test_path:
        drone.move(pos)

    dashboard = Dashboard(grid, drone)
    dashboard.setup_plot()
    dashboard.draw_grid()
    dashboard.show()