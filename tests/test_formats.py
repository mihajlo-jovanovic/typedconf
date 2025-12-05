import pytest
from pathlib import Path
from typedconf.config.formats import TomlFileLoader

class TestTomlFileLoader:
    def test_load_valid_toml(self, tmp_path):
        """Test loading a valid TOML file."""
        config_file = tmp_path / "config.toml"
        config_file.write_text('key = "value"\n[section]\nfoo = 123')
        
        loader = TomlFileLoader(config_file)
        data = loader.load()
        
        assert data == {"key": "value", "section": {"foo": 123}}

    def test_required_file_missing(self, tmp_path):
        """Test that missing required file raises FileNotFoundError."""
        config_file = tmp_path / "missing.toml"
        loader = TomlFileLoader(config_file, required=True)
        
        with pytest.raises(FileNotFoundError):
            loader.load()

    def test_optional_file_missing(self, tmp_path):
        """Test that missing optional file returns empty dict."""
        config_file = tmp_path / "missing.toml"
        loader = TomlFileLoader(config_file, required=False)
        
        data = loader.load()
        assert data == {}

    def test_invalid_toml(self, tmp_path):
        """Test that invalid TOML file returns empty dict (and logs warning)."""
        config_file = tmp_path / "invalid.toml"
        config_file.write_text('key = "value" \n broken_line')
        
        loader = TomlFileLoader(config_file)
        data = loader.load()
        
        assert data == {}
