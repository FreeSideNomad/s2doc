"""Tests for data engineering YAML to Markdown converter"""

import pytest
import os
import yaml
from pathlib import Path

from s2doc.detector import detect_schema_type, SchemaType
from s2doc.converters.data_eng import DataEngConverter


@pytest.fixture(scope="session")
def data_eng_example(examples_dir):
    """Path to data engineering example file"""
    return examples_dir / "data-eng.yaml"


@pytest.fixture(scope="session")
def data_eng_data(data_eng_example):
    """Load data engineering example data"""
    with open(data_eng_example, 'r') as f:
        docs = list(yaml.safe_load_all(f))
        return docs[-1]  # Return last document (skip frontmatter)


class TestDataEngDetection:
    """Test schema detection for data engineering YAML"""

    def test_detect_data_eng_schema(self, data_eng_data):
        """Test detection of data engineering schema"""
        schema_type = detect_schema_type(data_eng_data)
        assert schema_type == SchemaType.DATA_ENGINEERING

    def test_has_required_keys(self, data_eng_data):
        """Test that data engineering schema has required keys"""
        assert 'system' in data_eng_data
        assert 'pipelines' in data_eng_data
        assert 'datasets' in data_eng_data

    def test_system_structure(self, data_eng_data):
        """Test system structure"""
        system = data_eng_data['system']
        assert 'id' in system
        assert 'name' in system
        assert 'domains' in system
        assert system['id'].startswith('sys-')

    def test_domains_structure(self, data_eng_data):
        """Test domains structure"""
        domains = data_eng_data.get('domains', [])
        assert len(domains) > 0

        for domain in domains:
            assert 'id' in domain
            assert 'name' in domain
            assert 'pipelines' in domain
            assert domain['id'].startswith('dom-')

    def test_pipelines_structure(self, data_eng_data):
        """Test pipelines structure"""
        pipelines = data_eng_data.get('pipelines', [])
        assert len(pipelines) > 0

        for pipeline in pipelines:
            assert 'id' in pipeline
            assert 'name' in pipeline
            assert 'mode' in pipeline
            assert 'stages' in pipeline
            assert pipeline['id'].startswith('pip-')

    def test_datasets_structure(self, data_eng_data):
        """Test datasets structure"""
        datasets = data_eng_data.get('datasets', [])
        assert len(datasets) > 0

        for dataset in datasets:
            assert 'id' in dataset
            assert 'name' in dataset
            assert 'type' in dataset
            assert dataset['id'].startswith('ds-')


class TestDataEngConverter:
    """Test data engineering converter"""

    def test_converter_initialization(self, data_eng_data):
        """Test converter initializes correctly"""
        converter = DataEngConverter(data_eng_data)
        assert converter.data == data_eng_data
        assert 'id' in converter.system
        assert len(converter.domains) > 0
        assert len(converter.pipelines) > 0
        assert len(converter.datasets) > 0

    def test_conversion_generates_markdown(self, data_eng_data, tmp_path):
        """Test conversion generates markdown file"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_markdown_structure(self, data_eng_data, tmp_path):
        """Test generated markdown has expected structure"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check main sections
        assert "# ML Feature Store Platform" in content
        assert "## Table of Contents" in content
        assert "## Hierarchical Index" in content
        assert "## System Architecture" in content
        assert "## Domains" in content
        assert "## Datasets" in content
        assert "## Data Contracts" in content
        assert "## Data Quality Checks" in content
        assert "## Data Lineage" in content
        assert "## Governance" in content
        assert "## Observability" in content

    def test_mermaid_diagrams_present(self, data_eng_data, tmp_path):
        """Test that Mermaid diagrams are generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for Mermaid diagram markers
        assert "```mermaid" in content
        assert "graph TB" in content or "graph LR" in content

    def test_humanized_names(self, data_eng_data, tmp_path):
        """Test that entity names are humanized"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for humanized names (with spaces)
        assert "Feature Ingestion Domain" in content
        assert "User Events" in content
        assert "Transaction Features" in content

    def test_anchors_generated(self, data_eng_data, tmp_path):
        """Test that anchor links are generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for anchor tags
        assert '<a id="dom-feature-ingestion"></a>' in content
        assert '<a id="pip-ingest-user-events"></a>' in content
        assert '<a id="ds-user-events-raw"></a>' in content

    def test_dataset_references(self, data_eng_data, tmp_path):
        """Test that dataset references are linked"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for dataset reference links
        assert "](#ds-user-events-raw)" in content
        assert "](#ds-user-events-parsed)" in content

    def test_lineage_section(self, data_eng_data, tmp_path):
        """Test lineage section is generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check lineage content
        assert "## Data Lineage" in content
        assert "Upstream Dataset" in content
        assert "Downstream Dataset" in content
        assert "Transform" in content
        assert "Relationship" in content

    def test_governance_section(self, data_eng_data, tmp_path):
        """Test governance section is generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check governance content
        assert "## Governance" in content
        assert "Retention Policies" in content
        assert "Access Control" in content
        assert "PII Handling" in content

    def test_observability_section(self, data_eng_data, tmp_path):
        """Test observability section is generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check observability content
        assert "## Observability" in content
        assert "### Metrics" in content
        assert "### Service Level Objectives" in content
        assert "### Alerts" in content

    def test_pipeline_flow_diagrams(self, data_eng_data, tmp_path):
        """Test pipeline flow diagrams are generated"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for pipeline flow section
        assert "##### Pipeline Flow" in content

    def test_pii_information(self, data_eng_data, tmp_path):
        """Test PII information is displayed"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for PII indicators
        assert "Contains PII" in content
        assert "PII Fields" in content

    def test_schedules_displayed(self, data_eng_data, tmp_path):
        """Test pipeline schedules are displayed"""
        converter = DataEngConverter(data_eng_data)
        output_file = tmp_path / "test-output.md"

        converter.convert_to_markdown(str(output_file))

        content = output_file.read_text()

        # Check for schedule information
        assert "##### Schedule" in content
        assert "Type" in content

    def test_humanize_name_function(self):
        """Test the humanize_name function"""
        converter = DataEngConverter({'system': {}, 'pipelines': [], 'datasets': []})

        # Test PascalCase
        assert converter.humanize_name("UserEvents") == "User Events"
        assert converter.humanize_name("MLFeatureStore") == "ML Feature Store"

        # Test kebab-case
        assert converter.humanize_name("user-events") == "User Events"
        assert converter.humanize_name("ml-feature-store") == "Ml Feature Store"

        # Test already humanized
        assert converter.humanize_name("User Events") == "User Events"

        # Test edge cases
        assert converter.humanize_name("") == ""


class TestDataEngCLI:
    """Test CLI integration for data engineering"""

    def test_cli_converts_data_eng(self, data_eng_example, tmp_path):
        """Test CLI converts data engineering YAML"""
        from s2doc.cli import main
        import sys
        from unittest.mock import patch

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch('sys.argv', ['s2doc', str(data_eng_example), '-o', str(output_dir)]):
            main()

        output_file = output_dir / "data-eng.md"
        assert output_file.exists()
        assert output_file.stat().st_size > 0

    def test_cli_verbose_mode(self, data_eng_example, tmp_path, capsys):
        """Test CLI verbose mode for data engineering"""
        from s2doc.cli import main
        from unittest.mock import patch

        output_dir = tmp_path / "output"
        output_dir.mkdir()

        with patch('sys.argv', ['s2doc', str(data_eng_example), '-o', str(output_dir), '-v']):
            main()

        captured = capsys.readouterr()
        assert "Data Engineering" in captured.out
        assert "ML Feature Store Platform" in captured.out


class TestDiagramGenerator:
    """Test diagram generator"""

    def test_system_architecture_diagram(self, data_eng_data):
        """Test system architecture diagram generation"""
        from s2doc.converters.data_eng.diagram_generator import DiagramGenerator

        converter = DataEngConverter(data_eng_data)
        diagram_gen = DiagramGenerator()

        diagram = diagram_gen.generate_system_architecture(
            converter.system, converter.domains, converter.pipelines, converter.datasets
        )

        assert "```mermaid" in diagram
        assert "graph TB" in diagram
        assert "```" in diagram
        assert "subgraph Domains" in diagram
        assert "subgraph Pipelines" in diagram
        assert "subgraph Datasets" in diagram

    def test_pipeline_flow_diagram(self, data_eng_data):
        """Test pipeline flow diagram generation"""
        from s2doc.converters.data_eng.diagram_generator import DiagramGenerator

        converter = DataEngConverter(data_eng_data)
        diagram_gen = DiagramGenerator()

        # Get first pipeline
        pipeline = list(converter.pipelines.values())[0]

        diagram = diagram_gen.generate_pipeline_flow(pipeline, converter.datasets)

        assert "```mermaid" in diagram
        assert "graph LR" in diagram
        assert "```" in diagram

    def test_lineage_diagram(self, data_eng_data):
        """Test lineage diagram generation"""
        from s2doc.converters.data_eng.diagram_generator import DiagramGenerator

        converter = DataEngConverter(data_eng_data)
        diagram_gen = DiagramGenerator()

        diagram = diagram_gen.generate_lineage_diagram(converter.lineage, converter.datasets)

        assert "```mermaid" in diagram
        assert "graph LR" in diagram
        assert "```" in diagram
