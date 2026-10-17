---
name: hardware-network-topology
description: Map Linux NIC, Ethernet, RDMA, PCIe, queue, and fabric topology for communication and distributed workload analysis.
metadata:
  short-description: NIC and communication topology facts
---

# Network Topology

Use this atomic skill when network placement, link capacity, transport choice, or queueing may explain application behavior.

Inventory interface name and state, MAC, PCI address, driver and firmware, speed, MTU, RSS/queue counts, NUMA node, offloads, and link partner. For RDMA record device, port state, GID, link layer, and userspace/provider versions. Trace the path across NIC, PCIe root complex, switch/fabric, peer NIC, and endpoint where evidence is available.

Use `ip -d link`, `ethtool`, `lspci -tv`, `/sys/class/net`, `rdma link`, `ibdev2netdev`, `ss -ti`, and counters or packet captures as appropriate. Treat advertised speed, observed throughput, and application goodput as distinct values.

Represent topology edges explicitly and mark unknown switch or cross-host segments. A high network rate alone does not establish that the application is network-bound; pair it with queue, retransmit, CPU, latency, and workload measurements.
