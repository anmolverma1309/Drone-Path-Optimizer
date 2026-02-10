# Drone-Path-Optimizer

** Autonomous Surveillance Drone Path Planning System**

## Problem statement
Design an autonomous drone system that:
**Maximizes area coverage** on the grid
**Minimizes battery consumption**
**Avoids obstacles** and no-fly zone
**Finds optimal paths** using A* pathfinding


## Features

###Core Components
--> **Grid Generator** - Procedural obstacle and no-fly zone placement
-->**A* Pathfinding** - Optmial path finding with priority queue
-->**Coverage Planner** - Adaptive & greedy coverage strategies
-->**Live Dashboard** - Real-time metrics and animated visualization
-->**Drone Model** - Battery management and position tracking


### Algorithms

-->**A\* Search**: Distance heuristic for optimal pathfinding
-->**Adaptive Coverage**: Nearest-neighbor with battery awareness
-->**Greedy Coverage**: Look-ahead strategy prioritizing unvisited clusters


## Quick Start

### Prerequisites
```bash pip install numpy matplotlib```


### Run the Demo
```bash
#Live animated demo (RECOMMENDED)
python demo.py

#Quick static preview
python dmeo.py static

#Compare strategies
python dmeo.py compare

##Visualization

The dasboard shows:
--> **Grid Map**: 20x20 surveillance area
   - Green = Path Taken
   - Red = Obstacles
   - Orange = No-fly zone
   - Dark blue = visited cells
   - Cyan = Drone position

- **Battery Gauge**: Reak-time battery percentage
- **Coverage Meter**: % of accessible area covered
- **Stats Panel**: Position, path, length, coverage count

---


## Performance Metrics

Example run on 20x20 grid:
- **Coverage**: 88-92%
- **Battery Usage** : 75-85%
- **Path Efficiency**: ~180 steps for full coverage
- **Algorithm**: o(n log n) time complexity

## Hightlights

### DSA Skills Showcased
- **Priority Queue** (heapq for A*)
- **Graph Search** (A* Pathfinding)
- **Greedy Algorithms**(coverage optimization)
- **Dynamix Programming** (path memoization)

### Key elements
- **Live Animation** with real-time metrics
- **Professional Dashboard** with dark hacker aesthetic
- **90%+ Coverage" vs random ~45%
- **Battery Optimization** prevents mid-mission failure