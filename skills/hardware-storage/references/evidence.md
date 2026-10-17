# Storage hardware evidence

| Layer | Evidence | Purpose |
| --- | --- | --- |
| Media/controller | `nvme list`, `nvme id-ctrl`, `smartctl`, `lsscsi`, `lspci -nn` | Model, firmware, media type, endurance, controller identity |
| Namespace/block | `lsblk -o +MODEL,SERIAL,ROTA,DISC-MAX`, `/sys/block`, `udevadm` | Capacity, sector size, discard, queue and stable device identity |
| RAID/mapper | `mdadm --detail`, `lvs`, `pvs`, `dmsetup ls --tree` | Physical-to-logical composition and redundancy path |
| PCIe/locality | `lspci -tv`, `/sys/bus/pci/devices`, `numactl -H`, `hwloc-info` | Root port, link state, NUMA locality, shared bottlenecks |
| Runtime behavior | `iostat -xz`, `blktrace`/`bpftrace`, `/proc/<pid>/io` | Service time, queueing, I/O mix and process attribution |

Record whether values describe a namespace, block device, controller, or physical medium. Capacity and bandwidth at one layer must not be copied to another without an explicit relationship.

For NVMe, record namespace identity separately from controller identity. For RAID or logical volumes, preserve all child devices and the mapping rather than reporting only the top-level path.

For workload behavior, read the [I/O access-pattern contract](../../access-pattern-analysis/references/model.md). Aggregate counters cannot establish random/sequential fractions or request-size percentiles. Emit separate patterns at application and block boundaries, and join them to storage entities rather than treating the workload pattern as a media property.
