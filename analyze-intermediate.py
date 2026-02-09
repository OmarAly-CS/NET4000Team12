#!/usr/bin/env python3
import re, numpy as np, os

def extract_ping_times(filename):
    times = []
    with open(filename) as f:
        for line in f:
            match = re.search(r'time=([\d.]+)\s*ms', line)
            if match:
                times.append(float(match.group(1)))
    return times

print("=== Intermediate Results Analysis==")

results_dir = os.path.expanduser("~/tsn-emulation-project/results/intermediate")

# Analyze each test
tests = [
    ("1_baseline_ping.txt", "Baseline (no load)"),
    ("2_ping_udp_load.txt", "With UDP background"),
    ("3_ping_tcp_load.txt", "With TCP background")
]

for filename, label in tests:
    filepath = os.path.join(results_dir, filename)
    if os.path.exists(filepath):
        times = extract_ping_times(filepath)
        if times:
            print(f"\n{label}:")
            print(f"  Samples: {len(times)}")
            print(f"  Avg: {np.mean(times):.3f} ms")
            print(f"  Min/Max: {min(times):.3f}/{max(times):.3f} ms")
            print(f"  Jitter (std): {np.std(times):.3f} ms")
            print(f"  95th %ile: {np.percentile(times, 95):.3f} ms")
