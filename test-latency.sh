#!/bin/bash
echo "=== Quick Latency Test ==="
echo "Testing baseline latency between containers..."
echo ""

echo "Running 20 pings from sender to receiver:"
docker exec tsn-sender ping -c 20 10.10.10.3

echo ""
echo "=== Latency Statistics ==="
docker exec tsn-sender ping -c 20 10.10.10.3 | tail -3

echo ""
echo "To save results:"
echo "  docker exec tsn-sender ping -c 20 10.10.10.3 > ~/tsn-emulation-project/results/baseline/latency.txt"
