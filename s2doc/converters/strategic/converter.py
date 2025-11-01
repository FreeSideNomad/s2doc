"""Main converter class for Strategic DDD YAML to Markdown"""

from typing import List, Optional
from .models import (
    EntityResolver,
    generate_anchor,
    generate_link,
    format_boolean,
    generate_table,
    escape_markdown,
    safe_get,
    humanize_relationship_type
)


class StrategicDDDConverter:
    """Convert Strategic DDD YAML to Markdown"""

    def __init__(self, yaml_data: dict):
        self.system = yaml_data['system']
        self.resolver = EntityResolver(self.system)

    def convert_to_markdown(self) -> str:
        """Generate complete markdown document"""
        sections = [
            self._generate_header(),
            self._generate_index(),
            self._generate_architecture_diagram(),
            self._generate_domains_table(),
            self._generate_domain_details(),  # Now includes nested bounded contexts
            self._generate_bff_scopes(),       # Now includes nested interfaces
            self._generate_context_mappings_table(),
            self._generate_context_mappings_details()
        ]
        return "\n\n".join(filter(None, sections))

    def _generate_header(self) -> str:
        """Generate system header section"""
        system_name = self.system.get('name', 'System')
        system_id = self.system.get('id', '')
        version = self.system.get('version', '')
        description = self.system.get('description', '')

        header = f"# {system_name}\n\n"
        header += f"**System ID**: `{system_id}`\n"
        header += f"**Version**: {version}\n\n"
        header += f"{description}"

        return header

    def _generate_index(self) -> str:
        """Generate hierarchical index/table of contents"""
        lines = ["## Index\n"]

        # Domains and their bounded contexts
        domains = self.system.get('domains', [])
        if domains:
            lines.append("### Domains and Bounded Contexts\n")
            for domain in domains:
                domain_id = domain['id']
                domain_name = domain.get('name', '')
                lines.append(f"- {generate_link(domain_id, domain_name)}")

                # List bounded contexts under this domain
                contexts = self.resolver.get_contexts_for_domain(domain_id)
                for context in contexts:
                    bc_id = context['id']
                    bc_name = context.get('name', '')
                    lines.append(f"  - {generate_link(bc_id, bc_name)}")

            lines.append("")

        # BFF Scopes and their interfaces
        bff_scopes = self.system.get('bff_scopes', [])
        if bff_scopes:
            lines.append("### Backend-for-Frontend (BFF) Scopes and Interfaces\n")
            for bff in bff_scopes:
                bff_id = bff['id']
                bff_name = bff.get('name', '')
                lines.append(f"- {generate_link(bff_id, bff_name)}")

                # List interfaces under this BFF
                bff_interfaces = self.system.get('bff_interfaces', [])
                for bff_if in bff_interfaces:
                    if bff_if.get('bff_scope_ref') == bff_id:
                        bff_if_id = bff_if['id']
                        bff_if_name = bff_if.get('name', '')
                        lines.append(f"  - {generate_link(bff_if_id, bff_if_name)}")

            lines.append("")

        # Context mappings by domain
        mappings = self.system.get('context_mappings', [])
        if mappings:
            lines.append("### Context Mappings\n")

            # Group mappings by domain
            domain_mappings = {}
            for mapping in mappings:
                upstream = mapping.get('upstream_context', '')
                downstream = mapping.get('downstream_context', '')

                # Get domains for upstream and downstream
                upstream_bc = self.resolver.get_context(upstream)
                downstream_bc = self.resolver.get_context(downstream)

                if upstream_bc:
                    domain_ref = upstream_bc.get('domain_ref')
                    if domain_ref:
                        if domain_ref not in domain_mappings:
                            domain_mappings[domain_ref] = []
                        domain_mappings[domain_ref].append(mapping)

            for domain_id, domain_mapping_list in domain_mappings.items():
                domain = self.resolver.get_domain(domain_id)
                if domain:
                    domain_name = domain.get('name', domain_id)
                    lines.append(f"- **{domain_name}**")
                    for mapping in domain_mapping_list:
                        mapping_name = mapping.get('name', '')
                        mapping_id = mapping.get('id', '')
                        lines.append(f"  - {generate_link(mapping_id, mapping_name)}")

        return "\n".join(lines)

    def _generate_architecture_diagram(self) -> str:
        """Generate Mermaid diagram showing system hierarchy and context relationships"""
        system_name = self.system.get('name', 'System')
        domains = self.system.get('domains', [])
        bounded_contexts = self.system.get('bounded_contexts', [])
        context_mappings = self.system.get('context_mappings', [])
        bff_scopes = self.system.get('bff_scopes', [])
        bff_interfaces = self.system.get('bff_interfaces', [])

        lines = ["## System Architecture\n", "```mermaid", "graph TB"]

        # System node with stereotype (using guillemets « » instead of << >>)
        lines.append(f'    System["«System»<br/>{system_name}"]')
        lines.append("")

        # Generate domain nodes and connections
        domain_nodes = {}
        for i, domain in enumerate(domains):
            domain_id = domain['id']
            domain_name = domain['name']
            domain_type = domain.get('type', 'core')
            node_id = f"Domain{i+1}"
            domain_nodes[domain_id] = node_id

            lines.append(f'    {node_id}["«Domain»<br/>{domain_name}<br/>(type: {domain_type})"]')
            lines.append(f'    System --> {node_id}')

        lines.append("")

        # Generate bounded context nodes
        bc_nodes = {}
        bc_counter = 1
        for domain in domains:
            domain_id = domain['id']
            domain_node = domain_nodes.get(domain_id)
            if not domain_node:
                continue

            for bc_id in domain.get('bounded_contexts', []):
                bc = self.resolver.get_context(bc_id)
                if bc:
                    bc_node_id = f"BC{bc_counter}"
                    bc_nodes[bc_id] = bc_node_id
                    bc_name = bc['name']

                    lines.append(f'    {domain_node} --> {bc_node_id}["«Bounded Context»<br/>{bc_name}"]')
                    bc_counter += 1

        lines.append("")

        # Generate BFF scope nodes
        bff_nodes = {}
        bff_counter = 1
        if bff_scopes:
            for bff in bff_scopes:
                bff_id = bff['id']
                bff_name = bff.get('name', '')
                client_type = bff.get('client_type', '')
                bff_node_id = f"BFF{bff_counter}"
                bff_nodes[bff_id] = bff_node_id

                lines.append(f'    System --> {bff_node_id}["«BFF»<br/>{bff_name}<br/>({client_type})"]')
                bff_counter += 1

            lines.append("")

        # Generate BFF interface nodes
        bff_if_nodes = {}
        bff_if_counter = 1
        if bff_interfaces:
            for bff_if in bff_interfaces:
                bff_if_id = bff_if['id']
                bff_if_name = bff_if.get('name', '')
                bff_scope_ref = bff_if.get('bff_scope_ref', '')

                bff_if_node_id = f"BFFIF{bff_if_counter}"
                bff_if_nodes[bff_if_id] = bff_if_node_id

                # Connect to parent BFF scope
                bff_scope_node = bff_nodes.get(bff_scope_ref, bff_scope_ref)
                lines.append(f'    {bff_scope_node} --> {bff_if_node_id}["«BFF Interface»<br/>{bff_if_name}"]')

                # Connect to primary bounded context
                primary_bc = bff_if.get('primary_bounded_context_ref', '')
                if primary_bc and primary_bc in bc_nodes:
                    lines.append(f'    {bff_if_node_id} -.-> {bc_nodes[primary_bc]}')

                bff_if_counter += 1

            lines.append("")

        # Generate context relationships
        for mapping in context_mappings:
            upstream = mapping.get('upstream_context')
            downstream = mapping.get('downstream_context')
            rel_type = mapping.get('relationship_type', 'dependency')

            upstream_node = bc_nodes.get(upstream, upstream)
            downstream_node = bc_nodes.get(downstream, downstream)

            # Handle external systems
            if downstream not in bc_nodes and downstream:
                lines.append(f'    {downstream_node}["{downstream}"]')

            lines.append(f'    {upstream_node} -.->|"{rel_type}"| {downstream_node}')

        lines.append("")

        # Styling
        lines.append("    %% Styling")
        lines.append("    classDef systemStyle fill:#e1f5ff,stroke:#01579b,stroke-width:3px,color:#000")
        lines.append("    classDef coreStyle fill:#c8e6c9,stroke:#2e7d32,stroke-width:2px,color:#000")
        lines.append("    classDef supportingStyle fill:#fff9c4,stroke:#f57f17,stroke-width:2px,color:#000")
        lines.append("    classDef genericStyle fill:#f5f5f5,stroke:#616161,stroke-width:2px,color:#000")
        lines.append("    classDef bcStyle fill:#bbdefb,stroke:#1976d2,stroke-width:1px,color:#000")
        lines.append("    classDef bffStyle fill:#ffe0b2,stroke:#e65100,stroke-width:2px,color:#000")
        lines.append("    classDef bffIfStyle fill:#fff3e0,stroke:#ef6c00,stroke-width:1px,color:#000")
        lines.append("")

        # Apply system style
        lines.append("    class System systemStyle")

        # Apply domain styles based on type
        core_domains = []
        supporting_domains = []
        generic_domains = []

        for domain_id, node_id in domain_nodes.items():
            domain = self.resolver.get_domain(domain_id)
            if domain:
                domain_type = domain.get('type', 'core')
                if domain_type == 'core':
                    core_domains.append(node_id)
                elif domain_type == 'supporting':
                    supporting_domains.append(node_id)
                elif domain_type == 'generic':
                    generic_domains.append(node_id)

        if core_domains:
            lines.append(f"    class {','.join(core_domains)} coreStyle")
        if supporting_domains:
            lines.append(f"    class {','.join(supporting_domains)} supportingStyle")
        if generic_domains:
            lines.append(f"    class {','.join(generic_domains)} genericStyle")

        # Apply BC styles
        if bc_nodes:
            lines.append(f"    class {','.join(bc_nodes.values())} bcStyle")

        # Apply BFF styles
        if bff_nodes:
            lines.append(f"    class {','.join(bff_nodes.values())} bffStyle")

        # Apply BFF Interface styles
        if bff_if_nodes:
            lines.append(f"    class {','.join(bff_if_nodes.values())} bffIfStyle")

        lines.append("```")

        return "\n".join(lines)

    def _generate_domains_table(self) -> str:
        """Generate domains overview table"""
        domains = self.system.get('domains', [])
        if not domains:
            return ""

        headers = ["Name", "Type", "Strategic Importance", "Description"]
        rows = []

        for domain in domains:
            domain_id = domain['id']
            name = domain.get('name', '')
            domain_type = domain.get('type', '')
            importance = domain.get('strategic_importance', '')
            description = domain.get('description', '')

            rows.append([
                generate_link(domain_id, name),  # Link the name, not the ID
                domain_type,
                importance,
                escape_markdown(description)
            ])

        table = generate_table(headers, rows)
        return f"## Domains\n\n{table}"

    def _generate_bff_scopes(self) -> str:
        """Generate BFF scopes sections with nested interfaces"""
        bff_scopes = self.system.get('bff_scopes', [])
        if not bff_scopes:
            return ""

        sections = ["## Backend-for-Frontend (BFF) Scopes\n"]

        for bff in bff_scopes:
            sections.append(self._generate_single_bff_scope(bff))

        return "\n\n".join(sections)

    def _generate_single_bff_scope(self, bff: dict) -> str:
        """Generate single BFF scope section with nested interfaces"""
        lines = []

        # Header with anchor
        bff_id = bff['id']
        name = bff.get('name', '')
        lines.append(f"## {generate_anchor(bff_id)}{name}\n")

        # Basic attributes
        lines.append(f"**BFF ID**: `{bff_id}`")
        lines.append(f"**Client Type**: {bff.get('client_type', '')}")
        lines.append(f"**Serves Interface**: {bff.get('serves_interface', '')}")
        lines.append(f"**Owned By Team**: {bff.get('owned_by_team', '')} ({bff.get('team_type', '')})\n")

        # Aggregates from contexts
        aggregates_from = bff.get('aggregates_from_contexts', [])
        if aggregates_from:
            lines.append("#### Aggregates From Contexts")
            for context_id in aggregates_from:
                lines.append(f"- {generate_link(context_id, context_id)}")
            lines.append("")

        # Provides section
        provides = bff.get('provides', {})
        if provides:
            lines.append("#### Provides\n")

            # Endpoints
            endpoints = provides.get('endpoints', [])
            if endpoints:
                lines.append("**Endpoints**:")
                headers = ["Path", "Method", "Aggregates From", "Description"]
                rows = []
                for ep in endpoints:
                    agg_from = ep.get('aggregates_from', [])
                    agg_from_str = ", ".join(agg_from) if agg_from else ""
                    rows.append([
                        escape_markdown(ep.get('path', '')),
                        ep.get('method', ''),
                        escape_markdown(agg_from_str),
                        escape_markdown(ep.get('description', ''))
                    ])
                lines.append(generate_table(headers, rows))
                lines.append("")

            # Data aggregation
            data_agg = provides.get('data_aggregation', {})
            if data_agg:
                lines.append("**Data Aggregation**:")
                lines.append(f"- Strategy: {data_agg.get('strategy', '')}")
                if 'example' in data_agg:
                    lines.append(f"- Example: {data_agg['example']}")
                lines.append("")

            # Transformations
            transformations = provides.get('transformations', [])
            if transformations:
                lines.append("**Transformations**:")
                headers = ["From Context", "Transformation Type", "Description"]
                rows = []
                for trans in transformations:
                    rows.append([
                        trans.get('from_context', ''),
                        trans.get('transformation_type', ''),
                        escape_markdown(trans.get('description', ''))
                    ])
                lines.append(generate_table(headers, rows))
                lines.append("")

            # Client optimizations
            optimizations = provides.get('client_optimizations', [])
            if optimizations:
                lines.append("**Client Optimizations**:")
                for opt in optimizations:
                    lines.append(f"- {opt}")
                lines.append("")

        # Responsibilities
        responsibilities = bff.get('responsibilities', {})
        if responsibilities:
            lines.append("#### Responsibilities")
            lines.append(f"- Data Aggregation: {format_boolean(responsibilities.get('data_aggregation', False))}")
            lines.append(f"- Client-Specific Orchestration: {format_boolean(responsibilities.get('client_specific_orchestration', False))}")
            lines.append(f"- Presentation Logic: {format_boolean(responsibilities.get('presentation_logic', False))}")
            lines.append(f"- Format Translation: {format_boolean(responsibilities.get('format_translation', False))}")
            lines.append(f"- Business Logic: {format_boolean(responsibilities.get('business_logic', False))}")
            lines.append(f"- Transaction Management: {format_boolean(responsibilities.get('transaction_management', False))}")
            lines.append(f"- Direct Persistence: {format_boolean(responsibilities.get('direct_persistence', False))}")
            lines.append("")

        # Architecture
        lines.append("#### Architecture")
        lines.append(f"- **Layer**: {bff.get('architecture_layer', '')}")
        lines.append(f"- **Pattern Type**: {bff.get('pattern_type', '')}")

        upstream_deps = bff.get('upstream_dependencies', [])
        if upstream_deps:
            lines.append(f"- **Upstream Dependencies**: {', '.join(upstream_deps)}")

        calls = bff.get('calls', [])
        if calls:
            lines.append(f"- **Calls**: {', '.join(calls)}")
        lines.append("")

        # Anti-patterns
        anti_patterns = bff.get('anti_patterns', {})
        if anti_patterns:
            lines.append("#### Anti-Patterns (What to Avoid)")
            lines.append(f"- Shared Business Logic: {format_boolean(anti_patterns.get('shared_business_logic', False))}")
            lines.append(f"- Generic Cross-Cutting Concerns: {format_boolean(anti_patterns.get('generic_cross_cutting_concerns', False))}")
            lines.append(f"- Direct Database Access: {format_boolean(anti_patterns.get('direct_database_access', False))}")
            lines.append(f"- Serving Multiple Client Types: {format_boolean(anti_patterns.get('serving_multiple_client_types', False))}")
            lines.append("")

        # Now add nested BFF interfaces
        bff_interfaces = self.system.get('bff_interfaces', [])
        nested_interfaces = [bff_if for bff_if in bff_interfaces if bff_if.get('bff_scope_ref') == bff_id]

        for bff_if in nested_interfaces:
            lines.append(self._generate_single_bff_interface(bff_if))
            lines.append("")

        return "\n".join(lines)

    def _generate_single_bff_interface(self, bff_if: dict) -> str:
        """Generate single BFF interface section as H3"""
        lines = []

        # Header with anchor (H3 level)
        bff_if_id = bff_if['id']
        name = bff_if.get('name', '')
        lines.append(f"### {generate_anchor(bff_if_id)}{name}\n")

        # Basic attributes
        lines.append(f"**Interface ID**: `{bff_if_id}`")

        bff_scope_ref = bff_if.get('bff_scope_ref', '')
        if bff_scope_ref:
            lines.append(f"**BFF Scope**: {generate_link(bff_scope_ref, bff_scope_ref)}")

        primary_bc_ref = bff_if.get('primary_bounded_context_ref', '')
        if primary_bc_ref:
            lines.append(f"**Primary Context**: {generate_link(primary_bc_ref, primary_bc_ref)}")

        lines.append(f"**Base Path**: `{bff_if.get('base_path', '')}`\n")

        # Additional contexts
        additional_contexts = bff_if.get('additional_context_refs', [])
        if additional_contexts:
            lines.append("#### Additional Contexts")
            for context_id in additional_contexts:
                lines.append(f"- {generate_link(context_id, context_id)}")
            lines.append("")

        # Endpoints
        endpoints = bff_if.get('endpoints', [])
        if endpoints:
            lines.append("#### Endpoints")
            headers = ["Path", "Method", "Operation Type", "Description", "Delegates To", "Aggregates From"]
            rows = []
            for ep in endpoints:
                delegates_cmd = ep.get('delegates_to_commands', [])
                delegates_qry = ep.get('delegates_to_queries', [])
                delegates = delegates_cmd + delegates_qry
                delegates_str = ", ".join(delegates) if delegates else ""

                agg_from = ep.get('aggregates_data_from', [])
                agg_from_str = ", ".join(agg_from) if agg_from else ""

                rows.append([
                    escape_markdown(ep.get('path', '')),
                    ep.get('method', ''),
                    ep.get('operation_type', ''),
                    escape_markdown(ep.get('description', '')),
                    escape_markdown(delegates_str),
                    escape_markdown(agg_from_str)
                ])
            lines.append(generate_table(headers, rows))
            lines.append("")

        # Execution model
        lines.append("#### Execution Model")
        lines.append(f"- **Model**: {bff_if.get('execution_model', '')}")

        error_handling = bff_if.get('error_handling', {})
        if error_handling:
            lines.append(f"- **Error Handling Strategy**: {error_handling.get('strategy', '')}")
            if 'description' in error_handling:
                lines.append(f"- **Error Handling Description**: {error_handling['description']}")
        lines.append("")

        # Technology stack
        tech_stack = bff_if.get('technology_stack', {})
        if tech_stack:
            lines.append("#### Technology Stack")
            if 'framework' in tech_stack:
                lines.append(f"- **Framework**: {tech_stack['framework']}")
            if 'controller_annotation' in tech_stack:
                lines.append(f"- **Controller Annotation**: {tech_stack['controller_annotation']}")
            lines.append(f"- **Layer**: {bff_if.get('layer', '')}")
            lines.append("")

        # Value object conversion
        vo_conversion = bff_if.get('value_object_conversion', {})
        if vo_conversion:
            lines.append("#### Value Object Conversion")

            from_string = vo_conversion.get('from_string', [])
            if from_string:
                lines.append("\n**From String**:")
                headers = ["Value Object", "From Field", "Method"]
                rows = []
                for item in from_string:
                    rows.append([
                        item.get('value_object_ref', ''),
                        item.get('from_field', ''),
                        item.get('method', '')
                    ])
                lines.append(generate_table(headers, rows))

            to_string = vo_conversion.get('to_string', [])
            if to_string:
                lines.append("\n**To String**:")
                headers = ["Value Object", "To Field", "Method"]
                rows = []
                for item in to_string:
                    rows.append([
                        item.get('value_object_ref', ''),
                        item.get('to_field', ''),
                        item.get('method', '')
                    ])
                lines.append(generate_table(headers, rows))

        return "\n".join(lines)

    def _generate_context_mappings_table(self) -> str:
        """Generate context mappings table"""
        mappings = self.system.get('context_mappings', [])
        if not mappings:
            return ""

        headers = ["Mapping", "Upstream Context", "Downstream Context", "Relationship Type", "Integration Pattern"]
        rows = []

        for mapping in mappings:
            mapping_id = mapping.get('id', '')
            mapping_name = mapping.get('name', '')
            upstream = mapping.get('upstream_context', '')
            downstream = mapping.get('downstream_context', '')
            rel_type = mapping.get('relationship_type', '')
            integration = escape_markdown(mapping.get('integration_pattern', ''))

            # Link mapping name to its detail section using mapping ID as anchor
            mapping_link = generate_link(mapping_id, mapping_name)

            # Get context names instead of IDs
            if upstream.startswith('bc_'):
                upstream_bc = self.resolver.get_context(upstream)
                upstream_name = upstream_bc.get('name', upstream) if upstream_bc else upstream
                upstream_link = generate_link(upstream, upstream_name)
            else:
                upstream_link = upstream

            if downstream.startswith('bc_'):
                downstream_bc = self.resolver.get_context(downstream)
                downstream_name = downstream_bc.get('name', downstream) if downstream_bc else downstream
                downstream_link = generate_link(downstream, downstream_name)
            else:
                downstream_link = downstream

            # Humanize relationship type
            humanized_rel_type = humanize_relationship_type(rel_type)

            rows.append([
                mapping_link,
                upstream_link,
                downstream_link,
                humanized_rel_type,
                integration
            ])

        table = generate_table(headers, rows)
        return f"## Bounded Context Relationships\n\n{table}"

    def _generate_context_mappings_details(self) -> str:
        """Generate detailed context mapping sections"""
        mappings = self.system.get('context_mappings', [])
        if not mappings:
            return ""

        sections = []

        for mapping in mappings:
            sections.append(self._generate_single_context_mapping(mapping))

        return "\n\n".join(sections)

    def _generate_single_context_mapping(self, mapping: dict) -> str:
        """Generate single context mapping detail section"""
        lines = []

        # Header with anchor (H3 level)
        mapping_id = mapping.get('id', '')
        name = mapping.get('name', '')
        lines.append(f"### {generate_anchor(mapping_id)}{name}\n")

        # Basic attributes
        upstream = mapping.get('upstream_context', '')
        downstream = mapping.get('downstream_context', '')
        rel_type = mapping.get('relationship_type', '')

        lines.append(f"**Mapping ID**: `{mapping_id}`")

        upstream_link = generate_link(upstream, upstream) if upstream.startswith('bc_') else upstream
        downstream_link = generate_link(downstream, downstream) if downstream.startswith('bc_') else downstream

        lines.append(f"**Upstream**: {upstream_link}")
        lines.append(f"**Downstream**: {downstream_link}")
        lines.append(f"**Relationship Type**: {rel_type}\n")

        # Integration pattern
        integration = mapping.get('integration_pattern', '')
        if integration:
            lines.append(f"**Integration Pattern**: {integration}\n")

        # Translation map
        translation_map = mapping.get('translation_map', {})
        if translation_map:
            lines.append("#### Translation Map")
            for key, value in translation_map.items():
                lines.append(f"- {key} → {value}")
            lines.append("")

        # ACL details
        acl_details = mapping.get('acl_details', {})
        if acl_details:
            lines.append("#### Anti-Corruption Layer Details\n")

            facades = acl_details.get('facades', [])
            if facades:
                lines.append("**Facades**:")
                for facade in facades:
                    lines.append(f"- {facade}")
                lines.append("")

            adapters = acl_details.get('adapters', [])
            if adapters:
                lines.append("**Adapters**:")
                for adapter in adapters:
                    lines.append(f"- {adapter}")
                lines.append("")

            translators = acl_details.get('translators', [])
            if translators:
                lines.append("**Translators**:")
                for translator in translators:
                    lines.append(f"- {translator}")
                lines.append("")

        # Shared elements
        shared_elements = mapping.get('shared_elements', [])
        if shared_elements:
            lines.append("#### Shared Elements")
            for element in shared_elements:
                lines.append(f"- {element}")
            lines.append("")

        # Notes
        notes = mapping.get('notes', '')
        if notes:
            lines.append(f"**Notes**: {notes}")

        return "\n".join(lines)

    def _generate_domain_details(self) -> str:
        """Generate detailed domain sections with nested bounded contexts"""
        domains = self.system.get('domains', [])
        if not domains:
            return ""

        sections = []

        for domain in domains:
            sections.append(self._generate_single_domain(domain))

        return "\n\n".join(sections)

    def _generate_single_domain(self, domain: dict) -> str:
        """Generate single domain detail section with nested bounded contexts"""
        lines = []

        # Header with anchor (H2 level)
        domain_id = domain['id']
        domain_name = domain.get('name', '')
        lines.append(f"## {generate_anchor(domain_id)}{domain_name}\n")

        # Basic attributes
        lines.append(f"**Domain ID**: `{domain_id}`")
        lines.append(f"**Type**: {domain.get('type', '')}")
        lines.append(f"**Strategic Importance**: {domain.get('strategic_importance', '')}")

        investment = domain.get('investment_strategy', '')
        if investment:
            lines.append(f"**Investment Strategy**: {investment}\n")
        else:
            lines.append("")

        # Description
        description = domain.get('description', '')
        if description:
            lines.append(description)
            lines.append("")

        # Notes
        notes = domain.get('notes', '')
        if notes:
            lines.append(f"**Notes**: {notes}")
            lines.append("")

        # Now nest bounded contexts as H3 sections
        contexts = self.resolver.get_contexts_for_domain(domain_id)
        for context in contexts:
            lines.append(self._generate_single_bounded_context(context))
            lines.append("")

        return "\n".join(lines)

    def _generate_single_bounded_context(self, context: dict) -> str:
        """Generate single bounded context detail section as H3"""
        lines = []

        # Header with anchor (H3 level)
        bc_id = context['id']
        bc_name = context.get('name', '')
        lines.append(f"### {generate_anchor(bc_id)}{bc_name}\n")

        # Basic attributes
        lines.append(f"**Context ID**: `{bc_id}`")

        domain_ref = context.get('domain_ref', '')
        if domain_ref:
            domain = self.resolver.get_domain(domain_ref)
            domain_name = domain.get('name', domain_ref) if domain else domain_ref
            lines.append(f"**Domain**: {generate_link(domain_ref, domain_name)} (`{domain_ref}`)")

        team = context.get('team_ownership', '')
        if team:
            lines.append(f"**Team Ownership**: {team}\n")
        else:
            lines.append("")

        # Description
        description = context.get('description', '')
        if description:
            lines.append(description)
            lines.append("")

        # Ubiquitous language
        ub_lang = context.get('ubiquitous_language', {})
        glossary = ub_lang.get('glossary', [])
        if glossary:
            lines.append("#### Ubiquitous Language\n")
            headers = ["Term", "Definition", "Examples"]
            rows = []

            for term_def in glossary:
                term = term_def.get('term', '')
                definition = escape_markdown(term_def.get('definition', ''))
                examples = term_def.get('examples', [])
                examples_str = escape_markdown(", ".join(examples)) if examples else ""

                rows.append([term, definition, examples_str])

            lines.append(generate_table(headers, rows))
            lines.append("")

        # Aggregates
        aggregates = context.get('aggregates', [])
        if aggregates:
            lines.append("#### Aggregates")
            for agg in aggregates:
                lines.append(f"- {agg}")
            lines.append("")

        # Repositories
        repositories = context.get('repositories', [])
        if repositories:
            lines.append("#### Repositories")
            for repo in repositories:
                lines.append(f"- {repo}")
            lines.append("")

        # Domain services
        domain_services = context.get('domain_services', [])
        if domain_services:
            lines.append("#### Domain Services")
            for svc in domain_services:
                lines.append(f"- {svc}")
            lines.append("")

        # Application services
        app_services = context.get('application_services', [])
        if app_services:
            lines.append("#### Application Services")
            for svc in app_services:
                lines.append(f"- {svc}")
            lines.append("")

        # Domain events
        domain_events = context.get('domain_events', [])
        if domain_events:
            lines.append("#### Domain Events")
            for evt in domain_events:
                lines.append(f"- {evt}")

        return "\n".join(lines)
