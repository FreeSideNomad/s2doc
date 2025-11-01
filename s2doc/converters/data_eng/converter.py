"""Convert data engineering YAML to Markdown documentation."""

from typing import Dict, List, Any, Optional
from .diagram_generator import DiagramGenerator


class DataEngConverter:
    """Convert data engineering YAML to Markdown documentation."""

    def __init__(self, data: dict):
        """Initialize with parsed YAML data."""
        self.data = data
        self.system = data.get('system', {})
        self.domains = {d['id']: d for d in data.get('domains', [])}
        self.pipelines = {p['id']: p for p in data.get('pipelines', [])}
        self.datasets = {ds['id']: ds for ds in data.get('datasets', [])}
        self.contracts = data.get('contracts', [])
        self.checks = data.get('checks', [])
        self.lineage = data.get('lineage', [])
        self.governance = data.get('governance', {})
        self.observability = data.get('observability', {})
        self.diagram_gen = DiagramGenerator()

    def convert_to_markdown(self, output_path: str) -> None:
        """Generate markdown file."""
        sections = [
            self._generate_header(),
            self._generate_toc(),
            "---",
            self._generate_hierarchical_index(),
            "---",
            self._generate_system_architecture(),
            "---",
            self._generate_domains_section(),
            "---",
            self._generate_datasets_section(),
            "---",
            self._generate_contracts_section(),
            "---",
            self._generate_checks_section(),
            "---",
            self._generate_lineage_section(),
            "---",
            self._generate_governance_section(),
            "---",
            self._generate_observability_section(),
            "---",
            "*Generated with [s2doc](https://github.com/FreeSideNomad/s2doc)*"
        ]

        markdown = "\n\n".join(filter(None, sections))

        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(markdown)

    def _generate_header(self) -> str:
        """Generate system header section."""
        lines = [f"# {self.system.get('name', 'Data Engineering System')}"]

        if self.system.get('description'):
            lines.append(f"\n> {self.system['description']}")

        # Owners
        if self.system.get('owners'):
            owner_names = [f"{o.get('team', 'Unknown')} ({o.get('contact', 'N/A')})"
                          for o in self.system['owners']]
            lines.append(f"\n**Owners**: {', '.join(owner_names)}")

        # Tags
        if self.system.get('tags'):
            lines.append(f"**Tags**: {', '.join(self.system['tags'])}")

        return "\n".join(lines)

    def _generate_toc(self) -> str:
        """Generate table of contents."""
        lines = ["## Table of Contents", ""]

        toc_items = [
            "- [Hierarchical Index](#hierarchical-index)",
            "- [System Architecture](#system-architecture)",
            "- [Domains](#domains)"
        ]

        # Add domain entries
        for domain_id in self.system.get('domains', []):
            if domain_id in self.domains:
                domain = self.domains[domain_id]
                domain_name = self.humanize_name(domain.get('name', domain_id))
                toc_items.append(f"  - [Domain: {domain_name}](#{domain_id})")

        toc_items.extend([
            "- [Datasets](#datasets)",
            "- [Data Contracts](#contracts)",
            "- [Data Quality Checks](#checks)",
            "- [Data Lineage](#lineage)",
            "- [Governance](#governance)",
            "- [Observability](#observability)"
        ])

        lines.extend(toc_items)
        return "\n".join(lines)

    def _generate_hierarchical_index(self) -> str:
        """Generate hierarchical index of all entities."""
        lines = ["## Hierarchical Index", "", "### Domains", ""]

        for domain_id in self.system.get('domains', []):
            if domain_id not in self.domains:
                continue

            domain = self.domains[domain_id]
            domain_name = self.humanize_name(domain.get('name', domain_id))
            domain_desc = domain.get('description', '')

            lines.append(f"- **[{domain_name}](#{domain_id})** - {domain_desc}")

            # Pipelines
            if domain.get('pipelines'):
                lines.append("  - Pipelines:")
                for pipeline_id in domain['pipelines']:
                    if pipeline_id in self.pipelines:
                        pipeline = self.pipelines[pipeline_id]
                        pipeline_name = self.humanize_name(pipeline.get('name', pipeline_id))
                        pipeline_desc = pipeline.get('description', '')
                        lines.append(f"    - **[{pipeline_name}](#{pipeline_id})** - {pipeline_desc}")

                        # Stages
                        if pipeline.get('stages'):
                            stage_links = []
                            for stage in pipeline['stages']:
                                stage_name = self.humanize_name(stage.get('name', stage['id']))
                                stage_links.append(f"[{stage_name}](#{stage['id']})")
                            lines.append(f"      - Stages: {', '.join(stage_links)}")

            lines.append("")

        return "\n".join(lines)

    def _generate_system_architecture(self) -> str:
        """Generate system architecture section."""
        lines = ["## System Architecture", ""]
        lines.append(self.diagram_gen.generate_system_architecture(
            self.system, self.domains, self.pipelines, self.datasets
        ))
        return "\n".join(lines)

    def _generate_domains_section(self) -> str:
        """Generate domains section with pipelines and stages."""
        lines = ["## Domains", ""]

        for domain_id in self.system.get('domains', []):
            if domain_id not in self.domains:
                continue

            domain = self.domains[domain_id]
            lines.append(self._generate_domain_section(domain))
            lines.append("")

        return "\n".join(lines)

    def _generate_domain_section(self, domain: dict) -> str:
        """Generate individual domain section."""
        domain_id = domain['id']
        domain_name = self.humanize_name(domain.get('name', domain_id))

        lines = [
            f"### <a id=\"{domain_id}\"></a>{domain_name}",
            "",
            f"**ID**: `{domain_id}`"
        ]

        if domain.get('description'):
            lines.append(f"**Description**: {domain['description']}")

        if domain.get('owners'):
            owner_names = [f"{o.get('team', 'Unknown')} ({o.get('contact', 'N/A')})"
                          for o in domain['owners']]
            lines.append(f"**Owners**: {', '.join(owner_names)}")

        # Summary
        pipeline_ids = domain.get('pipelines', [])
        pipeline_count = len(pipeline_ids)

        # Count unique datasets
        unique_datasets = set()
        for pip_id in pipeline_ids:
            if pip_id in self.pipelines:
                pipeline = self.pipelines[pip_id]
                for stage in pipeline.get('stages', []):
                    unique_datasets.update(stage.get('inputs', []))
                    unique_datasets.update(stage.get('outputs', []))

        lines.extend([
            "",
            "#### Summary",
            "",
            "| Metric | Count |",
            "|--------|-------|",
            f"| Pipelines | {pipeline_count} |",
            f"| Datasets Referenced | {len(unique_datasets)} |",
            ""
        ])

        # Pipelines table
        if pipeline_ids:
            lines.extend([
                "#### Pipelines",
                "",
                "| Pipeline | Mode | Schedule Type | Stages | Input Datasets | Output Datasets |",
                "|----------|------|---------------|--------|----------------|-----------------|"
            ])

            for pip_id in pipeline_ids:
                if pip_id in self.pipelines:
                    pipeline = self.pipelines[pip_id]
                    pip_name = self.humanize_name(pipeline.get('name', pip_id))
                    mode = pipeline.get('mode', 'N/A')
                    schedule_type = pipeline.get('schedule', {}).get('type', 'N/A')
                    stage_count = len(pipeline.get('stages', []))

                    # Count inputs and outputs
                    inputs = set()
                    outputs = set()
                    for stage in pipeline.get('stages', []):
                        inputs.update(stage.get('inputs', []))
                        outputs.update(stage.get('outputs', []))

                    lines.append(
                        f"| [{pip_name}](#{pip_id}) | {mode} | {schedule_type} | "
                        f"{stage_count} | {len(inputs)} | {len(outputs)} |"
                    )

            lines.append("")

        # Detailed pipeline sections
        for pip_id in pipeline_ids:
            if pip_id in self.pipelines:
                lines.append(self._generate_pipeline_section(self.pipelines[pip_id], domain_id))
                lines.append("")

        return "\n".join(lines)

    def _generate_pipeline_section(self, pipeline: dict, domain_id: str) -> str:
        """Generate detailed pipeline documentation."""
        pip_id = pipeline['id']
        pip_name = self.humanize_name(pipeline.get('name', pip_id))

        lines = [
            f"#### <a id=\"{pip_id}\"></a>Pipeline: {pip_name}",
            "",
            f"**ID**: `{pip_id}`",
            f"**Mode**: {pipeline.get('mode', 'N/A')}"
        ]

        if pipeline.get('description'):
            lines.append(f"**Description**: {pipeline['description']}")

        if pipeline.get('traits'):
            lines.append(f"**Traits**: {', '.join(pipeline['traits'])}")

        if pipeline.get('tags'):
            lines.append(f"**Tags**: {', '.join(pipeline['tags'])}")

        # Schedule
        if pipeline.get('schedule'):
            lines.append("")
            lines.append(self._generate_schedule_section(pipeline['schedule']))

        # Pipeline flow diagram
        lines.extend([
            "",
            "##### Pipeline Flow",
            "",
            self.diagram_gen.generate_pipeline_flow(pipeline, self.datasets)
        ])

        # Stages
        if pipeline.get('stages'):
            lines.extend(["", "##### Stages", ""])
            for stage in pipeline['stages']:
                lines.append(self._generate_stage_section(stage))
                lines.append("")

        return "\n".join(lines)

    def _generate_schedule_section(self, schedule: dict) -> str:
        """Generate schedule section."""
        lines = [
            "##### Schedule",
            "",
            f"- **Type**: {schedule.get('type', 'N/A')}",
            f"- **Schedule ID**: `{schedule.get('id', 'N/A')}`"
        ]

        if schedule.get('cron_expression'):
            lines.append(f"- **Cron Expression**: `{schedule['cron_expression']}`")

        if schedule.get('interval_minutes'):
            lines.append(f"- **Interval**: {schedule['interval_minutes']} minutes")

        if schedule.get('triggers'):
            lines.append("- **Triggers**:")
            for trigger in schedule['triggers']:
                trigger_type = trigger.get('type', 'unknown')
                source = trigger.get('source', 'N/A')
                lines.append(f"  - {trigger_type} (source: {source})")

        return "\n".join(lines)

    def _generate_stage_section(self, stage: dict) -> str:
        """Generate stage documentation."""
        stage_id = stage['id']
        stage_name = self.humanize_name(stage.get('name', stage_id))

        lines = [
            f"###### <a id=\"{stage_id}\"></a>Stage: {stage_name}",
            "",
            f"**ID**: `{stage_id}`"
        ]

        if stage.get('description'):
            lines.append(f"**Description**: {stage['description']}")

        if stage.get('uses_patterns'):
            lines.append(f"**Patterns Used**: {', '.join(stage['uses_patterns'])}")

        if stage.get('depends_on'):
            dep_links = []
            for dep_id in stage['depends_on']:
                dep_links.append(f"`{dep_id}`")
            lines.append(f"**Depends On**: {', '.join(dep_links)}")

        # Input datasets
        if stage.get('inputs'):
            lines.extend(["", "**Input Datasets**:"])
            for ds_id in stage['inputs']:
                ds_name = self._get_dataset_name(ds_id)
                lines.append(f"- [{ds_name}](#{ds_id}) (`{ds_id}`)")

        # Output datasets
        if stage.get('outputs'):
            lines.extend(["", "**Output Datasets**:"])
            for ds_id in stage['outputs']:
                ds_name = self._get_dataset_name(ds_id)
                lines.append(f"- [{ds_name}](#{ds_id}) (`{ds_id}`)")

        # Transforms
        if stage.get('transforms'):
            lines.extend([
                "",
                "**Transforms**:",
                "",
                "| Transform ID | Type | Description | Configuration |",
                "|--------------|------|-------------|---------------|"
            ])

            for transform in stage['transforms']:
                trf_id = transform.get('id', 'N/A')
                trf_type = transform.get('type', 'N/A')
                trf_desc = transform.get('description', '')

                # Extract key config params
                config = transform.get('config', {})
                config_summary = self._summarize_config(config)

                lines.append(f"| `{trf_id}` | {trf_type} | {trf_desc} | {config_summary} |")

        return "\n".join(lines)

    def _generate_datasets_section(self) -> str:
        """Generate datasets section."""
        if not self.datasets:
            return "## Datasets\n\n*No datasets defined*"

        lines = [
            "## Datasets",
            "",
            "| Dataset | Type | Format | Location | Classification | Contains PII | Tags |",
            "|---------|------|--------|----------|----------------|--------------|------|"
        ]

        for ds_id, dataset in self.datasets.items():
            ds_name = self.humanize_name(dataset.get('name', ds_id))
            ds_type = dataset.get('type', 'N/A')
            ds_format = dataset.get('format', 'N/A')
            location = dataset.get('location', 'N/A')
            classification = dataset.get('classification', 'N/A')
            has_pii = "Yes" if dataset.get('contains_pii') else "No"
            tags = ', '.join(dataset.get('tags', []))

            lines.append(
                f"| [{ds_name}](#{ds_id}) | {ds_type} | {ds_format} | "
                f"`{location}` | {classification} | {has_pii} | {tags} |"
            )

        lines.append("")

        # Detailed dataset sections
        for ds_id, dataset in self.datasets.items():
            lines.append(self._generate_dataset_detail(dataset))
            lines.append("")

        return "\n".join(lines)

    def _generate_dataset_detail(self, dataset: dict) -> str:
        """Generate detailed dataset documentation."""
        ds_id = dataset['id']
        ds_name = self.humanize_name(dataset.get('name', ds_id))

        lines = [
            f"### <a id=\"{ds_id}\"></a>{ds_name}",
            "",
            f"**ID**: `{ds_id}`",
            f"**Type**: {dataset.get('type', 'N/A')}",
            f"**Format**: {dataset.get('format', 'N/A')}",
            f"**Location**: `{dataset.get('location', 'N/A')}`",
            f"**Classification**: {dataset.get('classification', 'N/A')}",
            f"**Contains PII**: {'Yes' if dataset.get('contains_pii') else 'No'}"
        ]

        if dataset.get('pii_fields'):
            lines.append(f"**PII Fields**: {', '.join(dataset['pii_fields'])}")

        if dataset.get('tags'):
            lines.append(f"**Tags**: {', '.join(dataset['tags'])}")

        # Schema
        schema = dataset.get('schema', {})
        if schema.get('fields'):
            lines.extend([
                "",
                "#### Schema",
                "",
                "| Field | Type | Nullable | PII | Description |",
                "|-------|------|----------|-----|-------------|"
            ])

            for field in schema['fields']:
                field_name = field.get('name', 'N/A')
                field_type = field.get('type', 'N/A')
                nullable = "Yes" if field.get('nullable', True) else "No"
                pii = "Yes" if field.get('pii', False) else "No"
                description = field.get('description', '-')

                lines.append(f"| `{field_name}` | {field_type} | {nullable} | {pii} | {description} |")

        # Partitioning
        if dataset.get('partitioning'):
            part = dataset['partitioning']
            lines.extend(["", "#### Partitioning", ""])

            if part.get('columns'):
                lines.append(f"- **Columns**: {', '.join(part['columns'])}")

            if part.get('strategy'):
                lines.append(f"- **Strategy**: {part['strategy']}")

            if part.get('strategy_ref'):
                lines.append(f"- **Strategy Reference**: `{part['strategy_ref']}`")

        # Quality dimensions
        if dataset.get('quality_dimensions'):
            lines.extend(["", "#### Quality Dimensions", ""])
            for qd_id in dataset['quality_dimensions']:
                lines.append(f"- `{qd_id}`")

        return "\n".join(lines)

    def _generate_contracts_section(self) -> str:
        """Generate data contracts section."""
        if not self.contracts:
            return "## Data Contracts\n\n*No contracts defined*"

        lines = [
            "## Data Contracts",
            "",
            "| Contract | Dataset | Version | Owners | Consumers | SLA Freshness | SLA Completeness |",
            "|----------|---------|---------|--------|-----------|---------------|------------------|"
        ]

        for contract in self.contracts:
            ctr_id = contract['id']
            ctr_name = self.humanize_name(contract.get('name', ctr_id))
            ds_id = contract.get('dataset', 'N/A')
            ds_name = self._get_dataset_name(ds_id)
            version = contract.get('version', 'N/A')

            owner_count = len(contract.get('owners', []))
            owner_teams = ', '.join([o.get('team', 'Unknown') for o in contract.get('owners', [])])

            consumer_count = len(contract.get('consumers', []))

            sla = contract.get('sla', {})
            freshness = f"{sla.get('freshness_minutes', 'N/A')}m" if sla.get('freshness_minutes') else 'N/A'
            completeness = f"{sla.get('completeness_percent', 'N/A')}%" if sla.get('completeness_percent') else 'N/A'

            lines.append(
                f"| [{ctr_name}](#{ctr_id}) | [{ds_name}](#{ds_id}) | {version} | "
                f"{owner_teams} | {consumer_count} | {freshness} | {completeness} |"
            )

        lines.append("")

        # Detailed contract sections
        for contract in self.contracts:
            lines.append(self._generate_contract_detail(contract))
            lines.append("")

        return "\n".join(lines)

    def _generate_contract_detail(self, contract: dict) -> str:
        """Generate detailed contract documentation."""
        ctr_id = contract['id']
        ctr_name = self.humanize_name(contract.get('name', ctr_id))
        ds_id = contract.get('dataset', 'N/A')
        ds_name = self._get_dataset_name(ds_id)

        lines = [
            f"### <a id=\"{ctr_id}\"></a>{ctr_name}",
            "",
            f"**ID**: `{ctr_id}`",
            f"**Dataset**: [{ds_name}](#{ds_id})",
            f"**Version**: {contract.get('version', 'N/A')}"
        ]

        if contract.get('evolution_policy'):
            lines.append(f"**Evolution Policy**: {contract['evolution_policy']}")

        if contract.get('schema', {}).get('$ref'):
            lines.append(f"**Schema Reference**: `{contract['schema']['$ref']}`")

        # SLA
        sla = contract.get('sla', {})
        if sla:
            lines.extend(["", "#### SLA", ""])
            if sla.get('freshness_minutes') is not None:
                lines.append(f"- **Freshness**: {sla['freshness_minutes']} minutes")
            if sla.get('completeness_percent') is not None:
                lines.append(f"- **Completeness**: {sla['completeness_percent']}%")
            if sla.get('availability_percent') is not None:
                lines.append(f"- **Availability**: {sla['availability_percent']}%")

        # Owners
        if contract.get('owners'):
            lines.extend(["", "#### Owners", ""])
            for owner in contract['owners']:
                team = owner.get('team', 'Unknown')
                contact = owner.get('contact', 'N/A')
                lines.append(f"- **{team}** ({contact})")

        # Consumers
        if contract.get('consumers'):
            lines.extend(["", "#### Consumers", ""])
            for consumer in contract['consumers']:
                team = consumer.get('team', 'Unknown')
                use_case = consumer.get('use_case', 'N/A')
                lines.append(f"- **{team}** - {use_case}")

        return "\n".join(lines)

    def _generate_checks_section(self) -> str:
        """Generate data quality checks section."""
        if not self.checks:
            return "## Data Quality Checks\n\n*No checks defined*"

        lines = [
            "## Data Quality Checks",
            "",
            "| Check | Type | Dataset | Severity | Alert Channel | Threshold |",
            "|-------|------|---------|----------|---------------|-----------|"
        ]

        for check in self.checks:
            chk_id = check['id']
            chk_name = self.humanize_name(check.get('name', chk_id))
            chk_type = check.get('type', 'N/A')
            ds_id = check.get('dataset', 'N/A')
            ds_name = self._get_dataset_name(ds_id)
            severity = check.get('severity', 'N/A')
            alert_channel = check.get('alert', {}).get('channel', 'N/A')

            # Threshold summary
            threshold = check.get('threshold', {})
            threshold_summary = self._summarize_config(threshold)

            lines.append(
                f"| [{chk_name}](#{chk_id}) | {chk_type} | [{ds_name}](#{ds_id}) | "
                f"{severity} | {alert_channel} | {threshold_summary} |"
            )

        lines.append("")

        # Detailed check sections
        for check in self.checks:
            lines.append(self._generate_check_detail(check))
            lines.append("")

        return "\n".join(lines)

    def _generate_check_detail(self, check: dict) -> str:
        """Generate detailed check documentation."""
        chk_id = check['id']
        chk_name = self.humanize_name(check.get('name', chk_id))
        ds_id = check.get('dataset', 'N/A')
        ds_name = self._get_dataset_name(ds_id)

        lines = [
            f"### <a id=\"{chk_id}\"></a>{chk_name}",
            "",
            f"**ID**: `{chk_id}`",
            f"**Type**: {check.get('type', 'N/A')}",
            f"**Dataset**: [{ds_name}](#{ds_id})",
            f"**Severity**: {check.get('severity', 'N/A')}"
        ]

        # Threshold
        threshold = check.get('threshold', {})
        if threshold:
            lines.extend(["", "#### Threshold", ""])
            for key, value in threshold.items():
                lines.append(f"- **{self.humanize_name(key)}**: {value}")

        # Assertions
        if check.get('assertions'):
            lines.extend(["", "#### Assertions", ""])
            for assertion in check['assertions']:
                condition = assertion.get('condition', 'N/A')
                description = assertion.get('description', '')
                if description:
                    lines.append(f"- **{description}**: `{condition}`")
                else:
                    lines.append(f"- `{condition}`")

        # Alert configuration
        alert = check.get('alert', {})
        if alert:
            lines.extend(["", "#### Alert Configuration", ""])
            lines.append(f"- **Channel**: {alert.get('channel', 'N/A')}")
            if alert.get('escalation'):
                lines.append(f"- **Escalation**: {alert['escalation']}")

        return "\n".join(lines)

    def _generate_lineage_section(self) -> str:
        """Generate lineage section with diagram and table."""
        if not self.lineage:
            return "## Data Lineage\n\n*No lineage defined*"

        lines = [
            "## Data Lineage",
            "",
            self.diagram_gen.generate_lineage_diagram(self.lineage, self.datasets),
            "",
            "| Upstream Dataset | Downstream Dataset | Transform | Relationship |",
            "|------------------|-------------------|-----------|--------------|"
        ]

        for lin in self.lineage:
            up_id = lin.get('upstream', 'N/A')
            down_id = lin.get('downstream', 'N/A')
            up_name = self._get_dataset_name(up_id)
            down_name = self._get_dataset_name(down_id)
            transform = lin.get('transform', 'N/A')
            relationship = lin.get('relationship', 'N/A')

            lines.append(
                f"| [{up_name}](#{up_id}) | [{down_name}](#{down_id}) | "
                f"`{transform}` | {relationship} |"
            )

        return "\n".join(lines)

    def _generate_governance_section(self) -> str:
        """Generate governance section."""
        if not self.governance:
            return "## Governance\n\n*No governance policies defined*"

        lines = ["## Governance", ""]

        # Retention
        if self.governance.get('retention'):
            lines.extend(["### Retention Policies", ""])
            lines.extend([
                "| Dataset | Policy | Duration |",
                "|---------|--------|----------|"
            ])

            for policy in self.governance['retention']:
                ds_id = policy.get('dataset', 'N/A')
                ds_name = self._get_dataset_name(ds_id)
                pol_type = policy.get('policy', 'N/A')

                duration = ''
                if policy.get('days'):
                    duration = f"{policy['days']} days"
                elif policy.get('years'):
                    duration = f"{policy['years']} years"
                else:
                    duration = 'Indefinitely' if pol_type == 'retain-indefinitely' else 'N/A'

                lines.append(f"| [{ds_name}](#{ds_id}) | {pol_type} | {duration} |")

            lines.append("")

        # Access control
        if self.governance.get('access'):
            lines.extend(["### Access Control", ""])
            lines.extend([
                "| Dataset | Tier | Roles |",
                "|---------|------|-------|"
            ])

            for policy in self.governance['access']:
                ds_id = policy.get('dataset', 'N/A')
                ds_name = self._get_dataset_name(ds_id)
                tier = policy.get('tier', 'N/A')
                roles = ', '.join(policy.get('roles', []))

                lines.append(f"| [{ds_name}](#{ds_id}) | {tier} | {roles} |")

            lines.append("")

        # PII handling
        if self.governance.get('pii_handling'):
            lines.extend(["### PII Handling", ""])
            lines.extend([
                "| Dataset | Masked Fields | Masking Method |",
                "|---------|---------------|----------------|"
            ])

            for policy in self.governance['pii_handling']:
                ds_id = policy.get('dataset', 'N/A')
                ds_name = self._get_dataset_name(ds_id)
                masked_fields = ', '.join(policy.get('masking', []))
                masking_method = policy.get('masking_method', 'N/A')

                lines.append(f"| [{ds_name}](#{ds_id}) | {masked_fields} | {masking_method} |")

            lines.append("")

        return "\n".join(lines)

    def _generate_observability_section(self) -> str:
        """Generate observability section."""
        if not self.observability:
            return "## Observability\n\n*No observability configuration defined*"

        lines = ["## Observability", ""]

        # Metrics
        if self.observability.get('metrics'):
            lines.extend(["### Metrics", ""])
            lines.extend([
                "| Metric | Dataset | Type | Description |",
                "|--------|---------|------|-------------|"
            ])

            for metric in self.observability['metrics']:
                name = metric.get('name', 'N/A')
                ds_id = metric.get('dataset', '')
                ds_name = self._get_dataset_name(ds_id) if ds_id else 'N/A'
                ds_link = f"[{ds_name}](#{ds_id})" if ds_id else 'N/A'
                metric_type = metric.get('type', 'N/A')
                description = metric.get('description', '')

                lines.append(f"| {name} | {ds_link} | {metric_type} | {description} |")

            lines.append("")

        # SLOs
        if self.observability.get('slos'):
            lines.extend(["### Service Level Objectives (SLOs)", ""])
            lines.extend([
                "| SLO | Target | Unit | Window | Linked Check |",
                "|-----|--------|------|--------|--------------|"
            ])

            for slo in self.observability['slos']:
                name = slo.get('name', 'N/A')
                target = slo.get('target', 'N/A')
                unit = slo.get('unit', 'N/A')
                window = slo.get('window', 'N/A')

                linked_check = slo.get('linked_check', '')
                check_link = f"[Check](#{linked_check})" if linked_check else 'N/A'

                lines.append(f"| {name} | {target} | {unit} | {window} | {check_link} |")

            lines.append("")

        # Alerts
        if self.observability.get('alerts'):
            lines.extend(["### Alerts", ""])
            lines.extend([
                "| Alert | Condition | Severity | Channel |",
                "|-------|-----------|----------|---------|"
            ])

            for alert in self.observability['alerts']:
                name = alert.get('name', 'N/A')
                condition = alert.get('condition', 'N/A')
                severity = alert.get('severity', 'N/A')
                channel = alert.get('channel', 'N/A')

                lines.append(f"| {name} | `{condition}` | {severity} | {channel} |")

            lines.append("")

        return "\n".join(lines)

    def _get_dataset_name(self, dataset_id: str) -> str:
        """Get humanized dataset name by ID."""
        if dataset_id in self.datasets:
            return self.humanize_name(self.datasets[dataset_id].get('name', dataset_id))
        return dataset_id

    def _summarize_config(self, config: dict) -> str:
        """Summarize configuration as compact string."""
        if not config:
            return '-'

        # Show first 2-3 important keys
        items = []
        for key, value in list(config.items())[:3]:
            if isinstance(value, (list, dict)):
                items.append(f"{key}: {type(value).__name__}")
            else:
                items.append(f"{key}: {value}")

        result = ', '.join(items)
        if len(config) > 3:
            result += ', ...'

        return result

    def humanize_name(self, name: str) -> str:
        """
        Convert entity names to human-readable format.
        Examples:
            UserEvents -> User Events
            user-events -> User Events
            User Event Features -> User Event Features
        """
        if not name:
            return ""

        # If already has spaces, return as-is
        if ' ' in name:
            return name

        # Handle kebab-case
        if '-' in name:
            return ' '.join(word.capitalize() for word in name.split('-'))

        # Handle PascalCase/camelCase
        result = []
        for i, char in enumerate(name):
            if i > 0 and char.isupper():
                # Check if previous char is lowercase or next char is lowercase
                prev_is_lower = name[i-1].islower()
                next_is_lower = i < len(name) - 1 and name[i+1].islower()

                if prev_is_lower or next_is_lower:
                    result.append(' ')
            result.append(char)

        return ''.join(result)
