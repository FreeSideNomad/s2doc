"""
Domain Stories to Markdown Converter (Single File Only)
Converts YAML domain stories to a single structured markdown file with embedded Mermaid diagrams.
"""

import yaml
from pathlib import Path
from typing import Dict, List, Any, Optional
from collections import defaultdict
from .diagram_renderer import DiagramRenderer


class DomainStoryConverter:
    """Converts domain stories YAML to a single markdown file with Mermaid diagrams."""

    def __init__(self, yaml_file: str):
        self.yaml_file = yaml_file

        with open(yaml_file, 'r') as f:
            self.data = yaml.safe_load(f)

        self.stories = self.data.get('domain_stories', [])
        self.diagram_renderer: Optional[DiagramRenderer] = None

    def convert(self, output_path: str) -> str:
        """
        Convert all domain stories to a single markdown file with navigation.

        Args:
            output_path: Path where the markdown file will be written

        Returns:
            Path to the generated markdown file
        """
        output_path = Path(output_path)

        # Initialize diagram renderer with images directory
        images_dir = output_path.parent / f"{output_path.stem}_images"
        self.diagram_renderer = DiagramRenderer(images_dir)

        print(f"Converting {len(self.stories)} domain stories to single file...")

        md = []

        # Header
        md.append("# Domain Stories - Complete Documentation\n\n")
        md.append(f"**Total Stories**: {len(self.stories)}  \n")
        md.append(f"**Version**: {self.data.get('version', 'N/A')}  \n")
        md.append("\n---\n\n")

        # Main Table of Contents
        md.append("## 📑 Table of Contents\n\n")
        md.append("### Quick Navigation\n")
        md.append("- [Stories by Tag](#stories-by-tag)\n")
        md.append("- [All Stories](#all-stories)\n")
        md.append("- [Actor Catalog](#actor-catalog)\n")
        md.append("- [Aggregate Catalog](#aggregate-catalog)\n")
        md.append("- [Command Catalog](#command-catalog)\n")
        md.append("\n")

        # Stories by Tag
        md.append("### Stories by Tag\n\n")
        stories_by_tag = defaultdict(list)
        for story in self.stories:
            tags = story.get('tags', [])
            if not tags:
                stories_by_tag['untagged'].append(story)
            else:
                for tag in tags:
                    stories_by_tag[tag].append(story)

        for tag in sorted(stories_by_tag.keys()):
            stories = stories_by_tag[tag]
            tag_display = tag.replace('_', ' ').title()
            md.append(f"#### {tag_display} ({len(stories)})\n")
            for story in stories:
                story_id = story.get('domain_story_id', 'unknown')
                title = story.get('title', 'Untitled')
                md.append(f"- [{title}](#{story_id})\n")
            md.append("\n")

        md.append("\n---\n\n")

        # All Stories Section
        md.append("## All Stories\n\n")
        md.append("| # | Story ID | Title | Tags |\n")
        md.append("|---|----------|-------|------|\n")
        for idx, story in enumerate(self.stories, 1):
            story_id = story.get('domain_story_id', 'unknown')
            title = story.get('title', 'Untitled')
            tags = ', '.join(story.get('tags', []))
            md.append(f"| {idx} | [{story_id}](#{story_id}) | {title} | {tags} |\n")

        md.append("\n---\n\n")

        # Individual Stories
        for idx, story in enumerate(self.stories, 1):
            print(f"  [{idx}/{len(self.stories)}] {story.get('title', 'Untitled')}")
            md.extend(self._generate_story_content(story))
            md.append("\n---\n\n")

        # Actor Catalog
        md.append("## Actor Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self._generate_actor_catalog())
        md.append("\n---\n\n")

        # Aggregate Catalog
        md.append("## Aggregate Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self._generate_aggregate_catalog())
        md.append("\n---\n\n")

        # Command Catalog
        md.append("## Command Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self._generate_command_catalog())

        # Write single file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(''.join(md))

        print(f"\n✓ Conversion complete! Output: {output_path}")
        return str(output_path)

    def create_docx_markdown(self, source_md_path: str, output_md_path: str) -> str:
        """
        Create a DOCX-specific markdown by replacing Mermaid blocks with PNG images.

        Args:
            source_md_path: Path to the source markdown file (with Mermaid)
            output_md_path: Path where DOCX-specific markdown will be written

        Returns:
            Path to the DOCX-specific markdown file
        """
        source_path = Path(source_md_path)
        output_path = Path(output_md_path)

        with open(source_path, 'r') as f:
            content = f.read()

        # Replace Mermaid code blocks with image references
        # Pattern: ```mermaid\nsequenceDiagram\n...\n```
        import re

        # For each story, replace Mermaid blocks with corresponding PNG images
        for story in self.stories:
            story_id = story.get('domain_story_id', 'unknown')

            # Check if we have images for this story
            if self.diagram_renderer:
                images_dir = self.diagram_renderer.output_dir
                seq_img = images_dir / f"{story_id}_sequence.png"
                flow_img = images_dir / f"{story_id}_flow.png"

                # Make image paths relative to the output markdown location
                # Both output_md and images are in the same parent directory
                if seq_img.exists():
                    rel_seq_path = images_dir.name + "/" + seq_img.name
                    seq_pattern = rf'(#### Sequence Diagram\s*\n\s*\n)```mermaid\s*\nsequenceDiagram\s*\n.*?```\s*\n'
                    # Add width=50% to scale down high-res image in Word
                    replacement = f'\\1![Sequence Diagram]({rel_seq_path}){{width=50%}}\n\n'
                    content = re.sub(seq_pattern, replacement, content, flags=re.DOTALL, count=1)

                # Replace flow diagram Mermaid block
                if flow_img.exists():
                    rel_flow_path = images_dir.name + "/" + flow_img.name
                    flow_pattern = rf'(#### Command-Event-Policy Flow\s*\n\s*\n)```mermaid\s*\ngraph LR\s*\n.*?```\s*\n'
                    replacement = f'\\1![Flow Diagram]({rel_flow_path})\n\n'
                    content = re.sub(flow_pattern, replacement, content, flags=re.DOTALL, count=1)

        # Write DOCX-specific markdown
        output_path.parent.mkdir(parents=True, exist_ok=True)
        with open(output_path, 'w') as f:
            f.write(content)

        return str(output_path)

    def _generate_story_content(self, story: Dict[str, Any]) -> List[str]:
        """Generate markdown content for a single story."""
        story_id = story.get('domain_story_id', 'unknown')
        md = []

        # Header
        md.append(f"## {story.get('title', 'Untitled')}\n\n")
        md.append(f"<a id=\"{story_id}\"></a>\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.append(f"**Story ID**: `{story_id}`  \n")
        md.append(f"**Tags**: {', '.join(story.get('tags', []))}  \n")
        md.append("\n")

        # Description
        if story.get('description'):
            md.append(f"### Description\n\n")
            md.append(f"{story['description'].strip()}\n\n")

        # Actors
        actors = story.get('actors', [])
        if actors:
            md.append(f"### Actors\n\n")
            md.append("| Actor ID | Name | Kind | Description |\n")
            md.append("|----------|------|------|-------------|\n")
            for actor in actors:
                actor_id = actor.get('actor_id', '')
                name = actor.get('name', '')
                kind = actor.get('kind', '')
                desc = actor.get('description', '').replace('\n', ' ')
                md.append(f"| `{actor_id}` | {name} | {kind} | {desc} |\n")
            md.append("\n")

        # Work Objects & Aggregates
        work_objects = story.get('work_objects', [])
        aggregates = story.get('aggregates', [])

        if work_objects or aggregates:
            md.append(f"### Domain Model\n\n")

            if aggregates:
                md.append(f"#### Aggregates\n\n")
                for agg in aggregates:
                    agg_id = agg.get('aggregate_id', '')
                    name = agg.get('name', '')
                    desc = agg.get('description', '')
                    md.append(f"##### {name} (`{agg_id}`)\n\n")
                    if desc:
                        md.append(f"{desc}\n\n")

                    invariants = agg.get('invariants', [])
                    if invariants:
                        md.append("**Invariants**:\n")
                        for inv in invariants:
                            md.append(f"- {inv}\n")
                        md.append("\n")

            if work_objects:
                md.append(f"#### Work Objects\n\n")
                for wobj in work_objects:
                    wobj_id = wobj.get('work_object_id', '')
                    name = wobj.get('name', '')
                    desc = wobj.get('description', '')
                    md.append(f"##### {name} (`{wobj_id}`)\n\n")
                    if desc:
                        md.append(f"{desc}\n\n")

                    attributes = wobj.get('attributes', [])
                    if attributes:
                        md.append("**Attributes**:\n\n")
                        md.append("| Name | Type | Required | Description |\n")
                        md.append("|------|------|----------|-------------|\n")
                        for attr in attributes:
                            attr_name = attr.get('name', '')
                            attr_type = attr.get('type', '')
                            required = '✓' if attr.get('required', False) else ''
                            attr_desc = attr.get('description', '').replace('\n', ' ')
                            md.append(f"| {attr_name} | {attr_type} | {required} | {attr_desc} |\n")
                        md.append("\n")

        # Commands
        commands = story.get('commands', [])
        if commands:
            md.append(f"### Commands\n\n")
            for cmd in commands:
                cmd_id = cmd.get('command_id', '')
                name = cmd.get('name', '')
                desc = cmd.get('description', '')
                md.append(f"#### {name} (`{cmd_id}`)\n\n")
                if desc:
                    md.append(f"{desc}\n\n")

                actor_ids = cmd.get('actor_ids', [])
                if actor_ids:
                    md.append(f"**Actors**: {', '.join([f'`{a}`' for a in actor_ids])}  \n")

                target_agg = cmd.get('target_aggregate_id')
                if target_agg:
                    md.append(f"**Target Aggregate**: `{target_agg}`  \n")

                events = cmd.get('emits_events', [])
                if events:
                    md.append(f"**Emits Events**: {', '.join([f'`{e}`' for e in events])}  \n")
                md.append("\n")

        # Events
        events = story.get('events', [])
        if events:
            md.append(f"### Events\n\n")
            md.append("| Event ID | Name | Description | Caused By |\n")
            md.append("|----------|------|-------------|----------|\n")
            for evt in events:
                evt_id = evt.get('event_id', '')
                name = evt.get('name', '')
                desc = evt.get('description', '').replace('\n', ' ')
                caused_by = evt.get('caused_by', {})
                caused_str = caused_by.get('command_id', caused_by.get('activity_id', ''))
                md.append(f"| `{evt_id}` | {name} | {desc} | `{caused_str}` |\n")
            md.append("\n")

        # Policies
        policies = story.get('policies', [])
        if policies:
            md.append(f"### Policies\n\n")
            md.append("| Policy ID | Name | When Event | Issues Command |\n")
            md.append("|-----------|------|------------|----------------|\n")
            for pol in policies:
                pol_id = pol.get('policy_id', '')
                name = pol.get('name', '')
                when_evt = pol.get('when_event_id', '')
                issues_cmd = pol.get('issues_command_id', '')
                md.append(f"| `{pol_id}` | {name} | `{when_evt}` | `{issues_cmd}` |\n")
            md.append("\n")

        # Generate diagrams (Mermaid for GitHub, PNG generated but not linked in main MD)
        md.append(f"### Visualizations\n\n")

        story_id = story.get('domain_story_id', 'unknown')

        # Generate PNG images (for DOCX, rendered separately)
        if self.diagram_renderer:
            self.diagram_renderer.generate_sequence_diagram(story, story_id)
            self.diagram_renderer.generate_flow_diagram(story, story_id)

        # Sequence diagram - Mermaid only for GitHub
        if commands and actors:
            md.append(f"#### Sequence Diagram\n\n")
            md.append(self._generate_mermaid_sequence(story))
            md.append("\n")

        # Command-Event-Policy flow - Mermaid only for GitHub
        if commands or events or policies:
            md.append(f"#### Command-Event-Policy Flow\n\n")
            md.append(self._generate_mermaid_flow(story))
            md.append("\n")

        return md

    def _generate_mermaid_sequence(self, story: Dict[str, Any]) -> str:
        """Generate Mermaid sequence diagram for a story."""
        lines = ["```mermaid\n", "sequenceDiagram\n"]

        actors = story.get('actors', [])
        commands = story.get('commands', [])
        events = story.get('events', [])

        # Participants
        for actor in actors:
            actor_id = actor.get('actor_id', '').replace('act_', '')
            name = actor.get('name', '')
            lines.append(f"    participant {actor_id} as {name}\n")

        # Add system if there are aggregates
        if story.get('aggregates'):
            lines.append(f"    participant System\n")

        # Interactions
        for cmd in commands[:5]:  # Limit to first 5 to avoid clutter
            actor_ids = cmd.get('actor_ids', [])
            cmd_name = cmd.get('name', '')

            if actor_ids:
                actor_short = actor_ids[0].replace('act_', '')
                lines.append(f"    {actor_short}->>+System: {cmd_name}\n")

                # Find emitted events
                emitted = cmd.get('emits_events', [])
                for evt_id in emitted[:2]:  # Limit events
                    evt = next((e for e in events if e.get('event_id') == evt_id), None)
                    if evt:
                        evt_name = evt.get('name', '')
                        lines.append(f"    System-->>-{actor_short}: {evt_name}\n")

        lines.append("```\n")
        return ''.join(lines)

    def _generate_mermaid_flow(self, story: Dict[str, Any]) -> str:
        """Generate Mermaid flowchart for command-event-policy flow."""
        lines = ["```mermaid\n", "graph LR\n"]

        commands = story.get('commands', [])
        events = story.get('events', [])
        policies = story.get('policies', [])

        # Limit to prevent diagram explosion
        max_nodes = 15
        node_count = 0

        for cmd in commands[:5]:
            if node_count >= max_nodes:
                break

            cmd_id = cmd.get('command_id', '')
            cmd_name = cmd.get('name', '')

            # Command node
            lines.append(f"    {cmd_id}[{cmd_name}]\n")
            node_count += 1

            # Events emitted by command
            for evt_id in cmd.get('emits_events', [])[:2]:
                if node_count >= max_nodes:
                    break
                evt = next((e for e in events if e.get('event_id') == evt_id), None)
                if evt:
                    evt_name = evt.get('name', '')
                    lines.append(f"    {evt_id}[{evt_name}]\n")
                    lines.append(f"    {cmd_id} -->|emits| {evt_id}\n")
                    node_count += 1

                    # Policies triggered by event
                    triggered_pols = evt.get('policies_triggered', [])
                    for pol_id in triggered_pols[:1]:
                        if node_count >= max_nodes:
                            break
                        pol = next((p for p in policies if p.get('policy_id') == pol_id), None)
                        if pol:
                            pol_name = pol.get('name', '')
                            issues_cmd = pol.get('issues_command_id', '')
                            lines.append(f"    {pol_id}{{{{{pol_name}}}}}\n")
                            lines.append(f"    {evt_id} -->|triggers| {pol_id}\n")
                            if issues_cmd:
                                lines.append(f"    {pol_id} -->|issues| {issues_cmd}\n")
                            node_count += 1

        if node_count == 0:
            lines.append("    Note[No command-event-policy flows in this story]\n")

        lines.append("```\n")
        return ''.join(lines)

    def _generate_actor_catalog(self) -> List[str]:
        """Generate actor catalog content."""
        md = []

        actors_map = {}
        for story in self.stories:
            story_id = story.get('domain_story_id', '')
            story_title = story.get('title', '')
            for actor in story.get('actors', []):
                actor_id = actor.get('actor_id', '')
                if actor_id not in actors_map:
                    actors_map[actor_id] = {
                        'name': actor.get('name', ''),
                        'kind': actor.get('kind', ''),
                        'description': actor.get('description', ''),
                        'stories': []
                    }
                actors_map[actor_id]['stories'].append((story_id, story_title))

        md.append(f"**Total Unique Actors**: {len(actors_map)}\n\n")
        md.append("| Actor ID | Name | Kind | Used in Stories |\n")
        md.append("|----------|------|------|----------------|\n")

        for actor_id in sorted(actors_map.keys()):
            actor = actors_map[actor_id]
            name = actor['name']
            kind = actor['kind']
            # Use anchor links for single file
            story_links = ', '.join([f"[{title}](#{sid})" for sid, title in actor['stories'][:3]])
            if len(actor['stories']) > 3:
                story_links += f" (+{len(actor['stories']) - 3} more)"
            md.append(f"| `{actor_id}` | {name} | {kind} | {story_links} |\n")

        return md

    def _generate_aggregate_catalog(self) -> List[str]:
        """Generate aggregate catalog content."""
        md = []

        agg_map = {}
        for story in self.stories:
            story_id = story.get('domain_story_id', '')
            story_title = story.get('title', '')
            for agg in story.get('aggregates', []):
                agg_id = agg.get('aggregate_id', '')
                if agg_id not in agg_map:
                    agg_map[agg_id] = {
                        'name': agg.get('name', ''),
                        'description': agg.get('description', ''),
                        'stories': []
                    }
                agg_map[agg_id]['stories'].append((story_id, story_title))

        md.append(f"**Total Unique Aggregates**: {len(agg_map)}\n\n")
        md.append("| Aggregate ID | Name | Used in Stories |\n")
        md.append("|--------------|------|----------------|\n")

        for agg_id in sorted(agg_map.keys()):
            agg = agg_map[agg_id]
            name = agg['name']
            # Use anchor links for single file
            story_links = ', '.join([f"[{title}](#{sid})" for sid, title in agg['stories'][:3]])
            if len(agg['stories']) > 3:
                story_links += f" (+{len(agg['stories']) - 3} more)"
            md.append(f"| `{agg_id}` | {name} | {story_links} |\n")

        return md

    def _generate_command_catalog(self) -> List[str]:
        """Generate command catalog content."""
        md = []

        cmd_map = {}
        for story in self.stories:
            story_id = story.get('domain_story_id', '')
            story_title = story.get('title', '')
            for cmd in story.get('commands', []):
                cmd_id = cmd.get('command_id', '')
                if cmd_id not in cmd_map:
                    cmd_map[cmd_id] = {
                        'name': cmd.get('name', ''),
                        'description': cmd.get('description', ''),
                        'stories': []
                    }
                cmd_map[cmd_id]['stories'].append((story_id, story_title))

        md.append(f"**Total Unique Commands**: {len(cmd_map)}\n\n")
        md.append("| Command ID | Name | Used in Stories |\n")
        md.append("|------------|------|----------------|\n")

        for cmd_id in sorted(cmd_map.keys()):
            cmd = cmd_map[cmd_id]
            name = cmd['name']
            # Use anchor links for single file
            story_links = ', '.join([f"[{title}](#{sid})" for sid, title in cmd['stories'][:3]])
            if len(cmd['stories']) > 3:
                story_links += f" (+{len(cmd['stories']) - 3} more)"
            md.append(f"| `{cmd_id}` | {name} | {story_links} |\n")

        return md
