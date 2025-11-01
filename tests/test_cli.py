"""Tests for CLI interface using real example files"""

import pytest
import tempfile
import os
from pathlib import Path
from unittest.mock import patch
import sys

from s2doc.cli import main


class TestCLI:
    """Test CLI interface with real example files"""

    @pytest.fixture
    def examples_dir(self):
        """Path to examples directory"""
        return Path(__file__).parent.parent / "examples"

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_cli_version(self):
        """Test --version flag"""
        with patch('sys.argv', ['s2doc', '--version']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_help(self):
        """Test --help flag"""
        with patch('sys.argv', ['s2doc', '--help']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 0

    def test_cli_missing_input_file(self):
        """Test error when input file doesn't exist"""
        with patch('sys.argv', ['s2doc', 'nonexistent.yaml']):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 4  # File I/O error

    def test_cli_tactical_conversion(self, examples_dir, output_dir):
        """Test CLI with tactical DDD example"""
        input_file = str(examples_dir / "payments-tactical.yaml")
        output_file = os.path.join(output_dir, "bc_payment_scheduling.md")

        with patch('sys.argv', ['s2doc', input_file, '-o', output_dir]):
            main()

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_cli_strategic_conversion(self, examples_dir, output_dir):
        """Test CLI with strategic DDD example"""
        input_file = str(examples_dir / "payments-strategic.yaml")
        output_file = os.path.join(output_dir, "payments-strategic.md")

        with patch('sys.argv', ['s2doc', input_file, '-o', output_dir]):
            main()

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_cli_domain_stories_conversion(self, examples_dir, output_dir):
        """Test CLI with domain stories example"""
        input_file = str(examples_dir / "cb-domain-stories.yaml")
        output_file = os.path.join(output_dir, "cb-domain-stories.md")

        with patch('sys.argv', ['s2doc', input_file, '-o', output_dir]):
            main()

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_cli_verbose_mode(self, examples_dir, output_dir, capsys):
        """Test CLI verbose mode"""
        input_file = str(examples_dir / "payments-tactical.yaml")

        with patch('sys.argv', ['s2doc', input_file, '-o', output_dir, '-v']):
            main()

        captured = capsys.readouterr()
        assert "Detected schema" in captured.out
        assert "Tactical DDD" in captured.out

    def test_cli_invalid_yaml(self, output_dir):
        """Test CLI with invalid YAML file"""
        # Create invalid YAML file
        invalid_file = os.path.join(output_dir, "invalid.yaml")
        with open(invalid_file, 'w') as f:
            f.write("invalid: yaml: syntax:")

        with patch('sys.argv', ['s2doc', invalid_file]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 1  # YAML parsing error

    def test_cli_unknown_schema(self, output_dir):
        """Test CLI with unknown schema"""
        # Create YAML file with unknown schema
        unknown_file = os.path.join(output_dir, "unknown.yaml")
        with open(unknown_file, 'w') as f:
            f.write("unknown_key: value\n")

        with patch('sys.argv', ['s2doc', unknown_file]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            assert exc_info.value.code == 2  # Schema detection failed

    def test_cli_default_output_directory(self, examples_dir):
        """Test CLI with default output directory (current directory)"""
        input_file = str(examples_dir / "payments-tactical.yaml")
        expected_output = "bc_payment_scheduling.md"

        try:
            # Clean up if file exists
            if os.path.exists(expected_output):
                os.remove(expected_output)

            with patch('sys.argv', ['s2doc', input_file]):
                main()

            assert os.path.exists(expected_output)
            assert os.path.getsize(expected_output) > 0

        finally:
            # Clean up
            if os.path.exists(expected_output):
                os.remove(expected_output)

    def test_cli_output_messages(self, examples_dir, output_dir, capsys):
        """Test CLI output messages"""
        input_file = str(examples_dir / "payments-tactical.yaml")

        with patch('sys.argv', ['s2doc', input_file, '-o', output_dir]):
            main()

        captured = capsys.readouterr()
        assert "✓ Generated" in captured.out
        assert "bc_payment_scheduling.md" in captured.out


class TestCLIErrorHandling:
    """Test CLI error handling"""

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_invalid_output_directory_permissions(self, examples_dir):
        """Test error when output directory cannot be created"""
        input_file = str(examples_dir / "examples/payments-tactical.yaml")
        # Try to create output in a directory that doesn't exist and can't be created
        invalid_output = "/root/cannot_create_this/output"

        with patch('sys.argv', ['s2doc', input_file, '-o', invalid_output]):
            # This should fail gracefully
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Should exit with file I/O error code
            assert exc_info.value.code in [3, 4]

    def test_empty_input_file(self, output_dir):
        """Test with empty input file"""
        empty_file = os.path.join(output_dir, "empty.yaml")
        with open(empty_file, 'w') as f:
            f.write("")

        with patch('sys.argv', ['s2doc', empty_file]):
            with pytest.raises(SystemExit) as exc_info:
                main()
            # Should fail with unknown schema
            assert exc_info.value.code == 2
