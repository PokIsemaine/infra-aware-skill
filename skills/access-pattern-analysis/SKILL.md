---
name: access-pattern-analysis
description: Model I/O access patterns across application, filesystem, block, object, network, and GPU-transfer boundaries, preserving request shape, locality, concurrency, semantics, and evidence.
metadata:
  short-description: Cross-layer access pattern analysis
---

# Access Pattern 分析

用于描述工作负载怎样访问资源，并把行为绑定到已有 infra 图。此 skill 属于 workload 层；设备规格仍由 hardware skill 提供，文件系统、分配和服务语义由对应层解释。

## 建模步骤

1. 确定 workload、phase、发起方、目标、观测层、时间窗口，以及逻辑请求的定义（API 调用、syscall、block request、对象请求、消息或 copy）。
2. 在已有图中引用实体 ID，形成路径。无法关联到设备时列出缺口；外部快照中的 ID 放入 `external_entity_ids`，不要猜测映射。
3. 按 phase、目标、层和语义边界拆分模式，记录操作混合、大小分布、地址/键序列、并发、到达过程、局部性和缓存/完成语义。只填有证据的字段。
4. 将吞吐、延迟等结果写入 `observations`，用 `pattern_id` 关联访问模式；硬件上限仍在 `capabilities`。请求模式、性能结果和设备能力分别保留。
5. 用 [JSON Schema](references/io-access-pattern.schema.json) 和 [校验脚本](scripts/validate_io_pattern.py) 校验。交付模式、证据、图关联和缺失项；基准配置只能标为 declared，不能写成实测。

## 必须保持的区别

- 应用请求、文件访问、块请求是不同观测边界。缓存、readahead、合并、拆分和重试可改变数量、大小和顺序；跨层模式通过关系关联，不能直接复制。
- 操作占比注明按请求数还是字节数，取值为 0–1。顺序性必须注明地址空间和分组键，按 stream/file/device 分组后判断；对象键和消息不能默认视为线性地址。
- `io_mode` 描述调用/提交方式，`configured_depth` 是配置，`in_flight` 是实际在途请求统计；异步接口不保证达到目标并发。
- buffered/direct、cache warmness、缓存命中率和 durability 分开记录。同步调用返回、direct I/O 完成、远端 ACK 均不能单独证明介质持久化。
- 未知值用 `unknown` 或省略字段并列入 `missing`；不使用 0 替代未知。合成例子标为 synthetic。推断依据与原始证据分别保留。

按需读 [字段与跨层契约](references/model.md)、[采集与解释](references/evidence.md) 和 [完整跨层示例](references/examples/storage-pipeline.json)。示例包含应用读取、块设备读取、GPU copy 和对象请求，均为合成数据。
