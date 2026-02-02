#!/usr/bin/env python3
"""

Analyzes baseline measurements with and without traffic control
"""

import json
import glob
import os
import numpy as np
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt

print("=" * 60)
print("INITIAL RESULTS ANALYSIS")
print("=" * 60)

def load_throughput_data(file_pattern):
    """Load throughput data from iperf3 JSON files"""
    throughputs = []
    files_processed = 0
    
    for file_path in glob.glob(file_pattern):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
                
                # Extract throughput from sender statistics
                if 'end' in data and 'sum_sent' in data['end']:
                    bps = data['end']['sum_sent'].get('bits_per_second', 0)
                    if bps > 0:
                        throughput_mbps = bps / 1_000_000  # Convert to Mbps
                        throughputs.append(throughput_mbps)
                        files_processed += 1
                else:
                    print(f"  Warning: No sum_sent data in {os.path.basename(file_path)}")
                    
        except json.JSONDecodeError as e:
            print(f"  Error: Could not parse JSON in {os.path.basename(file_path)}: {e}")
        except Exception as e:
            print(f"  Error reading {os.path.basename(file_path)}: {e}")
    
    return throughputs, files_processed

def analyze_latency_from_ping():
    """Get actual latency from ping test"""
    print("\n" + "=" * 40)
    print("LATENCY MEASUREMENT")
    print("=" * 40)
    print("To get actual latency, run:")
    print("  docker exec tsn-sender ping -c 20 10.10.10.3")
    print("\nExpected results:")
    print("  • Average latency: 0.1-0.3 ms")
    print("  • Maximum latency: < 1.0 ms")
    print("  • Packet loss: 0%")
    return []

def create_throughput_plot(best_effort, mixed_priority, results_dir):
    """Create visualization of throughput comparison"""
    if not best_effort or not mixed_priority:
        print("  Not enough data for visualization")
        return
    
    plt.figure(figsize=(12, 5))
    
    # Plot 1: Box plot comparison
    plt.subplot(1, 2, 1)
    box_data = [best_effort, mixed_priority]
    box_labels = ['No Traffic Control', 'With Traffic Control']
    
    bp = plt.boxplot(box_data, labels=box_labels, patch_artist=True)
    
    # Customize box colors
    colors = ['lightblue', 'lightgreen']
    for patch, color in zip(bp['boxes'], colors):
        patch.set_facecolor(color)
    
    plt.title('Throughput Comparison: With vs Without Traffic Control')
    plt.ylabel('Throughput (Mbps)')
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Add value labels
    for i, data in enumerate(box_data, 1):
        mean_val = np.mean(data)
        plt.text(i, mean_val + max(data)*0.05, f'{mean_val:.1f}', 
                ha='center', va='bottom', fontweight='bold')
    
    # Plot 2: Individual test results
    plt.subplot(1, 2, 2)
    
    # Plot best-effort tests
    x_best = range(1, len(best_effort) + 1)
    plt.scatter(x_best, best_effort, label='No TC', color='blue', 
                alpha=0.6, s=100, edgecolors='black')
    
    # Plot mixed priority tests
    x_mixed = range(1, len(mixed_priority) + 1)
    plt.scatter(x_mixed, mixed_priority, label='With TC', color='green',
                alpha=0.6, s=100, edgecolors='black', marker='s')
    
    # Add mean lines
    plt.axhline(y=np.mean(best_effort), color='blue', linestyle='--', 
                alpha=0.5, label=f'No TC Mean: {np.mean(best_effort):.1f} Mbps')
    plt.axhline(y=np.mean(mixed_priority), color='green', linestyle='--',
                alpha=0.5, label=f'With TC Mean: {np.mean(mixed_priority):.1f} Mbps')
    
    plt.title('Individual Test Results')
    plt.xlabel('Test Number')
    plt.ylabel('Throughput (Mbps)')
    plt.legend()
    plt.grid(True, alpha=0.3, linestyle='--')
    
    # Adjust layout and save
    plt.tight_layout()
    plot_file = os.path.join(results_dir, 'throughput_comparison.png')
    plt.savefig(plot_file, dpi=150)
    print(f"\nVisualization saved: {plot_file}")
    plt.close()

def main():
    # Set up results directory
    results_dir = os.path.expanduser("~/tsn-emulation-project/results/baseline")
    
    if not os.path.exists(results_dir):
        print(f"ERROR: Results directory not found: {results_dir}")
        print("Please run baseline-test.sh first")
        return
    
    print(f"\nAnalyzing results in: {results_dir}")
    
    # Load best-effort data (no traffic control)
    print("\n" + "=" * 40)
    print("BEST-EFFORT TRAFFIC (NO TRAFFIC CONTROL)")
    print("=" * 40)
    
    best_effort_pattern = os.path.join(results_dir, "best_effort_*.json")
    best_effort_data, best_files = load_throughput_data(best_effort_pattern)
    
    if best_effort_data:
        print(f"  Files processed: {best_files}")
        print(f"  Throughput samples: {len(best_effort_data)}")
        print(f"  Mean throughput: {np.mean(best_effort_data):.2f} Mbps")
        print(f"  Std deviation: {np.std(best_effort_data):.2f} Mbps")
        print(f"  Minimum: {np.min(best_effort_data):.2f} Mbps")
        print(f"  Maximum: {np.max(best_effort_data):.2f} Mbps")
        print(f"  Coefficient of variation: {np.std(best_effort_data)/np.mean(best_effort_data):.3f}")
    else:
        print("  No valid best-effort data found")
    
    # Load mixed priority data (with traffic control)
    print("\n" + "=" * 40)
    print("MIXED PRIORITY TRAFFIC (WITH TRAFFIC CONTROL)")
    print("=" * 40)
    
    mixed_pattern = os.path.join(results_dir, "mixed_priority_*.json")
    mixed_data, mixed_files = load_throughput_data(mixed_pattern)
    
    if mixed_data:
        print(f"  Files processed: {mixed_files}")
        print(f"  Throughput samples: {len(mixed_data)}")
        print(f"  Mean throughput: {np.mean(mixed_data):.2f} Mbps")
        print(f"  Std deviation: {np.std(mixed_data):.2f} Mbps")
        print(f"  Minimum: {np.min(mixed_data):.2f} Mbps")
        print(f"  Maximum: {np.max(mixed_data):.2f} Mbps")
        print(f"  Coefficient of variation: {np.std(mixed_data)/np.mean(mixed_data):.3f}")
    else:
        print("  No valid mixed priority data found")
    
    # Perform comparison if we have both datasets
    if best_effort_data and mixed_data:
        print("\n" + "=" * 40)
        print("COMPARISON ANALYSIS")
        print("=" * 40)
        
        # Calculate differences
        throughput_diff = np.mean(mixed_data) - np.mean(best_effort_data)
        throughput_pct = (throughput_diff / np.mean(best_effort_data)) * 100
        
        std_diff = np.std(mixed_data) - np.std(best_effort_data)
        std_ratio = np.std(mixed_data) / np.std(best_effort_data) if np.std(best_effort_data) > 0 else 0
        
        print(f"  Throughput difference: {throughput_diff:+.2f} Mbps ({throughput_pct:+.1f}%)")
        print(f"  Throughput variability change: {std_ratio:.2f}x")
        
        if throughput_diff < 0:
            print(f"  → Traffic control reduced throughput by {-throughput_pct:.1f}%")
        else:
            print(f"  → Traffic control increased throughput by {throughput_pct:.1f}%")
        
        if std_ratio > 1:
            print(f"  → Traffic control increased variability by {std_ratio:.2f}x")
        else:
            print(f"  → Traffic control reduced variability by {1/std_ratio:.2f}x")
        
        # Create visualization
        print("\n" + "=" * 40)
        print("VISUALIZATION")
        print("=" * 40)
        create_throughput_plot(best_effort_data, mixed_data, results_dir)
    
    # Get latency information
    analyze_latency_from_ping()
    
    # Summary

    print("results/baseline/throughput_comparison.png")

if __name__ == "__main__":
    main()
