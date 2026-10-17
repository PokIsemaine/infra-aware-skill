# Example normalized GPU chain

This is a shape example, not a hardware claim:

```yaml
entities:
  - {id: host:node-01, type: host, hostname: node-01}
  - {id: gpu:0000:41:00.0, type: gpu, vendor: nvidia, model: "<observed>", pci_address: "0000:41:00.0"}
  - {id: gpu-partition:gpu0:0, type: gpu_partition, partition_kind: mig, parent_gpu: gpu:0000:41:00.0}
  - {id: pod:ml/infer-7f, type: pod, namespace: ml, name: infer-7f}
  - {id: process:2184, type: process, pid: 2184}
relations:
  - {source: gpu:0000:41:00.0, type: attached_to, target: host:node-01}
  - {source: gpu-partition:gpu0:0, type: allocated_to, target: pod:ml/infer-7f}
  - {source: process:2184, type: runs_on, target: pod:ml/infer-7f}
observations:
  - subject: gpu-partition:gpu0:0
    metric: memory_used
    value: 8123
    unit: MiB
    timestamp: "<RFC3339>"
    source: dcgm
    scope: pod
    confidence: observed
```
