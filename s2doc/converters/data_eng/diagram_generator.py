"""Generate Mermaid diagrams for data engineering documentation."""

from typing import Dict, List, Any


class DiagramGenerator:
    """Generate Mermaid diagrams for data engineering documentation."""

    def generate_system_architecture(self, system: dict, domains: dict,
                                     pipelines: dict, datasets: dict) -> str:
        """Generate system architecture diagram showing hierarchy."""
        lines = ["```mermaid", "graph TB"]

        sys_id = system.get('id', 'sys')
        sys_name = system.get('name', 'System')
        lines.append(f'    {self._clean_id(sys_id)}["{sys_name}"]')
        lines.append("")

        # Domains
        domain_ids = system.get('domains', [])
        if domain_ids:
            lines.append("    subgraph Domains")
            for dom_id in domain_ids:
                if dom_id in domains:
                    domain = domains[dom_id]
                    dom_name = domain.get('name', dom_id)
                    lines.append(f'        {self._clean_id(dom_id)}["{dom_name}"]')
            lines.append("    end")
            lines.append("")

        # Pipelines (collect all)
        all_pipeline_ids = []
        for dom_id in domain_ids:
            if dom_id in domains:
                all_pipeline_ids.extend(domains[dom_id].get('pipelines', []))

        if all_pipeline_ids:
            lines.append("    subgraph Pipelines")
            for pip_id in all_pipeline_ids[:10]:  # Limit to first 10 for readability
                if pip_id in pipelines:
                    pipeline = pipelines[pip_id]
                    pip_name = pipeline.get('name', pip_id)
                    lines.append(f'        {self._clean_id(pip_id)}["{pip_name}"]')
            if len(all_pipeline_ids) > 10:
                lines.append(f'        MORE["... {len(all_pipeline_ids) - 10} more pipelines"]')
            lines.append("    end")
            lines.append("")

        # Key datasets (limit to those with most references)
        dataset_refs = {}
        for pip_id, pipeline in pipelines.items():
            for stage in pipeline.get('stages', []):
                for ds_id in stage.get('inputs', []) + stage.get('outputs', []):
                    dataset_refs[ds_id] = dataset_refs.get(ds_id, 0) + 1

        # Top 10 most referenced datasets
        top_datasets = sorted(dataset_refs.items(), key=lambda x: x[1], reverse=True)[:10]

        if top_datasets:
            lines.append("    subgraph Datasets")
            for ds_id, _ in top_datasets:
                if ds_id in datasets:
                    dataset = datasets[ds_id]
                    ds_name = dataset.get('name', ds_id)
                    lines.append(f'        {self._clean_id(ds_id)}["{ds_name}"]')
            lines.append("    end")
            lines.append("")

        # Relationships
        # System -> Domains
        for dom_id in domain_ids:
            if dom_id in domains:
                lines.append(f"    {self._clean_id(sys_id)} --> {self._clean_id(dom_id)}")

        # Domains -> Pipelines
        for dom_id in domain_ids:
            if dom_id in domains:
                for pip_id in domains[dom_id].get('pipelines', [])[:5]:  # First 5 per domain
                    if pip_id in pipelines:
                        lines.append(f"    {self._clean_id(dom_id)} --> {self._clean_id(pip_id)}")

        # Pipelines -> Datasets (show a few examples)
        example_count = 0
        for pip_id in all_pipeline_ids[:5]:  # First 5 pipelines
            if pip_id in pipelines:
                pipeline = pipelines[pip_id]
                for stage in pipeline.get('stages', [])[:2]:  # First 2 stages
                    for ds_id in stage.get('inputs', [])[:2]:  # First 2 inputs
                        if ds_id in [d[0] for d in top_datasets]:
                            lines.append(f"    {self._clean_id(pip_id)} -->|reads| {self._clean_id(ds_id)}")
                            example_count += 1
                            if example_count >= 5:
                                break
                    for ds_id in stage.get('outputs', [])[:2]:  # First 2 outputs
                        if ds_id in [d[0] for d in top_datasets]:
                            lines.append(f"    {self._clean_id(pip_id)} -->|writes| {self._clean_id(ds_id)}")
                            example_count += 1
                            if example_count >= 5:
                                break
                    if example_count >= 5:
                        break

        lines.append("")

        # Styling
        lines.append(f"    style {self._clean_id(sys_id)} fill:#e1f5ff")
        for dom_id in domain_ids:
            if dom_id in domains:
                lines.append(f"    style {self._clean_id(dom_id)} fill:#b3e0ff")
        for pip_id in all_pipeline_ids[:10]:
            if pip_id in pipelines:
                lines.append(f"    style {self._clean_id(pip_id)} fill:#80ccff")
        for ds_id, _ in top_datasets:
            if ds_id in datasets:
                lines.append(f"    style {self._clean_id(ds_id)} fill:#ffe6cc")

        lines.append("```")
        return "\n".join(lines)

    def generate_pipeline_flow(self, pipeline: dict, datasets: dict) -> str:
        """Generate pipeline flow diagram with stages and data flows."""
        lines = ["```mermaid", "graph LR"]

        stages = pipeline.get('stages', [])

        # Define all stages
        for i, stage in enumerate(stages):
            stage_id = stage.get('id', f'stg{i}')
            stage_name = stage.get('name', stage_id)
            lines.append(f'    {self._clean_id(stage_id)}["{stage_name}"]')

        lines.append("")

        # Define datasets
        all_datasets = set()
        for stage in stages:
            all_datasets.update(stage.get('inputs', []))
            all_datasets.update(stage.get('outputs', []))

        for ds_id in all_datasets:
            ds_name = datasets.get(ds_id, {}).get('name', ds_id) if ds_id in datasets else ds_id
            lines.append(f'    {self._clean_id(ds_id)}["{ds_name}"]')

        lines.append("")

        # Input/Output flows
        for stage in stages:
            stage_id = stage.get('id', 'stg')

            # Inputs
            for ds_id in stage.get('inputs', []):
                lines.append(f"    {self._clean_id(ds_id)} --> {self._clean_id(stage_id)}")

            # Outputs
            for ds_id in stage.get('outputs', []):
                lines.append(f"    {self._clean_id(stage_id)} --> {self._clean_id(ds_id)}")

        # Stage dependencies
        for stage in stages:
            stage_id = stage.get('id', 'stg')
            for dep_id in stage.get('depends_on', []):
                lines.append(f"    {self._clean_id(dep_id)} -.->|depends| {self._clean_id(stage_id)}")

        lines.append("")

        # Styling
        for stage in stages:
            stage_id = stage.get('id', 'stg')
            lines.append(f"    style {self._clean_id(stage_id)} fill:#80ccff")

        for ds_id in all_datasets:
            lines.append(f"    style {self._clean_id(ds_id)} fill:#ffe6cc")

        lines.append("```")
        return "\n".join(lines)

    def generate_lineage_diagram(self, lineage: List[dict], datasets: dict) -> str:
        """Generate data lineage diagram."""
        lines = ["```mermaid", "graph LR"]

        # Collect all unique datasets in lineage
        all_datasets = set()
        for lin in lineage:
            all_datasets.add(lin.get('upstream'))
            all_datasets.add(lin.get('downstream'))

        # Define dataset nodes
        for ds_id in all_datasets:
            if ds_id and ds_id in datasets:
                ds_name = datasets[ds_id].get('name', ds_id)
                lines.append(f'    {self._clean_id(ds_id)}["{ds_name}"]')

        lines.append("")

        # Define lineage relationships
        for i, lin in enumerate(lineage):
            up_id = lin.get('upstream')
            down_id = lin.get('downstream')
            transform = lin.get('transform', '')
            relationship = lin.get('relationship', '')

            if up_id and down_id:
                label = f"{transform}<br/>{relationship}" if transform and relationship else (transform or relationship or '')
                if label:
                    lines.append(f'    {self._clean_id(up_id)} -->|{label}| {self._clean_id(down_id)}')
                else:
                    lines.append(f'    {self._clean_id(up_id)} --> {self._clean_id(down_id)}')

        lines.append("")

        # Styling
        for ds_id in all_datasets:
            if ds_id:
                lines.append(f"    style {self._clean_id(ds_id)} fill:#ffe6cc")

        lines.append("```")
        return "\n".join(lines)

    def _clean_id(self, id_str: str) -> str:
        """Clean ID for use in Mermaid diagrams."""
        if not id_str:
            return "UNKNOWN"
        # Replace hyphens with underscores for Mermaid compatibility
        return id_str.replace('-', '_')
