---
name: linux-infra-awareness
description: Build Linux infrastructure context for code analysis and performance optimization using hardware, kernel, container, Kubernetes, and observability evidence.
metadata:
  short-description: Linux infrastructure context for code analysis
---

# Linux Infra Awareness

This is the routing skill for the layered registry. Use the narrowest atomic skill that can answer the question, then combine its evidence with Linux, platform, or external-service context when needed.

Use this skill when an analysis depends on the execution environment: CPU/GPU topology, memory and NUMA, storage or network paths, Linux scheduling and I/O, containers, Kubernetes placement, or runtime observations.

## Operating rules

- Establish the workload and execution boundary before suggesting an optimization.
- Treat discovered system facts as evidence with a source, timestamp, scope, and confidence. Distinguish observed facts, inferred relationships, and hypotheses.
- Prefer read-only inspection first. Ask before changing kernel settings, workloads, cluster resources, or persistent configuration.
- Preserve units and collection context: logical versus physical CPU, host versus container view, device versus mount, and node versus pod scope.
- Connect every recommendation to a bottleneck and a measurable validation signal. Do not infer causality from a single utilization percentage.
- Report missing permissions, unavailable counters, sampling interval, and topology ambiguity instead of silently filling gaps.

## Workflow

1. Define the workload, process or service, deployment scope, and target metric.
2. Collect the smallest useful Linux snapshot using the commands in [references/evidence.md](references/evidence.md).
3. Map the path from source code to process, thread, cgroup, container, pod, node, device, and external dependency.
4. Form competing bottleneck hypotheses across CPU, memory, synchronization, I/O, network, scheduler, and placement.
5. Select observations or profiling tools that can falsify those hypotheses.
6. Recommend a change only with an expected mechanism, safety boundary, and before/after measurement.

## Capability areas

- Hardware and topology: `/proc`, `/sys`, `lscpu`, NUMA, accelerators, PCIe, memory bandwidth, storage, and network devices.
- Linux runtime: processes, threads, scheduler behavior, cgroups, namespaces, page faults, locks, syscalls, filesystems, and TCP.
- Containers and Kubernetes: requests/limits, QoS, throttling, affinity, topology spread, device allocation, and pod-to-node placement.
- Observability: `perf`, eBPF tools, `/proc` counters, cgroup statistics, node and workload metrics, logs, traces, and continuous profiling.

Read [references/evidence.md](references/evidence.md) for command selection and evidence recording. Read [references/model.md](references/model.md) when building a reusable infrastructure model or explaining a causal chain.

## Atomic skill routing

- GPU device facts, memory hierarchy, links, partitioning, or accelerator placement: use [`hardware-gpu`](../hardware-gpu/SKILL.md).
- NIC, RDMA, Ethernet, PCIe, queue, or host network topology: use [`hardware-network-topology`](../hardware-network-topology/SKILL.md).
- Disks, SSD/NVMe, RAID, filesystems, storage fabrics, or volume paths: use [`hardware-storage`](../hardware-storage/SKILL.md).
- CPU sockets, NUMA, PCIe, CXL, accelerator, and NIC locality as a graph: use [`hardware-interconnect`](../hardware-interconnect/SKILL.md).
- Read/write or copy behavior, request sizes, sequential/random access, locality, concurrency, caching, and completion boundaries: use [`access-pattern-analysis`](../access-pattern-analysis/SKILL.md). Join its patterns to the same hardware entities and retain separate per-layer observations.
