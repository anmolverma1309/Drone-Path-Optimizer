"""
Enhanced Metrics Module for Drone Path Optimizer
Provides advanced analytics including turn counting, baseline comparison, 
safety scoring, and energy breakdown analysis.
"""

import numpy as np
import random


def calculate_turns(path):
    """
    Calculate the number of turns (direction changes) in a path
    
    Parameters:
        path: List of (row, col) tuples representing the path
        
    Returns:
        int: Number of turns in the path
    """
    if len(path) < 3:
        return 0
    
    turns = 0
    for i in range(1, len(path) - 1):
        prev_pos = path[i - 1]
        curr_pos = path[i]
        next_pos = path[i + 1]
        
        # Calculate direction vectors
        dir1 = (curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])
        dir2 = (next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1])
        
        # If directions are different, it's a turn
        if dir1 != dir2:
            turns += 1
    
    return turns


def calculate_random_baseline(grid, start_pos, battery_capacity):
    """
    Generate a random path baseline for comparison
    
    Parameters:
        grid: Grid object
        start_pos: Starting position (row, col)
        battery_capacity: Maximum battery available
        
    Returns:
        dict: Baseline statistics (path_length, coverage, turns)
    """
    from drone import Drone
    
    # Create a temporary drone for simulation
    temp_drone = Drone(start_pos, battery_capacity)
    
    path = [start_pos]
    current_pos = start_pos
    attempts = 0
    max_attempts = battery_capacity
    
    # Random walk until battery runs out or stuck
    while temp_drone.can_move() and attempts < max_attempts:
        # Get valid neighbors
        neighbors = grid.surroundings(current_pos)
        
        if not neighbors:
            break  # Stuck, no valid moves
        
        # Choose random neighbor
        next_pos = random.choice(neighbors)
        
        # Try to move
        if temp_drone.move(next_pos):
            path.append(next_pos)
            current_pos = next_pos
        
        attempts += 1
    
    # Calculate statistics
    turns = calculate_turns(path)
    coverage = len(temp_drone.visited)
    path_length = len(path) - 1  # Exclude starting position
    
    return {
        'path_length': path_length,
        'coverage': coverage,
        'turns': turns,
        'battery_used': battery_capacity - temp_drone.battery
    }


def safety_score(path, grid):
    """
    Calculate safety score (0-100) for a path
    100 = perfectly safe (no collisions, no invalid cells)
    
    Parameters:
        path: List of (row, col) tuples
        grid: Grid object
        
    Returns:
        int: Safety score (0-100)
    """
    if not path:
        return 100
    
    violations = 0
    total_checks = len(path)
    
    for pos in path:
        row, col = pos
        
        # Check bounds
        if row < 0 or row >= grid.size or col < 0 or col >= grid.size:
            violations += 1
            continue
        
        # Check cell type
        cell_type = grid.typeofcall(pos)
        if cell_type == 1 or cell_type == 2:  # Obstacle or no-fly
            violations += 1
    
    # Calculate score
    if total_checks == 0:
        return 100
    
    score = int(((total_checks - violations) / total_checks) * 100)
    return max(0, min(100, score))  # Clamp between 0 and 100


def calculate_safety_buffer_violations(path, grid):
    """
    Count how many times the path comes dangerously close to obstacles
    (within 1 cell of an obstacle without hitting it)
    
    Parameters:
        path: List of (row, col) tuples
        grid: Grid object
        
    Returns:
        int: Number of close calls
    """
    violations = 0
    
    for pos in path:
        row, col = pos
        
        # Check if we're in a safe cell
        if not grid.isvalid(pos):
            continue  # Skip invalid cells (those are actual collisions)
        
        # Check all 8 surrounding cells (diagonal + adjacent)
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if dr == 0 and dc == 0:
                    continue  # Skip current cell
                
                neighbor_row = row + dr
                neighbor_col = col + dc
                
                # Check bounds
                if (neighbor_row < 0 or neighbor_row >= grid.size or 
                    neighbor_col < 0 or neighbor_col >= grid.size):
                    continue
                
                # Check if neighbor is an obstacle
                neighbor_type = grid.grid[neighbor_row][neighbor_col]
                if neighbor_type == 1 or neighbor_type == 2:
                    violations += 1
                    break  # Count only once per position
            else:
                continue
            break
    
    return violations


def energy_breakdown(path):
    """
    Analyze energy consumption breakdown: straight moves vs turns
    
    Parameters:
        path: List of (row, col) tuples
        
    Returns:
        dict: Energy breakdown statistics
    """
    if len(path) < 2:
        return {
            'straight_moves': 0,
            'turn_moves': 0,
            'straight_energy': 0,
            'turn_energy': 0,
            'total_energy': 0,
            'turn_penalty_cost': 0
        }
    
    straight_moves = 0
    turn_moves = 0
    
    # First move is always straight
    straight_moves = 1
    
    # Check each subsequent move
    for i in range(1, len(path) - 1):
        prev_pos = path[i - 1]
        curr_pos = path[i]
        next_pos = path[i + 1]
        
        # Calculate direction vectors
        dir1 = (curr_pos[0] - prev_pos[0], curr_pos[1] - prev_pos[1])
        dir2 = (next_pos[0] - curr_pos[0], next_pos[1] - curr_pos[1])
        
        # If directions are the same, it's a straight move
        if dir1 == dir2:
            straight_moves += 1
        else:
            turn_moves += 1
    
    # Last move
    if len(path) >= 3:
        prev_dir = (path[-1][0] - path[-2][0], path[-1][1] - path[-2][1])
        second_last_dir = (path[-2][0] - path[-3][0], path[-2][1] - path[-3][1])
        if prev_dir == second_last_dir:
            straight_moves += 1
        else:
            turn_moves += 1
    elif len(path) == 2:
        straight_moves += 1
    
    # Energy costs (assuming 1 unit for straight, 3 units for turn with 2x penalty)
    base_cost = 1
    turn_penalty = 2
    
    straight_energy = straight_moves * base_cost
    turn_energy = turn_moves * (base_cost + turn_penalty)
    turn_penalty_cost = turn_moves * turn_penalty
    total_energy = straight_energy + turn_energy
    
    return {
        'straight_moves': straight_moves,
        'turn_moves': turn_moves,
        'straight_energy': straight_energy,
        'turn_energy': turn_energy,
        'total_energy': total_energy,
        'turn_penalty_cost': turn_penalty_cost,
        'efficiency': (straight_moves / (straight_moves + turn_moves) * 100) if (straight_moves + turn_moves) > 0 else 0
    }


def get_comprehensive_metrics(path, grid, drone, existing_baseline=None):
    """
    Get all metrics in one call for dashboard display
    
    Parameters:
        path: The complete path taken/planned
        grid: Grid object
        drone: Drone object (for baseline comparison)
        
    Returns:
        dict: Comprehensive metrics dictionary
    """
    # Calculate all metrics
    turns = calculate_turns(path)
    energy = energy_breakdown(path)
    safety = safety_score(path, grid)
    buffer_violations = calculate_safety_buffer_violations(path, grid)
    
    # Generate random baseline for comparison
    if existing_baseline:
        baseline = existing_baseline
    else:
        baseline = calculate_random_baseline(grid, drone.startposition, drone.battery_capacity)
    
    # Comparison stats
    coverage_improvement = 0
    if baseline['coverage'] > 0:
        coverage_improvement = ((drone.get_coverage_count() - baseline['coverage']) / baseline['coverage']) * 100
    
    turn_reduction = 0
    if baseline['turns'] > 0:
        turn_reduction = ((baseline['turns'] - turns) / baseline['turns']) * 100

    path_length_improvement = 0
    if baseline['path_length'] > 0:
        # For path length, shorter is better (usually), but for coverage, we might want efficiency.
        # Let's define improvement as how much shorter our path is for same/better coverage?
        # Or just raw comparison. Let's do % difference relative to baseline.
        # Negative means we are shorter (good).
        path_length = len(path)
        path_length_improvement = ((path_length - baseline['path_length']) / baseline['path_length']) * 100
    
    return {
        'path_length': len(path),
        'path_length_improvement': path_length_improvement,
        'turns': turns,
        'energy': energy,
        'safety_score': safety,
        'buffer_violations': buffer_violations,
        'baseline': baseline,
        'coverage_improvement': coverage_improvement,
        'turn_reduction': turn_reduction
    }


if __name__ == "__main__":
    # Test the metrics module
    from grid import Grid
    from drone import Drone
    from coverage import CoveragePlanner
    
    print("=== Metrics Module Test ===")
    print("-" * 40)
    
    # Create test environment
    grid = Grid(size=15, obstacle_prob=0.15, seedling=42)
    grid.setstartposition((0, 0))
    drone = Drone(startposition=(0, 0), battery_capacity=150)
    planner = CoveragePlanner(grid, drone)
    
    # Generate path
    path = planner.plan_adaptive_coverage(battery_limit=20)
    
    # Execute path
    for pos in path[:100]:  # Limit for test
        drone.move(pos)
    
    # Get metrics
    metrics = get_comprehensive_metrics(path[:100], grid, drone)
    
    print(f"\nPath Analysis:")
    print(f"  Turns: {metrics['turns']}")
    print(f"  Safety Score: {metrics['safety_score']}/100")
    print(f"  Buffer Violations: {metrics['buffer_violations']}")
    
    print(f"\nEnergy Breakdown:")
    print(f"  Straight Moves: {metrics['energy']['straight_moves']} ({metrics['energy']['straight_energy']} energy)")
    print(f"  Turn Moves: {metrics['energy']['turn_moves']} ({metrics['energy']['turn_energy']} energy)")
    print(f"  Turn Penalty Cost: {metrics['energy']['turn_penalty_cost']} extra units")
    print(f"  Movement Efficiency: {metrics['energy']['efficiency']:.1f}%")
    
    print(f"\nBaseline Comparison:")
    print(f"  Random Coverage: {metrics['baseline']['coverage']} cells")
    print(f"  Our Coverage: {drone.get_coverage_count()} cells")
    print(f"  Improvement: {metrics['coverage_improvement']:+.1f}%")
    print(f"  Random Turns: {metrics['baseline']['turns']}")
    print(f"  Our Turns: {metrics['turns']}")
    print(f"  Turn Reduction: {metrics['turn_reduction']:+.1f}%")
