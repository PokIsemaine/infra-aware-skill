# Infra Aware Linux

A Claude/Codex-compatible plugin registry for Linux-first infrastructure-aware code analysis and optimization.

The plugin treats hardware specifications, Linux and Kubernetes execution paths, and observability tools as composable evidence sources. The registry is layered as hardware, kernel, platform, external services, and workload. Its routing skill is [`skills/linux-infra-awareness`](skills/linux-infra-awareness); the initial atomic hardware skills cover GPUs, network topology, storage, and host interconnects.

## Layout

- `.codex-plugin/plugin.json`: Codex plugin manifest
- `.claude-plugin/plugin.json`: Claude plugin manifest
- `marketplace.json`: local registry entry
- `skills/`: discoverable skills
- `skills/linux-infra-awareness/references/`: progressively loaded Linux evidence and modeling guidance
- `skills/hardware-*/`: atomic hardware evidence skills
- `skills/access-pattern-analysis/`: cross-layer I/O access-pattern skill, JSON Schema, validator, and synthetic examples
- `docs/architecture.md`: layer boundaries and registry naming rules

## Local use

Install or link this repository as a plugin according to the host's registry mechanism, then invoke `$linux-infra-awareness` for Linux-dependent performance analysis.

For workload I/O behavior, use [`$access-pattern-analysis`](skills/access-pattern-analysis/SKILL.md). Its [model contract](skills/access-pattern-analysis/references/model.md) connects access shape, locality, concurrency, cache/durability semantics, and evidence windows to the existing infrastructure graph.
