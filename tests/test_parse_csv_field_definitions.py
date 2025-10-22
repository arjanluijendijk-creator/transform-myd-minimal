"""Tests for parse_csv_field_definitions function."""

import tempfile
from pathlib import Path

from transform_myd_minimal.main import parse_csv_field_definitions


def test_parse_csv_field_definitions_basic():
    """Test basic CSV parsing with all columns."""
    # Create a temporary CSV file with test data
    csv_content = """table name,field name,data type,field text,length,is key,# of occ,from total
TEST_TABLE,FIELD1,Character,First Field Description,000010,X,N/a,50
TEST_TABLE,FIELD2,Numeric,Second Field Description,005,,100,100
TEST_TABLE,FIELD3,Date,Third Field Description,8,,,100
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        # Parse the CSV
        result = parse_csv_field_definitions(csv_path)

        # Assertions
        assert len(result) == 3

        # Check FIELD1
        field1 = result[0]
        assert field1['field_name'] == 'FIELD1'
        assert field1['field_description'] == 'First Field Description'
        assert field1['dtype'] == 'Character'
        assert field1['field_count'] == 1
        assert field1['length'] == 10
        assert field1['is_key'] is True
        assert field1['nullable'] is False  # Key fields are not nullable

        # Check FIELD2
        field2 = result[1]
        assert field2['field_name'] == 'FIELD2'
        assert field2['field_description'] == 'Second Field Description'
        assert field2['dtype'] == 'Numeric'
        assert field2['field_count'] == 2
        assert field2['length'] == 5
        assert field2.get('is_key') is None
        assert field2['nullable'] is True

        # Check FIELD3
        field3 = result[2]
        assert field3['field_name'] == 'FIELD3'
        assert field3['field_description'] == 'Third Field Description'
        assert field3['dtype'] == 'Date'
        assert field3['field_count'] == 3
        assert field3['length'] == 8

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_empty_field_text():
    """Test CSV parsing when field text is empty."""
    csv_content = """table name,field name,data type,field text,length,is key,# of occ,from total
TEST_TABLE,FIELD1,Character,,000010,X,N/a,50
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)

        assert len(result) == 1
        field1 = result[0]
        assert field1['field_name'] == 'FIELD1'
        # When field_text is empty, description should be None
        assert field1['field_description'] is None
        assert field1['dtype'] == 'Character'

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_empty_data_type():
    """Test CSV parsing when data type is empty."""
    csv_content = """table name,field name,data type,field text,length,is key,# of occ,from total
TEST_TABLE,FIELD1,,Field Description,000010,X,N/a,50
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)

        assert len(result) == 1
        field1 = result[0]
        assert field1['field_name'] == 'FIELD1'
        assert field1['field_description'] == 'Field Description'
        # When data_type is empty, dtype should fallback to 'string'
        assert field1['dtype'] == 'string'

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_missing_columns():
    """Test CSV parsing with missing columns."""
    # Minimal CSV with only field name
    csv_content = """field name
FIELD1
FIELD2
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)

        assert len(result) == 2
        field1 = result[0]
        assert field1['field_name'] == 'FIELD1'
        assert field1['field_description'] is None
        assert field1['dtype'] == 'string'  # Default fallback

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_case_insensitive_headers():
    """Test CSV parsing with different case headers."""
    csv_content = """Table Name,Field Name,Data Type,Field Text
TEST_TABLE,FIELD1,Character,Field Description
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)

        assert len(result) == 1
        field1 = result[0]
        assert field1['field_name'] == 'FIELD1'
        assert field1['field_description'] == 'Field Description'
        assert field1['dtype'] == 'Character'

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_empty_file():
    """Test CSV parsing with empty file."""
    csv_content = """table name,field name,data type,field text,length,is key,# of occ,from total
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)
        assert len(result) == 0

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_skip_empty_rows():
    """Test CSV parsing skips empty rows."""
    csv_content = """table name,field name,data type,field text
TEST_TABLE,FIELD1,Character,Field Description

TEST_TABLE,FIELD2,Numeric,Another Description
"""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)

        assert len(result) == 2
        assert result[0]['field_name'] == 'FIELD1'
        assert result[1]['field_name'] == 'FIELD2'

    finally:
        csv_path.unlink()


def test_parse_csv_field_definitions_no_fieldnames():
    """Test CSV parsing handles missing fieldnames gracefully."""
    # Empty CSV file - no headers
    csv_content = ""

    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False, encoding='utf-8') as f:
        f.write(csv_content)
        csv_path = Path(f.name)

    try:
        result = parse_csv_field_definitions(csv_path)
        # Should return empty list without crashing
        assert len(result) == 0

    finally:
        csv_path.unlink()
