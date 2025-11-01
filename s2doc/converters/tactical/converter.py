"""Main converter class for Tactical DDD YAML to Markdown"""

from typing import List, Optional
from .models import (
    EntityResolver,
    generate_anchor,
    generate_link,
    format_boolean,
    generate_table,
    escape_markdown,
    safe_get,
    humanize_name
)
from .diagram_generator import AggregateUMLGenerator


class TacticalDDDConverter:
    """Convert Tactical DDD YAML to Markdown"""

    def __init__(self, yaml_data: dict):
        self.bounded_context = yaml_data['bounded_context']
        self.resolver = EntityResolver(self.bounded_context)
        self.diagram_generator = AggregateUMLGenerator(self.resolver)

    def convert_to_markdown(self) -> str:
        """Generate complete markdown document"""
        sections = [
            self._generate_header(),
            self._generate_application_services_table(),
            self._generate_domain_services_table(),
            self._generate_aggregates_table(),
            self._generate_repositories_table(),
            self._generate_aggregate_details(),
            self._generate_value_object_details(),
            self._generate_repository_details(),
            self._generate_domain_service_details(),
            self._generate_application_service_details(),
            self._generate_domain_events(),
            self._generate_command_interfaces(),
            self._generate_query_interfaces()
        ]
        return "\n\n".join(filter(None, sections))

    def _generate_header(self) -> str:
        """Generate bounded context header"""
        bc = self.bounded_context
        lines = [
            f"# {bc['name']}",
            "",
            f"**Context ID**: `{bc['id']}`",
            f"**Domain**: {bc.get('domain_ref', '')}",
            f"**Description**: {bc.get('description', '')}",
            "",
            "---"
        ]
        return "\n".join(lines)

    def _generate_application_services_table(self) -> str:
        """Generate application services summary table"""
        app_services = self.bounded_context.get('application_services', [])
        if not app_services:
            return ""

        lines = ["## Application Services", ""]

        rows = []
        for svc in app_services:
            name_link = generate_link(svc['id'], humanize_name(svc['name']))
            description = escape_markdown(svc.get('description', ''))
            rows.append([name_link, description])

        lines.append(generate_table(["Name", "Description"], rows))
        return "\n".join(lines)

    def _generate_domain_services_table(self) -> str:
        """Generate domain services summary table"""
        domain_services = self.bounded_context.get('domain_services', [])
        if not domain_services:
            return ""

        lines = ["## Domain Services", ""]

        rows = []
        for svc in domain_services:
            name_link = generate_link(svc['id'], humanize_name(svc['name']))
            description = escape_markdown(svc.get('description', ''))
            rows.append([name_link, description])

        lines.append(generate_table(["Name", "Description"], rows))
        return "\n".join(lines)

    def _generate_aggregates_table(self) -> str:
        """Generate aggregates summary table"""
        aggregates = self.bounded_context.get('aggregates', [])
        if not aggregates:
            return ""

        lines = ["## Aggregates", ""]

        rows = []
        for agg in aggregates:
            name_link = generate_link(agg['id'], humanize_name(agg['name']))
            # Get description from root entity or aggregate
            root_entity = self.resolver.get_entity(agg['root_ref'])
            description = ""
            if root_entity:
                # Try to get description from entity's first invariant or business method
                invariants = root_entity.get('invariants', [])
                if invariants:
                    description = invariants[0]
                else:
                    description = f"Manages {humanize_name(root_entity['name'])} lifecycle"
            rows.append([name_link, escape_markdown(description)])

        lines.append(generate_table(["Name", "Description"], rows))
        return "\n".join(lines)

    def _generate_repositories_table(self) -> str:
        """Generate repositories summary table"""
        repositories = self.bounded_context.get('repositories', [])
        if not repositories:
            return ""

        lines = ["## Repositories", ""]

        rows = []
        for repo in repositories:
            name_link = generate_link(repo['id'], humanize_name(repo['name']))
            agg = self.resolver.get_aggregate(repo['aggregate_ref'])
            description = f"Persistence for {humanize_name(agg['name'])}" if agg else ""
            rows.append([name_link, escape_markdown(description)])

        lines.append(generate_table(["Name", "Description"], rows))
        return "\n".join(lines)

    def _generate_aggregate_details(self) -> str:
        """Generate detailed aggregate sections with UML diagrams"""
        aggregates = self.bounded_context.get('aggregates', [])
        if not aggregates:
            return ""

        sections = []
        for agg in aggregates:
            sections.append(self._generate_aggregate_section(agg))

        return "\n\n".join(sections)

    def _generate_aggregate_section(self, agg: dict) -> str:
        """Generate a single aggregate detail section"""
        lines = [
            f"## {generate_anchor(agg['id'])}{humanize_name(agg['name'])}",
            "",
            f"**Aggregate ID**: `{agg['id']}`",
        ]

        # Root entity link
        root_entity = self.resolver.get_entity(agg['root_ref'])
        if root_entity:
            lines.append(f"**Root Entity**: {generate_link(root_entity['id'], humanize_name(root_entity['name']))}")

        # Size estimate
        if 'size_estimate' in agg:
            lines.append(f"**Size Estimate**: {agg['size_estimate'].capitalize()}")

        lines.append("")

        # Description (from root entity if available)
        if root_entity and root_entity.get('invariants'):
            lines.append("### Description")
            lines.append("")
            lines.append(root_entity['invariants'][0])
            lines.append("")

        # Entities
        entities = self.resolver.get_entities_for_aggregate(agg['id'])
        if entities:
            lines.append("### Entities")
            for ent in entities:
                is_root = ent['id'] == agg['root_ref']
                root_marker = " (root)" if is_root else ""
                lines.append(f"- {generate_link(ent['id'], humanize_name(ent['name']))}{root_marker}")
            lines.append("")

        # Value Objects
        value_objects = self.resolver.get_value_objects_for_aggregate(agg['id'])
        if value_objects:
            lines.append("### Value Objects")
            for vo in value_objects:
                lines.append(f"- {generate_link(vo['id'], humanize_name(vo['name']))}")
            lines.append("")

        # Consistency Rules
        if agg.get('consistency_rules'):
            lines.append("### Consistency Rules")
            for rule in agg['consistency_rules']:
                lines.append(f"- {rule}")
            lines.append("")

        # Invariants
        if agg.get('invariants'):
            lines.append("### Invariants")
            for inv in agg['invariants']:
                lines.append(f"- {inv}")
            lines.append("")

        # UML Diagram
        lines.append("### Aggregate UML Diagram")
        lines.append("")
        lines.append(self.diagram_generator.generate_diagram(agg))

        return "\n".join(lines)

    def _generate_value_object_details(self) -> str:
        """Generate detailed value object sections"""
        value_objects = self.bounded_context.get('value_objects', [])
        if not value_objects:
            return ""

        sections = []
        for vo in value_objects:
            sections.append(self._generate_value_object_section(vo))

        return "\n\n".join(sections)

    def _generate_value_object_section(self, vo: dict) -> str:
        """Generate a single value object detail section"""
        lines = [
            f"### {generate_anchor(vo['id'])}{humanize_name(vo['name'])} Value Object",
            "",
            f"**Value Object ID**: `{vo['id']}`",
            f"**Name**: {humanize_name(vo['name'])}",
            f"**Description**: {vo.get('description', '')}",
            f"**Immutable**: {format_boolean(vo.get('immutability', True))}",
            ""
        ]

        # Attributes
        if vo.get('attributes'):
            lines.append("#### Attributes")
            lines.append("")
            rows = []
            for attr in vo['attributes']:
                rows.append([
                    attr['name'],
                    attr['type'],
                    format_boolean(attr.get('required', True)),
                    escape_markdown(attr.get('description', ''))
                ])
            lines.append(generate_table(["Name", "Type", "Required", "Description"], rows))
            lines.append("")

        # Validation Rules
        if vo.get('validation_rules'):
            lines.append("#### Validation Rules")
            for rule in vo['validation_rules']:
                lines.append(f"- {rule}")
            lines.append("")

        # Equality Criteria
        if vo.get('equality_criteria'):
            lines.append("#### Equality Criteria")
            for crit in vo['equality_criteria']:
                lines.append(f"- {crit}")
            lines.append("")

        return "\n".join(lines)

    def _generate_repository_details(self) -> str:
        """Generate detailed repository sections"""
        repositories = self.bounded_context.get('repositories', [])
        if not repositories:
            return ""

        sections = []
        for repo in repositories:
            sections.append(self._generate_repository_section(repo))

        return "\n\n".join(sections)

    def _generate_repository_section(self, repo: dict) -> str:
        """Generate a single repository detail section"""
        lines = [
            f"## {generate_anchor(repo['id'])}{humanize_name(repo['name'])}",
            "",
            f"**Repository ID**: `{repo['id']}`",
        ]

        # Aggregate reference
        agg = self.resolver.get_aggregate(repo['aggregate_ref'])
        if agg:
            lines.append(f"**Aggregate**: {generate_link(agg['id'], humanize_name(agg['name']))}")

        lines.append("")

        # Interface Methods
        if repo.get('interface_methods'):
            lines.append("### Interface Methods")
            lines.append("")
            rows = []
            for method in repo['interface_methods']:
                params = method.get('parameters', [])
                param_strs = [f"{p['name']}: {p['type']}" for p in params]
                param_str = ", ".join(param_strs)
                rows.append([
                    method['name'],
                    param_str,
                    method.get('returns', 'void'),
                    escape_markdown(method.get('description', ''))
                ])
            lines.append(generate_table(["Method", "Parameters", "Returns", "Description"], rows))

        return "\n".join(lines)

    def _generate_domain_service_details(self) -> str:
        """Generate detailed domain service sections"""
        domain_services = self.bounded_context.get('domain_services', [])
        if not domain_services:
            return ""

        sections = []
        for svc in domain_services:
            sections.append(self._generate_domain_service_section(svc))

        return "\n\n".join(sections)

    def _generate_domain_service_section(self, svc: dict) -> str:
        """Generate a single domain service detail section"""
        lines = [
            f"## {generate_anchor(svc['id'])}{humanize_name(svc['name'])}",
            "",
            f"**Service ID**: `{svc['id']}`",
            "**Type**: Domain Service",
            ""
        ]

        # Description
        if svc.get('description'):
            lines.append("### Description")
            lines.append("")
            lines.append(svc['description'])
            lines.append("")

        # Operations/Methods
        if svc.get('operations'):
            lines.append("### Methods")
            lines.append("")
            rows = []
            for op in svc['operations']:
                params = op.get('parameters', [])
                param_strs = [f"{p['name']}: {p['type']}" for p in params]
                param_str = ", ".join(param_strs)
                rows.append([
                    op['name'],
                    param_str,
                    op.get('returns', 'void'),
                    escape_markdown(op.get('description', ''))
                ])
            lines.append(generate_table(["Method", "Parameters", "Returns", "Description"], rows))

        return "\n".join(lines)

    def _generate_application_service_details(self) -> str:
        """Generate detailed application service sections"""
        app_services = self.bounded_context.get('application_services', [])
        if not app_services:
            return ""

        sections = []
        for svc in app_services:
            sections.append(self._generate_application_service_section(svc))

        return "\n\n".join(sections)

    def _generate_application_service_section(self, svc: dict) -> str:
        """Generate a single application service detail section"""
        lines = [
            f"## {generate_anchor(svc['id'])}{humanize_name(svc['name'])}",
            "",
            f"**Service ID**: `{svc['id']}`",
            "**Type**: Application Service",
            ""
        ]

        # Description
        if svc.get('description'):
            lines.append("### Description")
            lines.append("")
            lines.append(svc['description'])
            lines.append("")

        # Operations
        if svc.get('operations'):
            lines.append("### Operations")
            lines.append("")
            for op in svc['operations']:
                lines.append(self._generate_operation_section(op))
                lines.append("")

        return "\n".join(lines)

    def _generate_operation_section(self, op: dict) -> str:
        """Generate operation detail subsection"""
        lines = [f"#### {op['name']} ({op['type'].capitalize()})"]
        lines.append("")
        lines.append(f"**Type**: {op['type'].capitalize()}")

        # Parameters
        if op.get('parameters'):
            lines.append("**Parameters**:")
            for param in op['parameters']:
                required_marker = " (required)" if param.get('required', True) else " (optional)"
                lines.append(f"- {param['name']}: {param['type']}{required_marker}")

        # Returns
        if op.get('returns'):
            lines.append(f"**Returns**: {op['returns']}")

        lines.append("")

        # Transaction Boundary (for commands)
        if op['type'] == 'command' and op.get('transaction_boundary'):
            tb = op['transaction_boundary']
            lines.append("**Transaction Boundary**:")
            lines.append(f"- Is Transactional: {format_boolean(tb.get('is_transactional', True))}")
            if tb.get('modifies_aggregates'):
                agg_links = []
                for agg_id in tb['modifies_aggregates']:
                    agg = self.resolver.get_aggregate(agg_id)
                    if agg:
                        agg_links.append(agg_id)
                lines.append(f"- Modifies Aggregates: {', '.join(agg_links)}")
            if tb.get('consistency_type'):
                lines.append(f"- Consistency Type: {tb['consistency_type']}")
            lines.append("")

        # Workflow
        if op.get('workflow'):
            wf = op['workflow']
            lines.append("**Workflow**:")

            if wf.get('validates_input'):
                lines.append("1. Validates input (✓)")

            step_num = 2
            if wf.get('loads_aggregates'):
                agg_names = []
                for agg_id in wf['loads_aggregates']:
                    agg = self.resolver.get_aggregate(agg_id)
                    if agg:
                        agg_names.append(agg_id)
                lines.append(f"{step_num}. Loads aggregates: {', '.join(agg_names)}")
                step_num += 1
            elif op['type'] == 'command':
                lines.append(f"{step_num}. Creates new aggregate")
                step_num += 1

            if wf.get('invokes_domain_operations'):
                ops_str = ', '.join(wf['invokes_domain_operations'])
                svc_refs = ""
                if wf.get('invokes_domain_services'):
                    svc_names = []
                    for svc_id in wf['invokes_domain_services']:
                        svc = self.resolver.get_domain_service(svc_id)
                        if svc:
                            svc_names.append(humanize_name(svc['name']))
                    if svc_names:
                        svc_refs = f" (via {', '.join(svc_names)})"
                lines.append(f"{step_num}. Invokes domain operations: {ops_str}{svc_refs}")
                step_num += 1

            if wf.get('persists_aggregates'):
                lines.append(f"{step_num}. Persists aggregate (✓)")
                step_num += 1

            if wf.get('publishes_events'):
                event_names = []
                for evt_id in wf['publishes_events']:
                    evt = self.resolver.get_domain_event(evt_id)
                    if evt:
                        event_names.append(evt_id)
                lines.append(f"{step_num}. Publishes events: {', '.join(event_names)}")
                step_num += 1

            if wf.get('returns_dto'):
                lines.append(f"{step_num}. Returns DTO: {wf['returns_dto']}")

        return "\n".join(lines)

    def _generate_domain_events(self) -> str:
        """Generate domain events section"""
        events = self.bounded_context.get('domain_events', [])
        if not events:
            return ""

        lines = ["## Domain Events", ""]

        for evt in events:
            lines.append(self._generate_domain_event_section(evt))
            lines.append("")

        return "\n".join(lines)

    def _generate_domain_event_section(self, evt: dict) -> str:
        """Generate a single domain event section"""
        lines = [
            f"### {generate_anchor(evt['id'])}{humanize_name(evt['name'])}",
            "",
            f"**Event ID**: `{evt['id']}`",
        ]

        # Aggregate reference
        agg = self.resolver.get_aggregate(evt['aggregate_ref'])
        if agg:
            lines.append(f"**Aggregate**: {generate_link(agg['id'], humanize_name(agg['name']))}")

        lines.append("")

        # Payload
        if evt.get('data_carried'):
            lines.append("#### Payload")
            lines.append("")
            rows = []
            for field in evt['data_carried']:
                rows.append([
                    field['name'],
                    field['type'],
                    escape_markdown(field.get('description', ''))
                ])
            lines.append(generate_table(["Field", "Type", "Description"], rows))

        return "\n".join(lines)

    def _generate_command_interfaces(self) -> str:
        """Generate command interfaces section"""
        cmd_interfaces = self.bounded_context.get('command_interfaces', [])
        if not cmd_interfaces:
            return ""

        lines = ["## Command Interfaces", ""]

        for cmd_if in cmd_interfaces:
            lines.append(self._generate_command_interface_section(cmd_if))
            lines.append("")

        return "\n".join(lines)

    def _generate_command_interface_section(self, cmd_if: dict) -> str:
        """Generate a single command interface section"""
        lines = [
            f"### {generate_anchor(cmd_if['id'])}{humanize_name(cmd_if['name'])} Interface",
            "",
            f"**Command Interface ID**: `{cmd_if['id']}`",
        ]

        if cmd_if.get('description'):
            lines.append(f"**Description**: {cmd_if['description']}")

        lines.append("")

        # Command Records
        for cmd_rec in cmd_if.get('command_records', []):
            lines.append(f"#### {humanize_name(cmd_rec['record_name'])}")
            lines.append("")
            lines.append(f"**Record Name**: {cmd_rec['record_name']}")
            lines.append(f"**Intent**: {cmd_rec['intent']}")
            lines.append("")

            # Parameters
            if cmd_rec.get('parameters'):
                lines.append("**Parameters**:")
                lines.append("")
                rows = []
                for param in cmd_rec['parameters']:
                    rows.append([
                        param['name'],
                        param['type'],
                        format_boolean(param.get('required', True)),
                        escape_markdown(param.get('description', ''))
                    ])
                lines.append(generate_table(["Name", "Type", "Required", "Description"], rows))
                lines.append("")

            # Returns
            lines.append("**Returns**:")
            lines.append(f"- Type: {cmd_rec.get('returns', 'void')}")
            if cmd_rec.get('return_type_ref'):
                vo = self.resolver.get_value_object(cmd_rec['return_type_ref'])
                if vo:
                    lines.append(f"- Value Object: {generate_link(vo['id'], humanize_name(vo['name']))}")
            lines.append("")

            # Modifies Aggregate
            if cmd_rec.get('modifies_aggregate'):
                agg = self.resolver.get_aggregate(cmd_rec['modifies_aggregate'])
                if agg:
                    lines.append(f"**Modifies Aggregate**: {generate_link(agg['id'], humanize_name(agg['name']))}")
                    lines.append("")

            # Publishes Events
            if cmd_rec.get('publishes_events'):
                lines.append("**Publishes Events**:")
                for evt_id in cmd_rec['publishes_events']:
                    evt = self.resolver.get_domain_event(evt_id)
                    if evt:
                        lines.append(f"- {generate_link(evt_id, humanize_name(evt['name']))}")
                lines.append("")

            # Audit Fields
            if cmd_rec.get('audit_fields'):
                lines.append(f"**Audit Fields**: {', '.join(cmd_rec['audit_fields'])}")
                lines.append("")

        return "\n".join(lines)

    def _generate_query_interfaces(self) -> str:
        """Generate query interfaces section"""
        qry_interfaces = self.bounded_context.get('query_interfaces', [])
        if not qry_interfaces:
            return ""

        lines = ["## Query Interfaces", ""]

        for qry_if in qry_interfaces:
            lines.append(self._generate_query_interface_section(qry_if))
            lines.append("")

        return "\n".join(lines)

    def _generate_query_interface_section(self, qry_if: dict) -> str:
        """Generate a single query interface section"""
        lines = [
            f"### {generate_anchor(qry_if['id'])}{humanize_name(qry_if['name'])} Interface",
            "",
            f"**Query Interface ID**: `{qry_if['id']}`",
        ]

        if qry_if.get('description'):
            lines.append(f"**Description**: {qry_if['description']}")

        lines.append("")

        # Query Methods
        for qry_method in qry_if.get('query_methods', []):
            lines.append(f"#### {humanize_name(qry_method['method_name'])}")
            lines.append("")
            lines.append(f"**Method Name**: {qry_method['method_name']}")

            if qry_method.get('description'):
                lines.append(f"**Description**: {qry_method['description']}")

            lines.append("")

            # Parameters
            if qry_method.get('parameters'):
                lines.append("**Parameters**:")
                lines.append("")
                rows = []
                for param in qry_method['parameters']:
                    rows.append([
                        param['name'],
                        param['type'],
                        format_boolean(param.get('required', True)),
                        escape_markdown(param.get('description', ''))
                    ])
                lines.append(generate_table(["Name", "Type", "Required", "Description"], rows))
                lines.append("")

            # Result Record
            lines.append(f"**Result Record**: {qry_method['result_record_name']}")
            lines.append("")

            # Result Structure
            if qry_method.get('result_structure') and qry_method['result_structure'].get('fields'):
                lines.append("**Result Structure**:")
                lines.append("")
                rows = []
                for field in qry_method['result_structure']['fields']:
                    rows.append([
                        field['name'],
                        field['type'],
                        field.get('serialization', ''),
                        escape_markdown(field.get('description', ''))
                    ])
                lines.append(generate_table(["Field", "Type", "Serialization", "Description"], rows))
                lines.append("")

            # Bypasses Domain Model
            bypasses = qry_method.get('bypasses_domain_model', False)
            lines.append(f"**Bypasses Domain Model**: {format_boolean(bypasses)}")
            lines.append("")

            # Optimizations
            if qry_method.get('optimizations'):
                opt = qry_method['optimizations']
                lines.append("**Optimizations**:")
                lines.append(f"- Denormalized: {format_boolean(opt.get('denormalized', False))}")
                lines.append(f"- Cached: {format_boolean(opt.get('cached', False))}")
                lines.append(f"- Indexed: {format_boolean(opt.get('indexed', True))}")
                lines.append("")

        return "\n".join(lines)
