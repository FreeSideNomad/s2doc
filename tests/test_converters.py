"""Tests for converters using real example files"""

import pytest
import yaml
import tempfile
import os
from pathlib import Path

from s2doc.converters.domain_stories import DomainStoryConverter
from s2doc.converters.strategic import StrategicDDDConverter
from s2doc.converters.tactical import TacticalDDDConverter


class TestDomainStoriesConverter:
    """Test domain stories converter with real example"""

    @pytest.fixture
    def example_file(self):
        """Path to domain stories example file"""
        return Path(__file__).parent.parent / "examples" / "cb-domain-stories.yaml"

    @pytest.fixture
    def output_dir(self):
        """Create temporary output directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield tmpdir

    def test_converter_initialization(self, example_file):
        """Test converter can be initialized with example file"""
        converter = DomainStoryConverter(str(example_file))
        assert converter is not None
        assert converter.stories is not None

    def test_conversion_produces_output(self, example_file, output_dir):
        """Test converter produces markdown output"""
        converter = DomainStoryConverter(str(example_file))
        output_file = os.path.join(output_dir, "output.md")

        converter.convert(output_file)

        assert os.path.exists(output_file)
        assert os.path.getsize(output_file) > 0

    def test_output_contains_expected_sections(self, example_file, output_dir):
        """Test generated markdown contains expected sections"""
        converter = DomainStoryConverter(str(example_file))
        output_file = os.path.join(output_dir, "output.md")

        converter.convert(output_file)

        with open(output_file, 'r') as f:
            content = f.read()

        # Check for expected sections
        assert "# " in content  # Has headers
        assert "```mermaid" in content  # Has diagrams
        assert "sequenceDiagram" in content or "graph" in content  # Has sequence or flow diagrams

    def test_multiple_stories_processed(self, example_file, output_dir):
        """Test that multiple stories are processed"""
        converter = DomainStoryConverter(str(example_file))

        # The cb-domain-stories example has 33 stories
        assert len(converter.stories) > 0


class TestStrategicDDDConverter:
    """Test strategic DDD converter with real example"""

    @pytest.fixture
    def example_file(self):
        """Path to strategic DDD example file"""
        return Path(__file__).parent.parent / "examples" / "payments-strategic.yaml"

    @pytest.fixture
    def example_data(self, example_file):
        """Load strategic DDD example data"""
        with open(example_file, 'r') as f:
            return yaml.safe_load(f)

    def test_converter_initialization(self, example_data):
        """Test converter can be initialized with example data"""
        converter = StrategicDDDConverter(example_data)
        assert converter is not None
        assert converter.system is not None

    def test_conversion_produces_markdown(self, example_data):
        """Test converter produces markdown output"""
        converter = StrategicDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert markdown is not None
        assert len(markdown) > 0
        assert isinstance(markdown, str)

    def test_output_contains_system_info(self, example_data):
        """Test output contains system information"""
        converter = StrategicDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for system name
        assert "Payment Platform" in markdown or "System" in markdown

        # Check for domains
        assert "Domain" in markdown

        # Check for bounded contexts
        assert "Bounded Context" in markdown or "Context" in markdown

    def test_output_contains_diagrams(self, example_data):
        """Test output contains Mermaid diagrams"""
        converter = StrategicDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert "```mermaid" in markdown
        assert "graph" in markdown

    def test_output_contains_context_mappings(self, example_data):
        """Test output contains context mapping information"""
        converter = StrategicDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for context mapping section
        assert "Context Mapping" in markdown or "Relationship" in markdown


class TestTacticalDDDConverter:
    """Test tactical DDD converter with real example"""

    @pytest.fixture
    def example_file(self):
        """Path to tactical DDD example file"""
        return Path(__file__).parent.parent / "examples" / "payments-tactical.yaml"

    @pytest.fixture
    def example_data(self, example_file):
        """Load tactical DDD example data"""
        with open(example_file, 'r') as f:
            return yaml.safe_load(f)

    def test_converter_initialization(self, example_data):
        """Test converter can be initialized with example data"""
        converter = TacticalDDDConverter(example_data)
        assert converter is not None
        assert converter.bounded_context is not None

    def test_conversion_produces_markdown(self, example_data):
        """Test converter produces markdown output"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert markdown is not None
        assert len(markdown) > 0
        assert isinstance(markdown, str)

    def test_output_contains_bounded_context_info(self, example_data):
        """Test output contains bounded context information"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for bounded context name
        assert "Payment Scheduling" in markdown or "Context" in markdown

        # Check for context ID
        assert "bc_payment_scheduling" in markdown

    def test_output_contains_aggregates(self, example_data):
        """Test output contains aggregate information"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert "Aggregate" in markdown
        assert "```mermaid" in markdown
        assert "classDiagram" in markdown

    def test_output_contains_services(self, example_data):
        """Test output contains service information"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for service sections
        assert "Application Service" in markdown or "Domain Service" in markdown

    def test_output_contains_value_objects(self, example_data):
        """Test output contains value object information"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert "Value Object" in markdown

    def test_output_contains_repositories(self, example_data):
        """Test output contains repository information"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        assert "Repository" in markdown or "Repositories" in markdown

    def test_humanized_entity_names(self, example_data):
        """Test that entity names are humanized"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for humanized names (spaces in entity names)
        assert "Payment Template" in markdown  # Not "PaymentTemplate"
        assert "Scheduled Payment" in markdown  # Not "ScheduledPayment"

    def test_summary_tables_present(self, example_data):
        """Test that summary tables are present"""
        converter = TacticalDDDConverter(example_data)
        markdown = converter.convert_to_markdown()

        # Check for table headers
        assert "| Name | Description |" in markdown

        # Check for specific table sections
        assert "## Application Services" in markdown
        assert "## Domain Services" in markdown
        assert "## Aggregates" in markdown
        assert "## Repositories" in markdown
