# Linux evidence guide

Collect commands at the narrowest scope that answers the question. Record command, timestamp, host/container scope, permissions, and relevant workload state.

| Area | Useful evidence | Typical question |
| --- | --- | --- |
| CPU/topology | `lscpu`, `numactl -H`, `/sys/devices/system/cpu`, `/proc/cpuinfo` | Are threads crossing sockets or sharing constrained cores? |
| Memory | `/proc/meminfo`, `/proc/<pid>/status`, `numastat`, cgroup memory files | Is the issue capacity, reclaim, locality, or bandwidth? |
| Scheduler | `pidstat -w`, `/proc/schedstat`, `perf sched`, `/proc/<pid>/sched` | Is runnable delay or migration limiting progress? |
| CPU time | `pidstat -u -t`, `perf stat`, `perf record`, `perf report` | Is time spent in user code, kernel code, or waiting? |
| I/O | `iostat -xz`, `pidstat -d`, `/proc/<pid>/io`, `filetop`, `biolatency` | Is latency from the device, filesystem, queue, or application? |
| Network | `ss -ti`, `sar -n DEV`, `ethtool -S`, `tc -s`, `tcpconnect` | Is throughput limited by drops, retransmits, queueing, or CPU? |
| Cgroups | `/sys/fs/cgroup`, `systemd-cgtop`, container runtime metadata | Is a limit or throttling hiding host capacity? |
| Kubernetes | `kubectl get pod -o wide`, `kubectl describe`, node allocatable/conditions | Where did the workload land and what constraints apply? |

Do not assume a command exists in a minimal image. When a profiler needs privileges, state that limitation and use a lower-privilege counter or an externally collected sample.
