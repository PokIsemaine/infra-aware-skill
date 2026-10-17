#!/usr/bin/env python3
"""Validate an I/O pattern snapshot and its cross-record invariants."""

import argparse
from datetime import datetime
import json
import math
from pathlib import Path
import sys

from jsonschema import Draft202012Validator, FormatChecker
from rfc3339_validator import validate_rfc3339

SCHEMA_PATH = Path(__file__).resolve().parents[1] / "references/io-access-pattern.schema.json"
FORMAT_CHECKER = FormatChecker()


@FORMAT_CHECKER.checks("date-time")
def valid_datetime(value):
    return not isinstance(value, str) or bool(validate_rfc3339(value.upper()))


def semantic_errors(document):
    """Run after JSON Schema validation so structural assumptions are safe."""
    entities = [entity["id"] for entity in document["entities"]]
    patterns = [pattern["id"] for pattern in document["io_access_patterns"]]
    relations = [relation["id"] for relation in document["relations"]]
    external = document.get("external_entity_ids", [])
    all_ids = entities + patterns + relations + external
    if len(all_ids) != len(set(all_ids)):
        yield "IDs must be unique across entities, patterns, relations, and external references"
    entity_ids = set(entities + external)
    endpoint_ids = entity_ids | set(patterns)
    subject_ids = endpoint_ids | set(relations)

    def reference(value, allowed, location):
        if value not in allowed:
            return f"{location}: unresolved reference {value!r}"
        return None

    for relation in document["relations"]:
        for key in ("source", "target"):
            error = reference(relation[key], endpoint_ids, f"{relation['id']}.{key}")
            if error:
                yield error
    for pattern in document["io_access_patterns"]:
        for key in ("workload_id", "actor_id", "source_id", "target_id"):
            if key in pattern:
                error = reference(pattern[key], entity_ids, f"{pattern['id']}.{key}")
                if error:
                    yield error
        path = pattern.get("path_entity_ids", [])
        cache = pattern.get("semantics", {}).get("cache_layer_id")
        for value in path + ([cache] if cache else []):
            error = reference(value, entity_ids, pattern["id"])
            if error:
                yield error
        if "operation_mix" in pattern:
            total = sum(pattern["operation_mix"]["fractions"].values())
            if not math.isclose(total, 1.0, rel_tol=0, abs_tol=1e-6):
                yield f"{pattern['id']}: operation fractions must sum to 1, got {total}"
        size_ops = [item["operation"] for item in pattern.get("request_size", [])]
        if len(size_ops) != len(set(size_ops)):
            yield f"{pattern['id']}: duplicate request_size operation; split the pattern instead"
        locality = pattern.get("locality", {})
        if locality.get("hot_set_bytes", 0) > locality.get("working_set_bytes", float("inf")):
            yield f"{pattern['id']}: hot set exceeds working set"
        for pointer in pattern.get("field_evidence", {}):
            try:
                if not pointer.startswith("/"):
                    raise KeyError(pointer)
                current = pattern
                for part in pointer[1:].split("/"):
                    part = part.replace("~1", "/").replace("~0", "~")
                    current = current[int(part)] if isinstance(current, list) else current[part]
            except (KeyError, IndexError, ValueError, TypeError):
                yield f"{pattern['id']}: field_evidence pointer does not resolve: {pointer}"

    for observation in document.get("observations", []):
        error = reference(observation["subject"], subject_ids, "observation.subject")
        if error:
            yield error
        if "pattern_id" in observation:
            error = reference(observation["pattern_id"], set(patterns), "observation.pattern_id")
            if error:
                yield error
    for capability in document.get("capabilities", []):
        error = reference(capability["subject"], subject_ids, "capability.subject")
        if error:
            yield error

    def walk(value, location="$"):
        if isinstance(value, list):
            for index, item in enumerate(value):
                yield from walk(item, f"{location}[{index}]")
        elif isinstance(value, dict):
            if "start" in value and "end" in value:
                start = datetime.fromisoformat(value["start"].upper().replace("Z", "+00:00"))
                end = datetime.fromisoformat(value["end"].upper().replace("Z", "+00:00"))
                if end <= start:
                    yield f"{location}: window end must be after start"
                if value.get("sampling_interval_ms", 0) > (end - start).total_seconds() * 1000:
                    yield f"{location}: sampling interval exceeds window"
            if value.get("kind") == "percentiles":
                points = [value[key] for key in ("p50", "p95", "p99") if key in value]
                if points != sorted(points):
                    yield f"{location}: percentiles must be nondecreasing"
            if value.get("kind") == "histogram":
                previous_upper = None
                for item in value["bins"]:
                    if item["upper"] <= item["lower"]:
                        yield f"{location}: histogram upper must exceed lower"
                    if previous_upper is not None and item["lower"] < previous_upper:
                        yield f"{location}: histogram bins must be ordered and nonoverlapping"
                    previous_upper = item["upper"]
                if sum(item["count"] for item in value["bins"]) != value["sample_count"]:
                    yield f"{location}: histogram counts must sum to sample_count"
            for key, item in value.items():
                yield from walk(item, f"{location}.{key}")

    for pattern in document["io_access_patterns"]:
        yield from walk(pattern, pattern["id"])
    for index, observation in enumerate(document.get("observations", [])):
        yield from walk(observation["window"], f"observations[{index}].window")


def validate(document):
    schema = json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))
    Draft202012Validator.check_schema(schema)
    validator = Draft202012Validator(schema, format_checker=FORMAT_CHECKER)
    errors = [f"{error.json_path}: {error.message}" for error in validator.iter_errors(document)]
    if errors:
        return errors
    return list(semantic_errors(document))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("snapshots", nargs="+", type=Path)
    args = parser.parse_args()
    failed = False
    for path in args.snapshots:
        try:
            def reject_constant(value):
                raise ValueError(f"Non-finite JSON number: {value}")
            document = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject_constant)
            errors = validate(document)
        except (OSError, ValueError) as error:
            errors = [str(error)]
        if errors:
            failed = True
            print(f"FAIL {path}", file=sys.stderr)
            for error in errors:
                print(f"  {error}", file=sys.stderr)
        else:
            print(f"OK {path}")
    return int(failed)


if __name__ == "__main__":
    sys.exit(main())
