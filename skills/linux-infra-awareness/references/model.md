# Infrastructure model

Represent an optimization context as a graph with typed entities and observations:

```text
code region -> process/thread -> cgroup/container -> pod -> node
                                      |                 |
                                  limits            CPU/NUMA/GPU/device
                                      |                 |
                                  metric/profile <- kernel/filesystem/network
```

Each observation should include:

- `subject`: entity or edge being measured
- `metric`: name and unit
- `value`: raw value plus aggregation (average, p95, rate, count)
- `window`: start, end, and sampling interval
- `source`: command, exporter, profiler, or trace span
- `scope`: host, namespace, container, pod, node, or device
- `confidence`: observed, inferred, or hypothesized

Keep derived conclusions separate from raw observations. A high CPU utilization is an observation; CPU throttling, lock contention, or useful work are competing explanations that need additional evidence.

## I/O access patterns

For structured behavior use the [I/O access-pattern contract](../../access-pattern-analysis/references/model.md) and its [JSON Schema](../../access-pattern-analysis/references/io-access-pattern.schema.json). The extension preserves entities, relations, observations, and capabilities, adding `io_access_patterns` with workload/actor/target/path references. Observations may carry a `pattern_id`; hardware peak specifications remain capabilities. Cross-layer request transformations are graph relationships, not an assumption of identical requests or byte counts.
