"""
Scalability Test for Drone Path Optimizer
Tests performance on different grid sizes (10x10 to 100x100)
"""

import time
import numpy as np
import csv
from grid import Grid
from drone import Drone
from coverage import CoveragePlanner
from a_star import a_star_search

def test_scalability():
    """Test the system with different grid sizes"""
    
    print("=" * 60)
    print("DRONE PATH OPTIMIZER - SCALABILITY TEST")
    print("=" * 60)
    
    grid_sizes = [10, 20, 30, 50, 75, 100]
    results = []
    
    for size in grid_sizes:
        print(f"\n{'='*60}")
        print(f"Testing Grid Size: {size}x{size}")
        print(f"{'='*60}")
        
        # Create grid and drone
        start_time = time.time()
        grid = Grid(size=size, obstacle_prob=0.15, no_fly_zone=0.05, seedling=42)
        drone = Drone(startposition=(0, 0), battery_capacity=size*size)
        planner = CoveragePlanner(grid, drone)
        
        setup_time = time.time() - start_time
        
        # Test A* pathfinding
        astar_start = time.time()
        path = a_star_search(grid, (0, 0), (size-1, size-1))
        astar_time = time.time() - astar_start
        
        # Test coverage planning
        coverage_start = time.time()
        coverage_path = planner.plan_adaptive_coverage(battery_limit=20)
        coverage_time = time.time() - coverage_start
        
        # Calculate metrics
        stats = grid.statistics()
        coverage_percent = planner.estimate_coverage_percent(coverage_path)
        path_length = len(coverage_path)
        battery_used = path_length
        battery_percent = ((drone.battery_capacity - battery_used) / drone.battery_capacity) * 100
        
        total_time = setup_time + astar_time + coverage_time
        
        # Store results
        result = {
            'size': size,
            'setup_time_ms': setup_time * 1000,
            'astar_time_ms': astar_time * 1000,
            'coverage_time_ms': coverage_time * 1000,
            'total_time_ms': total_time * 1000,
            'coverage_percent': coverage_percent,
            'path_length': path_length,
            'battery_remaining': battery_percent,
            'safe_cells': stats['safe'],
            'obstacle_cells': stats['obstacles']
        }
        results.append(result)
        
        # Print results
        print(f"\n[Results:]")
        print(f"  Setup Time:        {result['setup_time_ms']:.2f}ms")
        print(f"  A* Pathfinding:    {result['astar_time_ms']:.2f}ms")
        print(f"  Coverage Planning: {result['coverage_time_ms']:.2f}ms")
        print(f"  -------------------------------------")
        print(f"  Total Time:        {result['total_time_ms']:.2f}ms")
        print(f"\n[Performance Metrics:]")
        print(f"  Coverage:          {result['coverage_percent']:.1f}%")
        print(f"  Path Length:       {result['path_length']} steps")
        print(f"  Battery Remaining: {result['battery_remaining']:.1f}%")
        print(f"  Safe Cells:        {result['safe_cells']}")
        print(f"  Obstacles:         {result['obstacle_cells']}")
        
    # Summary table
    print(f"\n\n{'='*60}")
    print("SUMMARY TABLE")
    print(f"{'='*60}\n")
    
    print(f"{'Size':<8} | {'Time (ms)':<12} | {'Coverage':<10} | {'Battery':<10} | {'Path Len':<10}")
    print("-" * 60)
    
    for r in results:
        print(f"{r['size']:<8} | {r['total_time_ms']:<12.2f} | {r['coverage_percent']:<10.1f} | {r['battery_remaining']:<10.1f} | {r['path_length']:<10}")
    
    print(f"\n{'='*60}")
    print("[OK] SCALABILITY TEST COMPLETE")
    print(f"{'='*60}")
    
    # Performance analysis
    print(f"\n[PERFORMANCE ANALYSIS:]")
    
    # Check if performance degrades gracefully
    if results[-1]['total_time_ms'] < 5000:  # 5 seconds for largest grid
        print("  [OK] Excellent scalability - handles 100x100 in under 5 seconds")
    elif results[-1]['total_time_ms'] < 10000:
        print("  [OK] Good scalability - handles 100x100 in under 10 seconds")
    else:
        print("  [WARNING] Performance degrades on large grids")
    
    # Check coverage consistency
    avg_coverage = np.mean([r['coverage_percent'] for r in results])
    if avg_coverage > 80:
        print(f"  [OK] High average coverage: {avg_coverage:.1f}%")
    elif avg_coverage > 60:
        print(f"  [OK] Good average coverage: {avg_coverage:.1f}%")
    else:
        print(f"  [WARNING] Low average coverage: {avg_coverage:.1f}%")
    
    # Check battery efficiency
    avg_battery = np.mean([r['battery_remaining'] for r in results])
    if avg_battery > 70:
        print(f"  [OK] Excellent battery efficiency: {avg_battery:.1f}% remaining")
    elif avg_battery > 50:
        print(f"  [OK] Good battery efficiency: {avg_battery:.1f}% remaining")
    else:
        print(f"  [WARNING] Battery efficiency could be improved: {avg_battery:.1f}% remaining")
    
    return results


if __name__ == "__main__":
    results = test_scalability()
    
    # Save results to file
    with open('scalability_results.txt', 'w') as f:
        f.write("DRONE PATH OPTIMIZER - SCALABILITY TEST RESULTS\n")
        f.write("=" * 60 + "\n\n")
        f.write(f"{'Size':<8} | {'Time (ms)':<12} | {'Coverage':<10} | {'Battery':<10} | {'Path Len':<10}\n")
        f.write("-" * 60 + "\n")
        for r in results:
            f.write(f"{r['size']:<8} | {r['total_time_ms']:<12.2f} | {r['coverage_percent']:<10.1f} | {r['battery_remaining']:<10.1f} | {r['path_length']:<10}\n")
    
    # Save results to CSV for PowerPoint
    csv_filename = 'scalability_results.csv'
    with open(csv_filename, 'w', newline='') as csvfile:
        fieldnames = ['Grid Size', 'Time (ms)', 'Coverage (%)', 'Memory (KB)', 'Battery Remaining (%)', 'Path Length']
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        
        writer.writeheader()
        for r in results:
            # Estimate memory usage (very rough approximation)
            memory_kb = (r['size'] * r['size'] * 4) // 1024  # 4 bytes per cell, convert to KB
            
            writer.writerow({
                'Grid Size': f"{r['size']}x{r['size']}",
                'Time (ms)': f"{r['total_time_ms']:.2f}",
                'Coverage (%)': f"{r['coverage_percent']:.1f}",
                'Memory (KB)': memory_kb,
                'Battery Remaining (%)': f"{r['battery_remaining']:.1f}",
                'Path Length': r['path_length']
            })
    
    print("\n[SAVED] Results saved to scalability_results.txt")
    print(f"[SAVED] CSV exported to {csv_filename} (ready for PowerPoint)")
