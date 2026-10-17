# GPU evidence guide

Collect in layers and preserve the scope of each result.

| Layer | Evidence | Scope and purpose |
| --- | --- | --- |
| Device inventory | `nvidia-smi -q`, `rocm-smi`, `lspci -nn`, `/sys/class/drm` | Model, UUID, PCI address, memory, firmware, errors |
| Topology | `nvidia-smi topo -m`, `rocm-smi --showtopo`, `lspci -tv`, `numactl -H` | GPU-to-GPU, GPU-to-NIC, PCIe, and NUMA relationships |
| Visibility | CUDA/ROCm runtime query, container device files, Kubernetes device-plugin allocation | What the process, container, or pod can actually see |
| Dynamic telemetry | vendor query in repeat mode, DCGM/ exporter, ROCm SMI, cgroup and node metrics | Utilization, memory, clocks, power, temperature, throttling |
| Workload profile | Nsight Systems/Compute, ROCm profiler, `perf`, runtime traces | Kernel duration, launch gaps, copies, synchronization, occupancy |

Record host/container/pod scope and collection interval. A host-level inventory does not prove that a container can access every device. A device utilization sample does not identify which process caused it unless process attribution is collected.

For a minimal read-only snapshot, collect:

```text
vendor/model/UUID -> PCI address -> NUMA node -> parent/partition
-> visible device IDs -> allocation owner -> memory capacity/use
-> peer/link topology -> runtime and driver versions
```

Mark unavailable commands and privilege limitations explicitly. Never replace missing topology or attribution with an assumption.
