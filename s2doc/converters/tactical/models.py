"""Data models and helper utilities for Tactical DDD converter"""

from typing import Dict, List, Optional


class EntityResolver:
    """Resolve entity references within bounded context"""

    def __init__(self, bounded_context: dict):
        self.bounded_context = bounded_context
        self.entities_by_id = {e['id']: e for e in bounded_context.get('entities', [])}
        self.value_objects_by_id = {vo['id']: vo for vo in bounded_context.get('value_objects', [])}
        self.aggregates_by_id = {agg['id']: agg for agg in bounded_context.get('aggregates', [])}
        self.repositories_by_id = {repo['id']: repo for repo in bounded_context.get('repositories', [])}
        self.domain_services_by_id = {ds['id']: ds for ds in bounded_context.get('domain_services', [])}
        self.app_services_by_id = {aps['id']: aps for aps in bounded_context.get('application_services', [])}
        self.domain_events_by_id = {de['id']: de for de in bounded_context.get('domain_events', [])}
        self.command_interfaces_by_id = {ci['id']: ci for ci in bounded_context.get('command_interfaces', [])}
        self.query_interfaces_by_id = {qi['id']: qi for qi in bounded_context.get('query_interfaces', [])}

    def get_entity(self, entity_id: str) -> Optional[dict]:
        """Get entity by ID"""
        return self.entities_by_id.get(entity_id)

    def get_value_object(self, vo_id: str) -> Optional[dict]:
        """Get value object by ID"""
        return self.value_objects_by_id.get(vo_id)

    def get_aggregate(self, agg_id: str) -> Optional[dict]:
        """Get aggregate by ID"""
        return self.aggregates_by_id.get(agg_id)

    def get_repository(self, repo_id: str) -> Optional[dict]:
        """Get repository by ID"""
        return self.repositories_by_id.get(repo_id)

    def get_domain_service(self, svc_id: str) -> Optional[dict]:
        """Get domain service by ID"""
        return self.domain_services_by_id.get(svc_id)

    def get_application_service(self, svc_id: str) -> Optional[dict]:
        """Get application service by ID"""
        return self.app_services_by_id.get(svc_id)

    def get_domain_event(self, event_id: str) -> Optional[dict]:
        """Get domain event by ID"""
        return self.domain_events_by_id.get(event_id)

    def get_command_interface(self, cmd_id: str) -> Optional[dict]:
        """Get command interface by ID"""
        return self.command_interfaces_by_id.get(cmd_id)

    def get_query_interface(self, qry_id: str) -> Optional[dict]:
        """Get query interface by ID"""
        return self.query_interfaces_by_id.get(qry_id)

    def get_entities_for_aggregate(self, agg_id: str) -> List[dict]:
        """Get all entities in an aggregate"""
        aggregate = self.get_aggregate(agg_id)
        if not aggregate:
            return []
        entity_ids = aggregate.get('entities', [])
        return [self.entities_by_id[eid] for eid in entity_ids if eid in self.entities_by_id]

    def get_value_objects_for_aggregate(self, agg_id: str) -> List[dict]:
        """Get all value objects used by an aggregate"""
        aggregate = self.get_aggregate(agg_id)
        if not aggregate:
            return []
        vo_ids = aggregate.get('value_objects', [])
        return [self.value_objects_by_id[void] for void in vo_ids if void in self.value_objects_by_id]


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


def humanize_name(name: str) -> str:
    """
    Convert PascalCase or camelCase names to human-readable format.
    Examples:
        PaymentTemplate -> Payment Template
        ScheduledPayment -> Scheduled Payment
        WorkingDayCalculationService -> Working Day Calculation Service
        PaymentTemplateId -> Payment Template Id

    If the name already contains spaces, return it as-is.
    """
    if not name:
        return ""

    # If the name already contains spaces, it's already human-readable
    if ' ' in name:
        return name

    # Insert space before uppercase letters (except at the start)
    result = []
    for i, char in enumerate(name):
        if i > 0 and char.isupper():
            # Check if previous character is lowercase or if next character is lowercase
            # This handles acronyms better (e.g., "XMLParser" -> "XML Parser")
            prev_is_lower = name[i-1].islower()
            next_is_lower = i < len(name) - 1 and name[i+1].islower()

            if prev_is_lower or next_is_lower:
                result.append(' ')
        result.append(char)

    return ''.join(result)
