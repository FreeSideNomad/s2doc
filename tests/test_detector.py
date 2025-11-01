"""Tests for schema detection"""

import pytest
import yaml
from pathlib import Path

from s2doc.detector import detect_schema_type, get_schema_description, SchemaType


class TestSchemaDetection:
    """Test schema type detection with real example files"""

    @pytest.fixture
    def examples_dir(self):
        """Path to examples directory"""
        return Path(__file__).parent.parent / "examples"

    @pytest.fixture
    def domain_stories_data(self, examples_dir):
        """Load domain stories example"""
        with open(examples_dir / "cb-domain-stories.yaml", 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def strategic_data(self, examples_dir):
        """Load strategic DDD example"""
        with open(examples_dir / "payments-strategic.yaml", 'r') as f:
            return yaml.safe_load(f)

    @pytest.fixture
    def tactical_data(self, examples_dir):
        """Load tactical DDD example"""
        with open(examples_dir / "payments-tactical.yaml", 'r') as f:
            return yaml.safe_load(f)

    def test_detect_domain_stories(self, domain_stories_data):
        """Test detection of domain stories schema"""
        schema_type = detect_schema_type(domain_stories_data)
        assert schema_type == SchemaType.DOMAIN_STORIES
        assert "domain_stories" in domain_stories_data

    def test_detect_strategic_ddd(self, strategic_data):
        """Test detection of strategic DDD schema"""
        schema_type = detect_schema_type(strategic_data)
        assert schema_type == SchemaType.STRATEGIC_DDD
        assert "system" in strategic_data
        assert "domains" in strategic_data["system"]

    def test_detect_tactical_ddd(self, tactical_data):
        """Test detection of tactical DDD schema"""
        schema_type = detect_schema_type(tactical_data)
        assert schema_type == SchemaType.TACTICAL_DDD
        assert "bounded_context" in tactical_data
        assert "aggregates" in tactical_data["bounded_context"]

    def test_schema_descriptions(self):
        """Test human-readable schema descriptions"""
        assert "Domain Stories" in get_schema_description(SchemaType.DOMAIN_STORIES)
        assert "Strategic DDD" in get_schema_description(SchemaType.STRATEGIC_DDD)
        assert "Tactical DDD" in get_schema_description(SchemaType.TACTICAL_DDD)
        assert "Unknown" in get_schema_description(SchemaType.UNKNOWN)

    def test_unknown_schema(self):
        """Test detection of unknown schema"""
        invalid_data = {"random_key": "random_value"}
        schema_type = detect_schema_type(invalid_data)
        assert schema_type == SchemaType.UNKNOWN

    def test_empty_data(self):
        """Test detection with empty data"""
        schema_type = detect_schema_type({})
        assert schema_type == SchemaType.UNKNOWN

    def test_non_dict_data(self):
        """Test detection with non-dict data"""
        schema_type = detect_schema_type("not a dict")
        assert schema_type == SchemaType.UNKNOWN

    def test_schema_field_detection(self):
        """Test detection using $schema field"""
        # Domain stories with schema field
        data = {"$schema": "domain-stories.schema.yaml", "other": "data"}
        assert detect_schema_type(data) == SchemaType.DOMAIN_STORIES

        # Strategic with schema field
        data = {"$schema": "strategic-ddd.schema.yaml", "other": "data"}
        assert detect_schema_type(data) == SchemaType.STRATEGIC_DDD

        # Tactical with schema field
        data = {"$schema": "tactical-ddd.schema.yaml", "other": "data"}
        assert detect_schema_type(data) == SchemaType.TACTICAL_DDD

    def test_all_domain_stories_keys(self):
        """Test detection with different domain stories key variations"""
        # Using 'domain_stories' key
        data = {"domain_stories": []}
        assert detect_schema_type(data) == SchemaType.DOMAIN_STORIES

        # Using 'domain_story' key
        data = {"domain_story": {}}
        assert detect_schema_type(data) == SchemaType.DOMAIN_STORIES

        # Using 'stories' key
        data = {"stories": []}
        assert detect_schema_type(data) == SchemaType.DOMAIN_STORIES
