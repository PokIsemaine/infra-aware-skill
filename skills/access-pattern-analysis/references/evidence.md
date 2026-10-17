# 采集与解释

先从已有 trace、profile、配置和计数器建模；本 skill 不自动运行压测。若要补实验，明确数据集/文件、读写范围和资源预算，再执行对应任务授权内的采集。

| 来源 | 可以支持 | 不能单独支持 |
| --- | --- | --- |
| 应用/API spans、访问日志 | operation、对象/请求大小、时间、请求方、服务完成边界 | 设备 I/O 次数、介质持久化 |
| syscall/eBPF/系统调用 trace | fd、偏移、读写长度、调用返回、线程序列 | 未关联 fd/offset 时的顺序性；自动推导 mmap 全部访问 |
| `/proc/<pid>/io` 区间差分 | 进程字符/字节计数等聚合信息 | 随机率、请求大小分布、单请求尾延迟 |
| block trace、issue/complete 事件 | block request 的 offset、长度、顺序、排队/完成 | 应用原始请求大小、稳定的单进程 writeback 归属 |
| `/proc/diskstats` 等块统计 | 设备级完成计数、字节和时间的区间聚合 | 从平均请求大小重建完整大小分布，或识别随机访问 |
| fio 配置与结果 | declared 的访问参数、实际 depth/latency/bandwidth 统计 | 把 iodepth 直接当实测并发，把指定 rw 模式当生产工作负载证据 |
| GPU runtime trace | copy 的方向、大小、stream、提交/完成、overlap | 自动证明存储到 GPU 的直达路径或 kernel 内访存模式 |

记录 collector/工具版本、采样率、事件丢失、host/namespace/进程实例、时间基准和 fd/device/object 映射。不同 trace 时钟未对齐时不得建立精确先后关系。把热身、cache warmup、稳态、checkpoint/compaction 分窗；小样本高分位数标注 sample_count。

`O_DIRECT`、同步/异步提交和持久化是独立维度。不要以清空全局 page cache 作为默认采集前置步骤。批量吞吐和单请求延迟有不同完成边界；缓存命中率需记录缓存层，不能用不同语义的字节计数直接作比。

一手文档（2026-10-18 核对）：

- [Linux /proc：进程 I/O 计数](https://docs.kernel.org/filesystems/proc.html)：区分 rchar/wchar 与 read_bytes/write_bytes，并注意取消写入和计数边界。
- [Linux I/O statistics](https://docs.kernel.org/admin-guide/iostats.html)：设备统计的完成、合并、在途计数和时间语义。
- [fio 文档](https://fio.readthedocs.io/en/latest/fio_doc.html)：rw/bs/iodepth/direct、读写混合、随机分布与 achieved depth。复现实验时记录实际安装版本和配置。
