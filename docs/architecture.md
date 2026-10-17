# Registry architecture

The registry is organized by where an optimization fact originates and by the smallest reusable capability that can collect or interpret it.

```text
hardware      physical devices, topology, links, capacities, locality
    -> kernel  Linux scheduling, memory, I/O, networking, cgroups, syscalls
    -> platform containers, Kubernetes placement, device plugins, service meshes
    -> external  databases, object stores, queues, APIs, remote services
    -> workload  application code, model/runtime, pipeline, and target metrics
```

The arrows describe evidence flow, not a mandatory execution order. A skill should own one evidence boundary. Cross-layer analysis belongs in a routing skill that references atomic skills rather than duplicating their inventories.

## Naming

Use `<layer>-<capability>` for discoverable skills, for example `hardware-gpu` and `hardware-storage`. Keep vendor or generation details in references or collected metadata unless they require materially different procedures. Prefer a new skill only when the evidence source, decision boundary, or safety constraints differ.

## Initial hardware registry

- `hardware-gpu`: GPU devices, memory, hardware-defined partitions, peer access, and physical locality. Allocation and runtime visibility are platform concerns.
- `hardware-network-topology`: NIC, Ethernet, RDMA, queues, and fabric paths.
- `hardware-storage`: media, namespaces, controllers, block-device identity, and physical paths; join filesystem semantics and volume lifecycle from their owning layers.
- `hardware-interconnect`: shared CPU/NUMA/PCIe/CXL locality graph.

Future layers should add `kernel-*`, `platform-*`, and `external-*` skills while keeping this same atomic boundary.

## GPU layer boundary

`hardware-gpu` owns what the device is and how it is physically connected. It does not own who receives the device or what a process can see inside a container. Those facts belong to platform skills:

- `platform-gpu-runtime`: CUDA/ROCm runtime visibility, device files, process-to-device attribution, and runtime contexts.
- `platform-kubernetes-gpu`: device plugins, resource requests, MIG resources, scheduling, allocation, and pod placement.

The unified graph joins these layers through stable GPU UUIDs, PCI addresses, partition IDs, pod IDs, and process/container IDs.

## GPU-first implementation

GPU is the first complete vertical slice. Its skill owns GPU evidence, while the shared model connects GPU entities to processes, containers, pods, hosts, NUMA, PCIe, and peer links. Future skills should emit the same four-part shape rather than inventing a separate inventory format.

## Cross-layer I/O access patterns

`access-pattern-analysis` owns the common behavioral model for file/block I/O, object API access, network messages, and GPU copies. It is a workload skill that can describe observations at different layers; it does not change hardware, kernel, platform, or external-service ownership.

The canonical [contract](../skills/access-pattern-analysis/references/model.md) and [JSON Schema](../skills/access-pattern-analysis/references/io-access-pattern.schema.json) live inside the skill for standalone distribution. A snapshot retains entities/relations/observations/capabilities and adds `io_access_patterns`. Patterns reference existing entity IDs, phases, scopes and time windows; performance observations reference `pattern_id`. Kernel readahead, merging, caching, retries, and copies produce different patterns on the same graph. Preserve transformations and unresolved mappings instead of collapsing the layers.

The current GPU/storage `references/model.yaml` files are descriptive vocabularies. The I/O JSON Schema is the first machine-validated extension; it does not imply those existing YAML documents are executable schemas.
