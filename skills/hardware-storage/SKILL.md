---
name: hardware-storage
description: Identify Linux storage media, controllers, physical paths, queues, and hardware capabilities for infrastructure-aware analysis.
metadata:
  short-description: Storage device and path facts
---

# Storage Hardware

Use this atomic skill when storage latency, throughput, durability, or locality can affect a workload. It owns physical and block-device facts; filesystem behavior belongs to kernel skills, and mounts/volumes belong to platform skills.

Trace the hardware path from logical block device through mapper/RAID layer, controller, PCIe path, and physical media. Capture device model and rotational/flash class, sector sizes, queue depth, controller locality, negotiated PCIe state, endurance, namespace/LBA layout, and capacity. Model filesystem, mount, container, and volume entities as joined upper-layer relations rather than hardware entities.

Prefer `lsblk`, `udevadm`, `nvme list`, `nvme id-ctrl`, `mdadm --detail`, `lvm`, `/sys/block`, `lspci -tv`, and `smartctl` when available. Keep logical volumes, block devices, controllers, and physical media separate. Use `iostat` and process I/O counters as observations joined from kernel/workload skills, not as static hardware facts.

Separate vendor peak specifications from measured service time, queue depth, read/write mix, and tail latency. State whether durability and controller cache semantics were verified before recommending asynchronous or buffered I/O changes.

## Storage path output

Emit entities and relations for:

```text
media -> namespace/lun -> controller -> PCIe/CXL path -> NUMA node -> block device
```

Each path edge should include `link_type`, negotiated PCIe state when applicable, locality, queue characteristics, provenance, and confidence. Keep `advertised` and `measured` capacity, bandwidth, IOPS, and latency separate.

Read [references/evidence.md](references/evidence.md) for collection scope and [references/model.yaml](references/model.yaml) for the normalized storage graph.

## Workload access patterns

Use [`access-pattern-analysis`](../access-pattern-analysis/SKILL.md) to describe how a workload accesses these devices. Reuse this skill's block-device/controller IDs as pattern targets and graph path references. Request size, sequential/random behavior, read/write mix, concurrency, caching, and completion semantics belong to that cross-layer behavior model, not to hardware capabilities. Compare device specifications only against a pattern with compatible block size, mix, concurrency, and durability conditions.
