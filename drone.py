
class Drone:

    def __init__(self, startposition, battery_capacity=100, moving_cost=1):
        self.startposition = startposition
        self.position = startposition
        self.battery_capacity = battery_capacity
        self.battery = battery_capacity
        self.moving_cost = moving_cost
        self.path_history = [startposition]
        self.visited = {startposition}

    def move(self, nextpos):
        if self.battery < self.moving_cost:
            return False
        
        self.position = nextpos
        self.battery -= self.moving_cost
        self.path_history.append(nextpos)
        self.visited.add(nextpos)

        return True
    
    def can_move(self):
        return self.battery >= self.moving_cost
    
    def get_battery_percentage(self):
        return (self.battery / self.battery_capacity) * 100
    
    def get_coverage_count(self):
        return len(self.visited)
    
    def get_path_length(self):
        return len(self.path_history) - 1
    
    def reset(self):
        self.position = self.startposition
        self.battery = self.battery_capacity
        self.path_history = [self.startposition]
        self.visited = {self.startposition}

    def get_status(self):
        return {
            'position': self.position,
            'battery': self.battery,
            'battery_percentage': self.get_battery_percentage(),
            'coverage': self.get_coverage_count(),
            'path_length': self.get_path_length()
        }
    

if __name__ == "__main__":
    
    print("===Drone Model demo")
    print("-" * 40)

    drone = Drone(startposition=(0, 0), battery_capacity=100, moving_cost=1)

    print(f"Start Position: {drone.position}")
    print(f"Battery: {drone.battery}%")

    moves = [(0, 1), (1, 1), (1, 2), (2, 2)]
    for themove in moves:
        if drone.move(themove):
            print(f"Moved to {themove} - Battery: {drone.get_battery_percentage():.1f}%")

    status = drone.get_status()
    print("\n=== Final Status ===")
    print(f"Position: {status['position']}")
    print(f"Battery : {status['battery_percentage']:.1f}%")
    print(f"Coverage: {status['coverage']} cells")
    print(f"Path Length: {status['path_length']} steps")