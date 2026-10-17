# I/O access pattern 通用契约 v0.1

此处定义仓库自己的跨层契约，机器约束以同目录的 `io-access-pattern.schema.json` 为准。它不是硬件规格表，也不是 fio 参数的直接翻译。

## 图与观测的连接

文档保留 `entities`、`relations`、`observations`、`capabilities`，新增 `io_access_patterns`。模式是带证据的行为描述，通过 workload/actor/target/path 引用原图；不会把进程、文件或对象存储放进 hardware 的实体词表。单独安装此 skill 时，schema、脚本和示例都在 skill 内部可用。

```text
workload/phase -> actor -> file/API/object/copy -> block/device/link
                             |                       |
                      pattern@application       pattern@block
                             |                       |
                          latency                queue/time
```

`path_entity_ids` 按本次分析的访问方向排列，只表明经过哪些实体；确切连接语义由 `relations` 的 source/type/target 表达，不推导物理数据流或总线必经顺序。GPU copy 的 `actor_id` 是提交者，`source_id` 是数据源，`target_id` 是目的地；read/write 的方向相对于观测 API。

同一批数据在不同层各有一个模式。用 `observed_downstream_of` 关联下游模式，证据不足时仅写 `correlated_with`。这些关系允许 pattern ID 作为端点；不意味着字节相等、请求一一对应或已证明因果。测得 amplification 时注明同窗口、数据范围、缓存和额外流量。

ID 复用已有 GPU UUID、namespace ID、进程实例 ID、对象集合 ID 等。`/dev/nvme0n1`、裸 PID、容器内 fd 都不是全局稳定标识，需加 host/boot/进程启动时间等作用域。部分图用 `external_entity_ids` 明确声明外部实体引用，后续合并时解析它们。

## 核心字段

| 字段 | 含义与边界 |
| --- | --- |
| `id`, `workload_id`, `phase` | 行为 ID、工作负载、启动/稳态/compaction 等阶段；不同 phase 不混成平均 |
| `actor_id`, `source_id`, `target_id` | 发起方、可选的数据源、被访问对象/目的地；目标不必是磁盘 |
| `layer` | application / syscall / filesystem / block / device / object_api / network / gpu_transfer |
| `scope` | host/container/pod/process/stream 等取证范围，以稳定实体 ID 补充 |
| `window` | RFC3339 起止时间、可选采样间隔；计数器应取区间增量 |
| `evidence` | observed/inferred/declared/synthetic、来源、收集时间、方法、采样率/丢失事件 |
| `field_evidence` | 可选，以 pattern 内的 JSON Pointer 为 key 覆盖某字段的 evidence；例如配置深度 declared、in_flight observed |
| `missing` | 当前证据无法回答的字段/映射，不用空值冒充完整观测 |
| `operation_mix` | 枚举操作的 fraction、`basis`（request_count/bytes）；必须含 unknown 剩余量或完整归一化 |
| `request_size` | 按操作区分的固定值、分位数或带 count 的直方图；只描述样本分布，不假设全量 |
| `addressing` | file_offset / block_lba / object_key / memory_offset / stream_position；顺序/随机/stride，分组键、stride、对齐 |
| `concurrency` | sync/async/mixed/unknown、配置深度、worker 数、实际 in-flight 分布及其作用域 |
| `arrival` | open_loop/closed_loop/unknown、steady/bursty/periodic/unknown、间隔分布、可选 batch size |
| `locality` | working set、hot set、reuse distance、access skew；不同单位/测量方法不能互换 |
| `semantics` | buffered/direct/mmap/unknown、cold/warm/mixed/unknown、命中率、flush 策略、完成边界、持久化保证和 ordering |

`distribution` 的单位和形式显式声明。`fixed` 是固定值；`percentiles` 是样本分位数，不能反推出直方图；`histogram` 用 `[lower, upper)` 桶与计数表示。相同模式的大小、操作、时延仍是边际分布，不能当作它们的联合分布。需要重放时应保留原始事件/trace 来源、时间戳、operation/offset/length/stream/order；此摘要本身不保证精确重放。

`request_size[].size_basis` 区分请求长度、实际传输长度和 payload 大小；短读、部分写入、压缩、消息封装和对象 Range 请求会令三者不同。`operation_mix.basis=bytes` 只统计定义过的数据字节，不把无数据的 flush 算成零比例请求混进去；需要请求占比时另建 request_count 模式。请求是否含失败/重试、in_flight 是时间采样还是事件采样，在 evidence.method 中注明。混合来源时用 `field_evidence` 对精确字段提供不同的来源和 basis。

`addressing.pattern=sequential` 的含义是同一分组内下一请求起点等于上一请求末尾（按该地址空间单位）；stride 用相邻起点之差。`block_lba` 的偏移以逻辑块计数，记录 `address_unit_bytes` 才能转为 bytes。多线程顺序流合并后可显得随机，文件偏移连续也不能证明物理 LBA 连续。mixed 的随机比例只在明确分类方法/分组后填写；只有键采样时优先记录 skew/reuse，不推导 seek 距离。

通用 schema 使用 `unknown` 表达未知分类。对不适用的可选字段直接省略；例如消息没有文件偏移、GET 没有文件系统 durability。零请求窗口不生成归一化的 operation_mix，说明无样本。

## 结果与能力

`observations` 每项记录 subject、metric、value、unit、aggregation、window、source、scope、confidence；可附 `pattern_id`。常见 metric：request_rate、byte_rate、completion_latency、submit_latency、queue_latency、error_rate、retry_rate。unit 使用 requests/s、bytes/s、us、ratio 等明确单位；aggregation 用 mean/p95/p99 等，不能将均值当尾延迟。

`capabilities` 继续表示设备/链路 advertised/measured/inferred 能力。配置 IOPS 是负载目标，实测 IOPS 是 observation，厂商 peak IOPS 是 capability。不能脱离块大小、并发和读写 mix 比较三者。

## 校验

```bash
python -m pip install -r skills/access-pattern-analysis/scripts/requirements.txt
python skills/access-pattern-analysis/scripts/validate_io_pattern.py skills/access-pattern-analysis/references/examples/storage-pipeline.json
```

JSON Schema 校验字段类型、单位、枚举与分布形状；脚本进一步校验 ID/引用、时间窗口、mix 归一化、分位数单调性、直方图桶和计数。校验通过不证明采集正确或跨层归因成立。
