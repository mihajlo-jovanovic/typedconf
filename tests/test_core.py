import pytest
from typing import Any, Mapping
from unittest.mock import MagicMock

from typedconf.config.core import deep_merge, load_sources, ConfigLoader


class TestDeepMerge:
    def test_simple_merge_overwrite(self):
        source = {"a": 1, "b": 2}
        destination = {"a": 0, "c": 3}
        result = deep_merge(source, destination)
        assert result == {"a": 1, "b": 2, "c": 3}
        assert destination == {"a": 1, "b": 2, "c": 3}  # Modifies in-place

    def test_nested_merge(self):
        source = {"nested": {"x": 10, "y": 20}}
        destination = {"nested": {"x": 5, "z": 30}, "other": "val"}
        result = deep_merge(source, destination)
        assert result == {
            "nested": {"x": 10, "y": 20, "z": 30},
            "other": "val",
        }

    def test_list_overwrite(self):
        """Lists should be overwritten, not merged."""
        source = {"items": [1, 2]}
        destination = {"items": [3, 4]}
        result = deep_merge(source, destination)
        assert result == {"items": [1, 2]}

    def test_type_mismatch_overwrite(self):
        """If types don't match (dict vs int), overwrite."""
        source = {"a": {"x": 1}}
        destination = {"a": 100}
        result = deep_merge(source, destination)
        assert result == {"a": {"x": 1}}

    def test_source_copy(self):
        """Ensure dictionaries from source are copied, not referenced."""
        source_inner = {"x": 1}
        source = {"a": source_inner}
        destination = {}
        deep_merge(source, destination)
        
        assert destination["a"] == source_inner
        assert destination["a"] is not source_inner  # Should be a copy
        
        source_inner["x"] = 2
        assert destination["a"]["x"] == 1  # Destination should remain unchanged


class MockLoader(ConfigLoader):
    def __init__(self, data: dict, should_fail: bool = False):
        self.data = data
        self.should_fail = should_fail

    def load(self) -> Mapping[str, Any]:
        if self.should_fail:
            raise Exception("Load failed")
        return self.data


class TestLoadSources:
    def test_load_single_source(self):
        loader = MockLoader({"a": 1})
        result = load_sources([loader])
        assert result == {"a": 1}

    def test_load_multiple_sources_order(self):
        """Later sources should override earlier ones."""
        loader1 = MockLoader({"a": 1, "b": 1})
        loader2 = MockLoader({"a": 2})
        result = load_sources([loader1, loader2])
        assert result == {"a": 2, "b": 1}

    def test_load_with_failure(self):
        """If a loader fails, it should be skipped (logged) and others should proceed."""
        loader1 = MockLoader({"a": 1})
        loader2 = MockLoader({}, should_fail=True)
        loader3 = MockLoader({"b": 2})
        
        result = load_sources([loader1, loader2, loader3])
        assert result == {"a": 1, "b": 2}

    def test_empty_sources(self):
        result = load_sources([])
        assert result == {}
