# Example storage path

```yaml
entities:
  - {id: media:nvme0, type: storage_media, media_kind: nvme, model: "<observed>"}
  - {id: ns:nvme0n1, type: storage_namespace, parent_media: media:nvme0, capacity_bytes: "<observed>"}
  - {id: ctl:pci-0000:5e:00.0, type: storage_controller, controller_kind: nvme}
  - {id: block:nvme0n1, type: block_device, device_name: /dev/nvme0n1}
relations:
  - {source: ns:nvme0n1, type: namespace_of, target: media:nvme0}
  - {source: ns:nvme0n1, type: controlled_by, target: ctl:pci-0000:5e:00.0}
  - {source: block:nvme0n1, type: controlled_by, target: ctl:pci-0000:5e:00.0}
observations:
  - subject: ctl:pci-0000:5e:00.0
    metric: negotiated_pcie_width
    value: 4
    unit: lanes
    timestamp: "<RFC3339>"
    source: lspci
    scope: host
    confidence: observed
```
