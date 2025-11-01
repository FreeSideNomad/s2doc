"""Data models and helper utilities for Strategic DDD converter"""

from typing import Dict, List, Optional


class EntityResolver:
    """Resolve entity references to full objects"""

    def __init__(self, system: dict):
        self.system = system
        self.domains_by_id = {d['id']: d for d in system.get('domains', [])}
        self.contexts_by_id = {bc['id']: bc for bc in system.get('bounded_contexts', [])}
        self.bff_scopes_by_id = {bff['id']: bff for bff in system.get('bff_scopes', [])}
        self.bff_interfaces_by_id = {bff_if['id']: bff_if for bff_if in system.get('bff_interfaces', [])}
        self.context_mappings_by_id = {cm['id']: cm for cm in system.get('context_mappings', [])}

    def get_domain(self, domain_id: str) -> Optional[dict]:
        """Get domain by ID"""
        return self.domains_by_id.get(domain_id)

    def get_context(self, context_id: str) -> Optional[dict]:
        """Get bounded context by ID"""
        return self.contexts_by_id.get(context_id)

    def get_bff_scope(self, bff_id: str) -> Optional[dict]:
        """Get BFF scope by ID"""
        return self.bff_scopes_by_id.get(bff_id)

    def get_contexts_for_domain(self, domain_id: str) -> List[dict]:
        """Get all bounded contexts for a domain"""
        domain = self.get_domain(domain_id)
        if not domain:
            return []
        context_ids = domain.get('bounded_contexts', [])
        return [self.contexts_by_id[bc_id] for bc_id in context_ids if bc_id in self.contexts_by_id]


def generate_anchor(entity_id: str) -> str:
    """Generate markdown anchor from entity ID"""
    return f'<a id="{entity_id}"></a>'


def generate_link(entity_id: str, display_text: str = None) -> str:
    """Generate markdown link to entity"""
    text = display_text or entity_id
    return f'[{text}](#{entity_id})'


def format_boolean(value: bool) -> str:
    """Format boolean as checkmark or X"""
    return "✓" if value else "✗"


def generate_table(headers: List[str], rows: List[List[str]]) -> str:
    """Generate markdown table"""
    if not rows:
        return ""

    # Header row
    header_row = "| " + " | ".join(headers) + " |"

    # Separator row
    separator = "| " + " | ".join(["---"] * len(headers)) + " |"

    # Data rows
    data_rows = []
    for row in rows:
        data_rows.append("| " + " | ".join(str(cell) for cell in row) + " |")

    return "\n".join([header_row, separator] + data_rows)


def escape_markdown(text: str) -> str:
    """Escape special characters in markdown"""
    if not text:
        return ""
    # Escape pipe characters in table cells
    return text.replace("|", "\\|")


def safe_get(obj: dict, key: str, default: str = "") -> str:
    """Safely get value from dict with default"""
    value = obj.get(key, default)
    return str(value) if value is not None else default


def humanize_relationship_type(rel_type: str) -> str:
    """Convert relationship type from snake_case to human-readable format"""
    if not rel_type:
        return ""

    # Special cases
    special_cases = {
        "acl": "ACL",
        "api": "API"
    }

    # Split by underscore and capitalize each word
    words = rel_type.split('_')
    humanized = []

    for word in words:
        if word.upper() in special_cases.values():
            humanized.append(word.upper())
        elif word in special_cases:
            humanized.append(special_cases[word])
        else:
            humanized.append(word.capitalize())

    return " ".join(humanized)
