#!/bin/bash
echo "=== Baseline Measurements ==="

# Create results directory
RESULTS_DIR="$HOME/tsn-emulation-project/results/baseline"
mkdir -p "$RESULTS_DIR"
echo "Results will be saved to: $RESULTS_DIR"

# Clean up any existing iperf servers
echo "1. Cleaning up existing iperf3 processes..."
docker exec tsn-receiver pkill iperf3 2>/dev/null
docker exec tsn-sender pkill iperf3 2>/dev/null
sleep 2

# Start iperf3 servers on receiver
echo "2. Starting iperf3 servers on receiver..."
echo "   Port 5001: High priority traffic"
echo "   Port 5002: Medium priority traffic"
docker exec -d tsn-receiver iperf3 -s -p 5001
docker exec -d tsn-receiver iperf3 -s -p 5002
sleep 3  # Give servers time to start

echo "3. Test 1: Best-effort traffic (NO Traffic Control)..."
echo "   Testing port 5001 without traffic control"
echo "   Clearing traffic control for baseline..."
docker exec tsn-sender tc qdisc del dev eth0 root 2>/dev/null

for i in {1..5}; do
    echo "   Run $i of 5..."
    docker exec tsn-sender iperf3 -c 10.10.10.3 -p 5001 -t 3 -J > "$RESULTS_DIR/best_effort_$i.json"
    if [ $? -eq 0 ]; then
        echo "     ✓ Success"
    else
        echo "     ✗ Failed"
    fi
    sleep 1
done

echo "4. Test 2: Mixed priority traffic (WITH Traffic Control)..."
echo "   Re-enabling traffic control..."
docker exec tsn-sender tc qdisc del dev eth0 root 2>/dev/null
docker exec tsn-sender tc qdisc add dev eth0 root handle 1: prio bands 3
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 \
  match ip dport 5001 0xffff flowid 1:1
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 2 u32 \
  match ip dport 5002 0xffff flowid 1:2
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 3 u32 \
  match ip dst 0.0.0.0/0 flowid 1:3
sleep 1

echo "   Starting background high-priority traffic..."
docker exec -d tsn-sender iperf3 -c 10.10.10.3 -p 5001 -t 15

echo "   Testing medium-priority traffic under load..."
for i in {1..3}; do
    echo "   Mixed test $i of 3..."
    docker exec tsn-sender iperf3 -c 10.10.10.3 -p 5002 -t 3 -J > "$RESULTS_DIR/mixed_priority_$i.json"
    if [ $? -eq 0 ]; then
        echo "     ✓ Success"
    else
        echo "     ✗ Failed"
    fi
    sleep 2
done

echo "5. Clean up..."
docker exec tsn-receiver pkill iperf3 2>/dev/null
docker exec tsn-sender pkill iperf3 2>/dev/null

echo ""
echo "=== Baseline Tests Complete ==="
echo "Results saved in: $RESULTS_DIR"
echo ""
echo "Files created:"
ls -la "$RESULTS_DIR/" | grep -E "\.json$|total"
echo ""
#echo "Next step: Run analysis with: python3 scripts/analyze-initial.py"
