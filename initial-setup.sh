#!/bin/bash
echo "=== Initial Results - Traffic Control Setup ==="

# Setup traffic control on sender
echo "1. Clearing existing traffic control..."
docker exec tsn-sender tc qdisc del dev eth0 root 2>/dev/null
sleep 1

echo "2. Setting up priority queuing (3 bands)..."
docker exec tsn-sender tc qdisc add dev eth0 root handle 1: prio bands 3

echo "3. Creating traffic filters..."
# Clear existing filters
docker exec tsn-sender tc filter del dev eth0 2>/dev/null

# High priority: port 5001 -> band 1
echo "   Port 5001 -> High Priority (Band 1)"
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 1 u32 \
  match ip dport 5001 0xffff flowid 1:1

# Medium priority: port 5002 -> band 2
echo "   Port 5002 -> Medium Priority (Band 2)"
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 2 u32 \
  match ip dport 5002 0xffff flowid 1:2

# Low priority: everything else -> band 3
echo "   All other traffic -> Low Priority (Band 3)"
docker exec tsn-sender tc filter add dev eth0 parent 1:0 protocol ip prio 3 u32 \
  match ip dst 0.0.0.0/0 flowid 1:3

echo "4. Traffic control setup complete!"
echo ""
echo "=== Verification ==="
echo "Queue disciplines:"
docker exec tsn-sender tc qdisc show dev eth0
echo ""
echo "Filters:"
docker exec tsn-sender tc filter show dev eth0
echo ""
#echo "=== Ready for baseline testing ==="
