"""
Domain Stories Toolkit

A Python toolkit for converting Domain Stories YAML models into
structured Markdown documentation with Mermaid diagrams and Word documents for review.
"""

__version__ = "1.0.0"
__author__ = "Igor Music"

from .converter import DomainStoryConverter
from .docx_converter import convert_md_to_docx
from .comment_extractor import extract_comments_to_yaml

__all__ = [
    "DomainStoryConverter",
    "convert_md_to_docx",
    "extract_comments_to_yaml",
]
