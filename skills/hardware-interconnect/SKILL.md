---
name: hardware-interconnect
description: Model GPU interconnects and Linux host locality across GPUs, CPUs, NUMA, PCIe, NICs, and storage.
metadata:
  short-description: Host interconnect and locality graph
---

# Hardware Interconnect

Use this atomic skill when GPU placement, peer communication, host staging, or device locality may explain performance. It is the physical graph companion to `hardware-gpu`; resource allocation and scheduler placement remain platform concerns.

Build a graph of sockets, NUMA nodes, memory controllers, PCIe root ports and switches, GPUs, NICs, storage controllers, and CXL devices. For GPU analysis, explicitly model GPU-GPU links (NVLink, XGMI, PCIe, or host-staged), GPU-CPU/NUMA paths, GPU-NIC paths, and GPU-storage paths. Preserve parent-child PCI relationships and the NUMA node associated with each endpoint. Mark links as observed, reported by firmware, or inferred.

Use `lstopo`, `lspci -tv`, `numactl -H`, `/sys/bus/pci/devices`, `hwloc-info`, and vendor topology tools when available. Record link generation/width and negotiated state separately from theoretical maximum.

The output should answer locality questions such as which CPU and memory domain can efficiently feed a GPU, whether two GPUs share a PCIe bottleneck, whether a NIC is local to a GPU, and which facts still need a microbenchmark.

## GPU interconnect output

Emit a graph whose link records contain:

- `source` and `target`: stable entity IDs such as GPU UUID or PCI address
- `link_type`: `nvlink`, `xgmi`, `pcie`, `cxl`, `numa_memory`, or `host_staged`
- `direction`: `bidirectional`, `source_to_target`, or `unknown`
- `generation`, `width`, and `negotiated_state` when available
- `advertised_bandwidth` and `measured_bandwidth` as separate capabilities
- `access_mode`: `peer_direct`, `peer_disabled`, `host_staged`, or `unknown`
- `provenance` and `confidence`

Do not equate a vendor link label with usable application bandwidth. Validate important paths with peer-access checks and a transfer microbenchmark under the workload's message sizes.
