"""Behavioral checks for the common I/O contract; no host access required."""

from copy import deepcopy
import json
from pathlib import Path
import unittest

from validate_io_pattern import validate

EXAMPLE = Path(__file__).resolve().parents[1] / "references/examples/storage-pipeline.json"


class IoPatternValidationTests(unittest.TestCase):
    def setUp(self):
        self.document = json.loads(EXAMPLE.read_text(encoding="utf-8"))

    def test_cross_layer_example(self):
        self.assertEqual(validate(self.document), [])

    def test_unknown_and_external_entities_are_supported(self):
        pattern = self.document["io_access_patterns"][0]
        self.document = {
            "schema_version": "0.1", "entities": [], "relations": [],
            "external_entity_ids": [pattern[key] for key in ("workload_id", "actor_id", "target_id")],
            "io_access_patterns": [{key: pattern[key] for key in (
                "id", "workload_id", "phase", "actor_id", "target_id", "layer", "scope", "window", "evidence", "missing"
            )}]
        }
        self.document["io_access_patterns"][0]["addressing"] = {
            "space": "unknown", "pattern": "unknown", "group_by": ["unknown"]
        }
        self.assertEqual(validate(self.document), [])

    def test_invalid_inputs(self):
        def mutate(document, case):
            pattern = document["io_access_patterns"][0]
            if case == "dangling_target":
                pattern["target_id"] = "missing:device"
            elif case == "duplicate_id":
                document["entities"].append(deepcopy(document["entities"][0]))
            elif case == "percentage_instead_of_ratio":
                pattern["operation_mix"]["fractions"]["read"] = 100
            elif case == "incomplete_mix":
                pattern["operation_mix"]["fractions"]["read"] = 0.8
            elif case == "wrong_size_unit":
                pattern["request_size"][0]["distribution"]["unit"] = "us"
            elif case == "reversed_percentiles":
                pattern["request_size"][0]["distribution"]["p99"] = 1
            elif case == "mixed_distribution_shapes":
                pattern["request_size"][0]["distribution"]["value"] = 4096
            elif case == "reversed_window":
                pattern["window"]["end"] = "2026-10-17T00:00:00Z"
            elif case == "invalid_datetime":
                pattern["window"]["start"] = "not-a-date"
            elif case == "timezone_missing":
                pattern["window"]["start"] = "2026-10-18T00:00:00"
            elif case == "unknown_pattern_reference":
                document["observations"][0]["pattern_id"] = "missing:pattern"
            elif case == "histogram_counts":
                document["io_access_patterns"][1]["request_size"][0]["distribution"]["sample_count"] = 501
            elif case == "histogram_overlap":
                document["io_access_patterns"][1]["request_size"][0]["distribution"]["bins"][1]["lower"] = 4096
            elif case == "missing_lba_unit":
                del document["io_access_patterns"][1]["addressing"]["address_unit_bytes"]
            elif case == "missing_stride":
                pattern["addressing"]["pattern"] = "strided"
            elif case == "hot_set_exceeds_working_set":
                pattern["locality"] = {"hot_set_bytes": 100, "working_set_bytes": 50}
            elif case == "unscoped_cache_ratio":
                pattern["semantics"]["cache_hit_ratio"] = 0.5
            elif case == "bad_evidence_pointer":
                pattern["field_evidence"] = {"/nonexistent": deepcopy(pattern["evidence"])}

        for case in (
            "dangling_target", "duplicate_id", "percentage_instead_of_ratio", "incomplete_mix",
            "wrong_size_unit", "reversed_percentiles", "mixed_distribution_shapes", "reversed_window",
            "invalid_datetime", "timezone_missing", "unknown_pattern_reference", "histogram_counts",
            "histogram_overlap", "missing_lba_unit", "missing_stride", "hot_set_exceeds_working_set",
            "unscoped_cache_ratio", "bad_evidence_pointer"
        ):
            with self.subTest(case=case):
                document = deepcopy(self.document)
                mutate(document, case)
                self.assertTrue(validate(document), f"Invalid case was accepted: {case}")

    def test_field_provenance_can_override_configured_depth(self):
        pattern = self.document["io_access_patterns"][0]
        pattern["concurrency"]["configured_depth"] = 8
        evidence = deepcopy(pattern["evidence"])
        evidence["basis"] = "declared"
        pattern["field_evidence"] = {"/concurrency/configured_depth": evidence}
        self.assertEqual(validate(self.document), [])


if __name__ == "__main__":
    unittest.main()
