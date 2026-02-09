#!/bin/bash
echo "=== Results ==="

RESULTS_DIR="$HOME/tsn-emulation-project/results/intermediate"
mkdir -p "$RESULTS_DIR"

echo "1. Setup traffic control..."
docker exec tsn-sender tc qdisc del dev eth0 root 2>/dev/null
docker exec tsn-sender tc qdisc add dev eth0 root handle 1: prio bands 3

echo "2. Baseline ping (no load)..."
docker exec tsn-sender ping -c 30 10.10.10.3 | tee "$RESULTS_DIR/1_baseline_ping.txt"

echo "3. Latency with UDP background traffic..."
docker exec -d tsn-receiver iperf3 -s -p 6001 -u
sleep 2
docker exec -d tsn-sender iperf3 -c 10.10.10.3 -p 6001 -u -b 5M -t 30
docker exec tsn-sender ping -c 20 10.10.10.3 | tee "$RESULTS_DIR/2_ping_udp_load.txt"

echo "4. Latency with TCP background traffic..."
docker exec tsn-receiver pkill iperf3 2>/dev/null
sleep 2
docker exec -d tsn-receiver iperf3 -s -p 6002
sleep 2
docker exec -d tsn-sender iperf3 -c 10.10.10.3 -p 6002 -t 20
docker exec tsn-sender ping -c 20 10.10.10.3 | tee "$RESULTS_DIR/3_ping_tcp_load.txt"

echo "5. Clean up..."
docker exec tsn-receiver pkill iperf3 2>/dev/null
docker exec tsn-sender pkill iperf3 2>/dev/null

echo "Tests complete! Results in: $RESULTS_DIR"
