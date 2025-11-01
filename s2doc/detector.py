"""Schema detection for YAML files"""

from enum import Enum
from typing import Dict, Any


class SchemaType(Enum):
    """Supported schema types"""
    DOMAIN_STORIES = "domain_stories"
    STRATEGIC_DDD = "strategic_ddd"
    TACTICAL_DDD = "tactical_ddd"
    DATA_ENGINEERING = "data_engineering"
    UNKNOWN = "unknown"


def detect_schema_type(data: Dict[Any, Any]) -> SchemaType:
    """
    Detect which schema the YAML data conforms to.

    Args:
        data: Parsed YAML data

    Returns:
        SchemaType enum value
    """
    if not isinstance(data, dict):
        return SchemaType.UNKNOWN

    # Check $schema field first (most reliable)
    if '$schema' in data:
        schema_url = str(data['$schema']).lower()
        if 'domain-stories' in schema_url or 'domain_stories' in schema_url:
            return SchemaType.DOMAIN_STORIES
        elif 'strategic' in schema_url:
            return SchemaType.STRATEGIC_DDD
        elif 'tactical' in schema_url:
            return SchemaType.TACTICAL_DDD
        elif 'data-eng' in schema_url or 'data-engineering' in schema_url:
            return SchemaType.DATA_ENGINEERING

    # Check top-level keys for domain stories
    if 'domain_story' in data or 'domain_stories' in data or 'stories' in data:
        return SchemaType.DOMAIN_STORIES

    # Check for data engineering schema (system with pipelines and datasets)
    if 'system' in data and 'pipelines' in data and 'datasets' in data:
        system = data['system']
        if isinstance(system, dict) and 'domains' in system:
            return SchemaType.DATA_ENGINEERING

    # Check for strategic DDD schema
    if 'system' in data:
        system = data['system']
        if isinstance(system, dict):
            if 'domains' in system or 'bounded_contexts' in system:
                return SchemaType.STRATEGIC_DDD

    # Check for tactical DDD schema
    if 'bounded_context' in data:
        bc = data['bounded_context']
        if isinstance(bc, dict):
            if 'aggregates' in bc or 'entities' in bc or 'value_objects' in bc:
                return SchemaType.TACTICAL_DDD

    return SchemaType.UNKNOWN


def get_schema_description(schema_type: SchemaType) -> str:
    """
    Get human-readable description of schema type.

    Args:
        schema_type: The schema type

    Returns:
        Human-readable description
    """
    descriptions = {
        SchemaType.DOMAIN_STORIES: "Domain Stories (narrative scenarios)",
        SchemaType.STRATEGIC_DDD: "Strategic DDD (system architecture)",
        SchemaType.TACTICAL_DDD: "Tactical DDD (bounded context details)",
        SchemaType.DATA_ENGINEERING: "Data Engineering (pipeline and dataset modeling)",
        SchemaType.UNKNOWN: "Unknown schema type"
    }
    return descriptions.get(schema_type, "Unknown")


def get_error_message() -> str:
    """
    Get error message for unknown schema types.

    Returns:
        Formatted error message with guidance
    """
    return """
The file does not match any of the supported schemas:
  - Domain Stories (expects 'domain_story' or 'stories' key)
  - Strategic DDD (expects 'system' key with domains/bounded_contexts)
  - Tactical DDD (expects 'bounded_context' key with aggregates/entities)
  - Data Engineering (expects 'system', 'pipelines', and 'datasets' keys)

Please verify your YAML file structure or check the documentation.
"""
