#!/usr/bin/env python3
"""
Tests for transform command error handling.
"""

import subprocess
import sys
import tempfile
from pathlib import Path


def test_transform_missing_template_error():
    """Test that transform command exits with error when template file is missing."""
    # Set up a temporary directory structure
    with tempfile.TemporaryDirectory() as tmpdir:
        tmppath = Path(tmpdir)

        # Create minimal required directory structure
        (tmppath / "data" / "07_raw").mkdir(parents=True, exist_ok=True)
        (tmppath / "data" / "06_template").mkdir(parents=True, exist_ok=True)
        (tmppath / "migrations" / "test_obj" / "test_var").mkdir(parents=True, exist_ok=True)

        # Create a dummy raw data file
        import pandas as pd
        raw_df = pd.DataFrame({"col1": ["val1"], "col2": ["val2"]})
        raw_file = tmppath / "data" / "07_raw" / "test_obj_test_var.xlsx"
        raw_df.to_excel(raw_file, index=False)

        # Create dummy mapping file
        import yaml
        mapping_data = {
            "metadata": {
                "object": "test_obj",
                "variant": "test_var",
                "generated_at": "2025-01-01T00:00:00.000000",
                "source_index": "migrations/test_obj/test_var/index_source.yaml",
                "target_index": "migrations/test_obj/test_var/index_target.yaml",
                "mapped_count": 0,
                "unmapped_count": 1,
                "to_audit": 0,
                "unused_sources": 0,
                "unused_targets": 1
            },
            "mappings": []
        }
        mapping_file = tmppath / "migrations" / "test_obj" / "test_var" / "mapping.yaml"
        with open(mapping_file, "w") as f:
            yaml.dump(mapping_data, f)

        # Create dummy target index file
        target_data = {
            "metadata": {
                "object": "test_obj",
                "variant": "test_var",
                "target_file": "data/02_target/test_obj_test_var.xml",
                "generated_at": "2025-01-01T00:00:00.000000",
                "structure": "S_TEST_VAR",
                "target_fields_count": 1
            },
            "target_fields": [
                {
                    "target_field": "FIELD1",
                    "target_field_name": "FIELD1",
                    "target_field_description": "Test Field 1",
                    "target_table": "test_var",
                    "target_is_mandatory": True,
                    "target_field_group": "key",
                    "target_is_key": True,
                    "target_sheet_name": "Field List",
                    "target_data_type": "Text",
                    "target_length": 10,
                    "target_decimal": None,
                    "target_field_count": 1
                }
            ]
        }
        target_file = tmppath / "migrations" / "test_obj" / "test_var" / "index_target.yaml"
        with open(target_file, "w") as f:
            yaml.dump(target_data, f)

        # NOTE: We deliberately DO NOT create a template file
        # Template should be at: data/06_template/S_TEST_VAR#*.csv

        # Run transform command
        result = subprocess.run(
            [
                sys.executable,
                "-m",
                "transform_myd_minimal",
                "transform",
                "--object", "test_obj",
                "--variant", "test_var",
                "--root", str(tmppath),
            ],
            capture_output=True,
            text=True,
        )

        # Should exit with error code 6 (missing template)
        assert result.returncode == 6, f"Expected exit code 6, got {result.returncode}. stderr: {result.stderr}"

        # Should contain error message about missing template
        combined_output = result.stdout + result.stderr
        assert "missing_template" in combined_output.lower() or "template" in combined_output.lower(), \
            f"Expected error message about missing template. Output: {combined_output}"


if __name__ == "__main__":
    print("Running transform error tests...")
    test_transform_missing_template_error()
    print("✓ All transform error tests passed!")
