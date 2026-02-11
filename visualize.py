

import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.animation import FuncAnimation
import numpy as np

class Dashboard:

    colorpalette = {
        'safe': '#1a1a2e', 
        'obstacle': '#e94560',
        'no_fly': '#ff6b35',
        'path': '#00ff88',
        'drone': '#00d4ff',
        'visited': '#0f3460',
        # Fix: visitedd -> visited
        'visitedd': '#0f3460',
        'grid_lines': '#16213e'
    }

    def __init__ (self, grid, drone):


    

        self.grid = grid
        self.drone = drone
        self.fig = None
        self.axes = None
        self.axe_grid = None
        self.axe_battery = None
        self.axe_coverage = None
        self.axe_stats = None

    def setupPlot(self):
        

        self.fig = plt.figure(figsize = (16, 6))

        
        gridzz = self.fig.add_gridspec(2, 3, width_ratios=[2, 1, 1],
                                       height_ratios = [1, 1], hspace = 0.3, wspace = 0.3)
        
         
        self.axe_grid = self.fig.add_subplot(gridzz[:, 0])

    
        self.axe_battery = self.fig.add_subplot(gridzz[0, 1])
        self.axe_coverage = self.fig.add_subplot(gridzz[0, 2])
        self.axe_stats = self.fig.add_subplot(gridzz[1, 1:])

        self.fig.patch.set_facecolor('#0a0a0a')

        return self.fig
    
    def _hex_to_rgb(self, hex_color):
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+2], 16)/255 for i in (0, 2, 4))

    def drawingGrid(self, showPath = True, showDrone = True):
        
        self.axe_grid.clear()

        

        grid_vis = np.zeros((self.grid.size, self.grid .size, 3))

        for thei in range(self.grid.size):
            for thej in range(self.grid.size):
                cell_type = self.grid.grid[thei][thej]


                if (thei, thej) in self.drone.visited:
                    # Fix: visited key name
                    color = self._hex_to_rgb(self.colorpalette['visited'])

                elif cell_type == 0: 
                    color = self._hex_to_rgb(self.colorpalette['safe'])
                
                elif cell_type == 1:
                    # Fix: rbg -> rgb
                    color = self._hex_to_rgb(self.colorpalette['obstacle'])
                elif cell_type == 2:
                    color = self._hex_to_rgb(self.colorpalette ['no_fly'])

                grid_vis[thei][thej] = color

        
        self.axe_grid.imshow(grid_vis, origin = 'upper')

        if showPath and len(self.drone.pathHistory) > 1:
            path_array = np.array(self.drone.pathHistory)
            self.axe_grid.plot(path_array[:, 1], path_array[:, 0],
                               color = self.colorpalette['path'], linewidth =2,
                               alpha = 0.7, marker = 'o', markersize = 3)
            
        if showDrone:
            drone_row, droneCol = self.drone.position
            # Fix: invalid args to Circle? No, (x,y) tuple is 1st arg. (droneCol, drone_row) is correct.
            circle = patches.Circle((droneCol, drone_row), 0.4,
                                    color = self.colorpalette['drone'], zorder = 10)
            
            self.axe_grid.add_patch(circle)
            # Fix: haa/vaa -> ha/va
            self.axe_grid.text(droneCol, drone_row, 'D',
                               ha = 'center', va = 'center', fontsize = 12, fontweight = 'bold', color = 'white', zorder = 11)
        
        self.axe_grid.set_xlim(-0.5, self.grid.size - 0.5)
        self.axe_grid.set_ylim(self.grid.size - 0.5, -0.5)
        self.axe_grid.set_xticks(range(self.grid.size))
        self.axe_grid.set_yticks(range(self.grid.size))
        self.axe_grid.grid(True, color = self.colorpalette['grid_lines'], linewidth = 0.5)

    def update(self):
        # Wrapper for update logic if needed, or just redraw grid
        self.drawingGrid()

    def show(self):
        plt.show()
        self.axe_grid.set_title('Surveillance grid',
                       color = 'white', fontsize = 14, fontweight = 'bold')
        self.axe_grid.set_facecolor('#0a0a0a')
        self.axe_grid.tick_params(colors = 'white')

    def drawingbattery(self):

        self.axe_battery.clear()

        battery_part = self.drone.getbatterypercent()

    
        self.axe_battery.barh([0], [battery_part], height = 0.5, color = self._get_battery_color(battery_part))
        self.axe_battery.barh([0], [100 - battery_part], left = [battery_part], height = 0.5, color = '#1a1a1a')

        self.axe_battery.set_xlim(0, 100)
        self.axe_battery.set.ylim(-0.5, 0.5)
        self.axe_battery.set_title(f'Battery: {battery_part:.1f}%', haa = 'center', vaa = 'center', color = 'white', fontsize = 16, fontweight = 'bold')
        self.axe_battery.axis('off')
        self.axe_battery.set_facecolor('#0a0a0a')

        
        self.axe_battery.text (50, 0, f'{battery_part:.1f}%',
                               haa = 'center', vaa= 'center', color = 'white',
                               fontsize = 16, fontweight = 'bold')
        
    def drawingCoverage(self):
        
        self.axe_coverage.clear()

        total_safe = np.sum(self.grid.grid == 0)
        coverage_part = (self.drone.get_coverage_count() / total_safe) * 100

        
        self.axe_coverage.barh([0], [coverage_part], height = 0.5,
                               color = self.colorpalette['path'])
        self.axe_coverage.barh([0], [100 - coverage_part], left = [coverage_part],
                               height = 0.5, color = '#1a1a1a')
        self.axe_coverage.set_xlim (0, 100)
        self.axe_coverage.set_ylim(-0.5, 0.5)
        self.axe_coverage.set_title(f'coverage: {coverage_part:.1f}%',
                                    color = 'white', fontweight = 'bold')
        self.axe_coverage.axis('off')
        self.axe_coverage.set_facecolor('#0a0a0a')

        
        self.axe_coverage.text(50, 0, f'{coverage_part:.1f}%',
                               haa= 'center', vaa = 'center', color = 'white',
                               fontsize = 16, fontweight = 'bold')
        
    def drawingTheStats(stats):
        
        stats.axe_stats.clear()

        status = stats.drone.get_status()
        grid_stats = stats.grid.get_stats()
        total_safe = grid_stats['safe']
        coverage_part = (stats['coverage'] / total_safe) * 100

        statsText = f"""
        Position: {status['position']}
        Battery: {status['battery_percent']:.1}% ({status['battery']} / {stats.drone.battery_capacity})
        Path Length: {status['path_length ']} moves
        Coverage: {status['coverage']} / {total_safe} cells ({coverage_part:.1f}%)
        """

        stats.axe_stats.text(0.1, 0.5, statsText, color = 'white',
                             fontsize = 11, family = 'monospace', vaa = 'center')
        stats.axe_stats.set_xlim(0, 1)
        stats.axe_stats.set_ylim(0, 1)
        stats.axe_stats.axis('off')
        stats.axe_stats.set_facecolor('#0a0a0a')

    def reset(update):
        
        update.draw_grid()
        update.draw_battery()
        update.draw_coverage()
        update.draw_stats()
        plt.draw()


    
    def showingoff(show):
    
        show.setup_plot()
        show.reset()

    
        plt.show()

    def _hex_to_rgb(self, hex_color):
    
        hex_color = hex_color.lstrip('#')
        return tuple(int(hex_color[i:i+1], 16) / 255 for i in (0, 2, 4))
    
    def _get_battery_color(self, battery_part):
        if battery_part > 60:
            return '#00ff88'
        elif battery_part > 30:
            return '#ffd700'
        else:
            return '#e94560'
        
if __name__ == "__main__":
    from grid import Grid
    from drone import Drone


    print(" === visualization demo is being displayed here")
    print("-" * 40)

     
    grid = Grid(size = 20, obstacle_prob = 0.15, no_fly_zone = 0.05, seedling = 42)

    drone = Drone(startposition = (0, 0), batteryCapacity = 100)


    test_path = [(0, 1), (0, 2), (1, 2), (2, 3), (3, 3)]
    for pos in test_path:
        drone.move(pos)

    

    dashboard = Dashboard(grid, drone)
    dashboard.show()




    



                     

    