"""Strategic DDD YAML to Markdown Converter

This package converts Strategic DDD YAML files into comprehensive Markdown documentation.
"""

from .converter import StrategicDDDConverter
from .models import EntityResolver

__version__ = "1.0.0"
__all__ = ["StrategicDDDConverter", "EntityResolver"]
