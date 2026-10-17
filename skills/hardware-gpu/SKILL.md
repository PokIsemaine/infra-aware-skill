---
name: hardware-gpu
description: Identify Linux GPU hardware, memory, physical links, and device capabilities for infrastructure-aware analysis.
metadata:
  short-description: GPU hardware and topology facts
---

# GPU Hardware

Use this atomic skill when GPU model, count, memory, hardware-defined partitioning, peer access, or accelerator locality can change a code or workload decision. Keep scheduling and allocation semantics in platform skills.

Collect facts before interpreting utilization. At minimum capture vendor/model, device count, VRAM, compute capability or equivalent, driver/runtime versions, PCI address, NUMA locality, and whether the process sees the host device directly, through a container, or through a scheduler allocation.

The canonical GPU output has four parts:

1. **Entities**: physical GPU, hardware-defined logical partition (MIG/vGPU/SR-IOV), GPU memory pool, and host. Process, container, pod, and runtime entities are joined from upper layers.
2. **Relations**: `partition_of`, `attached_to`, `peer_link`, and `connected_via`. `visible_to`, `allocated_to`, and `runs_on` are platform/runtime relations.
3. **Observations**: measured utilization, memory usage, temperature, power, clocks, errors, transfer rate, kernel duration, and queue/wait time.
4. **Capabilities**: advertised or measured memory capacity, compute throughput, copy bandwidth, peer access, link type, and partition limits.

Use the schema in [references/model.yaml](references/model.yaml). Every observation must retain its source, timestamp, scope, unit, and confidence. Keep static inventory, dynamic telemetry, and workload measurements separate.

Prefer read-only evidence such as `nvidia-smi -q`, `rocm-smi`, `lspci -nn`, and `/sys/class/drm`. Record hardware-defined MIG/SR-IOV/vGPU partitions as separate logical devices and preserve the parent device relationship. Runtime visibility and Kubernetes allocation belong to platform skills; this skill may consume their outputs as relations. See [references/evidence.md](references/evidence.md) for vendor-neutral collection and scope rules.

For communication claims, inspect peer-to-peer accessibility and actual link topology. Do not infer NVLink, XGMI, PCIe, or host-staged transfer behavior from device names alone.

Output a normalized device inventory plus uncertainty and a validation plan. Keep measured bandwidth/latency separate from vendor peak specifications.

## End-to-end GPU path

When the request concerns an application or service, connect the GPU facts through this path:

```text
code region -> process/thread -> runtime context -> container/pod
  -> allocated logical GPU -> parent physical GPU -> PCIe/NUMA/link topology
  -> GPU memory/copy engines/SMs -> kernel and transfer observations
```

Do not claim that a GPU is the bottleneck until the path includes workload evidence such as kernel time, launch gaps, memory pressure, host-to-device transfer, synchronization, or device queueing. For multi-GPU work, join platform allocation facts to this hardware graph; do not infer allocation from hardware inventory.

## Vendor handling

Use one normalized model for NVIDIA, AMD, and other accelerators. Put vendor-specific fields under `vendor_fields`; do not make vendor names part of stable entity IDs. Treat MIG, vGPU, SR-IOV, and scheduler slices as logical devices with an explicit parent.
