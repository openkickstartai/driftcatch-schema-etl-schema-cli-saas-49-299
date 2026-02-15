"""Tests for DriftCatch core engine — 9 test cases."""
import json
import pytest
from driftcatch import (
    snapshot_csv, snapshot_json, diff_schemas,
    has_breaking, format_report, save_snapshot, load_snapshot,
)


@pytest.fixture
def csv_file(tmp_path):
    p = tmp_path / "data.csv"
    p.write_text("id,name,email\n1,Alice,a@b.com\n2,Bob,b@c.com\n")
    return str(p)


@pytest.fixture
def json_file(tmp_path):
    p = tmp_path / "data.json"
    p.write_text(json.dumps([{"id": 1, "name": "Alice", "active": True}]))
    return str(p)


def test_snapshot_csv_columns_and_types(csv_file):
    snap = snapshot_csv(csv_file)
    assert set(snap["columns"].keys()) == {"id", "name", "email"}
    assert snap["columns"]["id"]["type"] == "int"
    assert snap["columns"]["name"]["type"] == "str"


def test_snapshot_json_columns_and_types(json_file):
    snap = snapshot_json(json_file)
    assert snap["columns"]["id"]["type"] == "int"
    assert snap["columns"]["active"]["type"] == "bool"
    assert "captured_at" in snap


def test_diff_detects_removed_column():
    old = {"columns": {"id": {"type": "int", "nullable": False},
                       "name": {"type": "str", "nullable": False}}}
    new = {"columns": {"id": {"type": "int", "nullable": False}}}
    changes = diff_schemas(old, new)
    assert len(changes) == 1
    assert changes[0]["severity"] == "BREAKING"
    assert "removed" in changes[0]["message"]


def test_diff_detects_type_change():
    old = {"columns": {"id": {"type": "int", "nullable": False}}}
    new = {"columns": {"id": {"type": "str", "nullable": False}}}
    changes = diff_schemas(old, new)
    assert has_breaking(changes)
    assert "type" in changes[0]["message"]


def test_diff_detects_added_column_as_info():
    old = {"columns": {"id": {"type": "int", "nullable": False}}}
    new = {"columns": {"id": {"type": "int", "nullable": False},
                       "email": {"type": "str", "nullable": True}}}
    changes = diff_schemas(old, new)
    assert len(changes) == 1
    assert changes[0]["severity"] == "INFO"


def test_nullable_to_non_nullable_is_breaking():
    old = {"columns": {"id": {"type": "int", "nullable": True}}}
    new = {"columns": {"id": {"type": "int", "nullable": False}}}
    changes = diff_schemas(old, new)
    assert has_breaking(changes)
    assert "non-nullable" in changes[0]["message"]


def test_non_nullable_to_nullable_is_warning():
    old = {"columns": {"id": {"type": "int", "nullable": False}}}
    new = {"columns": {"id": {"type": "int", "nullable": True}}}
    changes = diff_schemas(old, new)
    assert not has_breaking(changes)
    assert changes[0]["severity"] == "WARNING"


def test_identical_schemas_no_changes():
    schema = {"columns": {"id": {"type": "int", "nullable": False},
                          "name": {"type": "str", "nullable": True}}}
    changes = diff_schemas(schema, schema)
    assert len(changes) == 0
    assert not has_breaking(changes)


def test_save_and_load_roundtrip(tmp_path):
    snap = {"source": "test", "captured_at": "now",
            "columns": {"x": {"type": "int", "nullable": False}}}
    path = str(tmp_path / "snap.json")
    save_snapshot(snap, path)
    loaded = load_snapshot(path)
    assert loaded == snap


def test_format_report_empty():
    assert "No schema changes" in format_report([])


def test_format_report_shows_severity():
    changes = [{"severity": "BREAKING", "column": "x",
                "message": "Column 'x' removed"}]
    report = format_report(changes)
    assert "BREAKING" in report
