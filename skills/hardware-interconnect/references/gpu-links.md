# GPU interconnect evidence

Use multiple sources because topology reporting and usable bandwidth answer different questions.

| Path | Discovery evidence | Validation evidence |
| --- | --- | --- |
| GPU-GPU | `nvidia-smi topo -m`, `rocm-smi --showtopo`, vendor runtime topology | P2P access query and bidirectional transfer benchmark |
| GPU-CPU/NUMA | `nvidia-smi topo -m`, `numactl -H`, `lspci -tv`, `hwloc-info` | Host-to-device and device-to-host bandwidth by NUMA binding |
| GPU-NIC | GPU/NIC PCI tree, vendor topology, `/sys/class/pci_bus` | RDMA or socket transfer benchmark with explicit CPU affinity |
| GPU-storage | PCIe tree, NVMe/controller locality, GPUDirect capability if applicable | Read/write benchmark with path and cache semantics recorded |

For every edge record whether the result is hardware-reported, runtime-observed, or measured. Keep topology matrices and benchmark results as separate observations linked by the same edge ID.

## Minimal graph shape

```yaml
links:
  - id: link:gpu0-gpu1
    source: gpu:<uuid-0>
    target: gpu:<uuid-1>
    link_type: pcie
    direction: bidirectional
    negotiated_state: gen4-x16
    access_mode: peer_direct
    provenance: nvidia-smi-topology
    confidence: observed
capabilities:
  - subject: link:gpu0-gpu1
    name: measured_bandwidth
    value: 245
    unit: GB/s
    kind: measured
```
