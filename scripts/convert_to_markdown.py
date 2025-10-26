#!/usr/bin/env python3
"""
Domain Stories to Markdown Converter
Converts YAML domain stories to structured markdown with embedded Mermaid diagrams.

Usage:
    python convert_to_markdown.py cb-domain-stories.yaml output/
    python convert_to_markdown.py cb-domain-stories.yaml output/ --single-file
"""

import yaml
import os
import sys
from pathlib import Path
from typing import Dict, List, Any
from collections import defaultdict


class DomainStoryConverter:
    """Converts domain stories YAML to markdown with Mermaid diagrams."""

    def __init__(self, yaml_file: str, output_dir: str):
        self.yaml_file = yaml_file
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

        with open(yaml_file, 'r') as f:
            self.data = yaml.safe_load(f)

        self.stories = self.data.get('domain_stories', [])

    def convert_all(self):
        """Convert all domain stories to markdown."""
        print(f"Converting {len(self.stories)} domain stories...")

        # Generate index
        self.generate_index()

        # Generate per-story markdown
        for idx, story in enumerate(self.stories, 1):
            print(f"  [{idx}/{len(self.stories)}] {story.get('title', 'Untitled')}")
            self.generate_story_markdown(story, idx)

        # Generate catalogs
        self.generate_actor_catalog()
        self.generate_aggregate_catalog()
        self.generate_command_catalog()

        print(f"\n✓ Conversion complete! Output in: {self.output_dir}")

    def convert_to_single_file(self, output_file: str = "domain-stories-complete.md"):
        """Convert all domain stories to a single markdown file with navigation."""
        print(f"Converting {len(self.stories)} domain stories to single file...")

        md = []

        # Header
        md.append("# Domain Stories - Complete Documentation\n\n")
        md.append(f"**Total Stories**: {len(self.stories)}  \n")
        md.append(f"**Version**: {self.data.get('version', 'N/A')}  \n")
        md.append(f"**Generated**: {self.data.get('version', 'N/A')}  \n")
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
            md.extend(self.generate_story_content(story, idx, single_file=True))
            md.append("\n---\n\n")

        # Actor Catalog
        md.append("## Actor Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self.generate_actor_catalog_content())
        md.append("\n---\n\n")

        # Aggregate Catalog
        md.append("## Aggregate Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self.generate_aggregate_catalog_content())
        md.append("\n---\n\n")

        # Command Catalog
        md.append("## Command Catalog\n\n")
        md.append("[↑ Back to Top](#-table-of-contents)\n\n")
        md.extend(self.generate_command_catalog_content())

        # Write single file
        output_path = self.output_dir / output_file
        with open(output_path, 'w') as f:
            f.write(''.join(md))

        print(f"\n✓ Single file conversion complete! Output: {output_path}")

    def generate_index(self):
        """Generate main index file with story listings."""
        md = []
        md.append("# Domain Stories Index\n")
        md.append(f"**Total Stories**: {len(self.stories)}\n")
        md.append(f"**Version**: {self.data.get('version', 'N/A')}\n")
        md.append("---\n")

        # Group stories by tags
        stories_by_tag = defaultdict(list)
        for story in self.stories:
            tags = story.get('tags', [])
            if not tags:
                stories_by_tag['untagged'].append(story)
            else:
                for tag in tags:
                    stories_by_tag[tag].append(story)

        # Table of contents
        md.append("## Table of Contents\n")
        md.append("- [Stories by Tag](#stories-by-tag)\n")
        md.append("- [All Stories](#all-stories)\n")
        md.append("- [Actor Catalog](actors.md)\n")
        md.append("- [Aggregate Catalog](aggregates.md)\n")
        md.append("- [Command Catalog](commands.md)\n")
        md.append("\n---\n")

        # Stories by tag
        md.append("## Stories by Tag\n")
        for tag in sorted(stories_by_tag.keys()):
            stories = stories_by_tag[tag]
            md.append(f"\n### {tag.replace('_', ' ').title()} ({len(stories)})\n")
            for story in stories:
                story_id = story.get('domain_story_id', 'unknown')
                title = story.get('title', 'Untitled')
                md.append(f"- [{title}]({story_id}.md)\n")

        # All stories
        md.append("\n## All Stories\n")
        md.append("| # | Story ID | Title | Tags |\n")
        md.append("|---|----------|-------|------|\n")
        for idx, story in enumerate(self.stories, 1):
            story_id = story.get('domain_story_id', 'unknown')
            title = story.get('title', 'Untitled')
            tags = ', '.join(story.get('tags', []))
            md.append(f"| {idx} | [{story_id}]({story_id}.md) | {title} | {tags} |\n")

        # Write index
        with open(self.output_dir / 'index.md', 'w') as f:
            f.write(''.join(md))

    def generate_story_markdown(self, story: Dict[str, Any], story_num: int):
        """Generate markdown for a single story."""
        story_id = story.get('domain_story_id', 'unknown')
        md = []

        # Header
        md.append(f"# {story.get('title', 'Untitled')}\n")
        md.append(f"**Story ID**: `{story_id}`  \n")
        md.append(f"**Tags**: {', '.join(story.get('tags', []))}  \n")
        md.append("\n---\n")

        # Description
        if story.get('description'):
            md.append("## Description\n")
            md.append(f"{story['description'].strip()}\n")
            md.append("\n---\n")

        # Actors
        actors = story.get('actors', [])
        if actors:
            md.append("## Actors\n")
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
            md.append("## Domain Model\n")

            if aggregates:
                md.append("### Aggregates\n")
                for agg in aggregates:
                    agg_id = agg.get('aggregate_id', '')
                    name = agg.get('name', '')
                    desc = agg.get('description', '')
                    md.append(f"\n#### {name} (`{agg_id}`)\n")
                    if desc:
                        md.append(f"{desc}\n")

                    invariants = agg.get('invariants', [])
                    if invariants:
                        md.append("\n**Invariants**:\n")
                        for inv in invariants:
                            md.append(f"- {inv}\n")
                md.append("\n")

            if work_objects:
                md.append("### Work Objects\n")
                for wobj in work_objects:
                    wobj_id = wobj.get('work_object_id', '')
                    name = wobj.get('name', '')
                    desc = wobj.get('description', '')
                    md.append(f"\n#### {name} (`{wobj_id}`)\n")
                    if desc:
                        md.append(f"{desc}\n")

                    attributes = wobj.get('attributes', [])
                    if attributes:
                        md.append("\n**Attributes**:\n")
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
            md.append("## Commands\n")
            for cmd in commands:
                cmd_id = cmd.get('command_id', '')
                name = cmd.get('name', '')
                desc = cmd.get('description', '')
                md.append(f"\n### {name} (`{cmd_id}`)\n")
                if desc:
                    md.append(f"{desc}\n")

                actor_ids = cmd.get('actor_ids', [])
                if actor_ids:
                    md.append(f"\n**Actors**: {', '.join([f'`{a}`' for a in actor_ids])}\n")

                target_agg = cmd.get('target_aggregate_id')
                if target_agg:
                    md.append(f"**Target Aggregate**: `{target_agg}`\n")

                events = cmd.get('emits_events', [])
                if events:
                    md.append(f"**Emits Events**: {', '.join([f'`{e}`' for e in events])}\n")
            md.append("\n")

        # Events
        events = story.get('events', [])
        if events:
            md.append("## Events\n")
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
            md.append("## Policies\n")
            md.append("| Policy ID | Name | When Event | Issues Command |\n")
            md.append("|-----------|------|------------|----------------|\n")
            for pol in policies:
                pol_id = pol.get('policy_id', '')
                name = pol.get('name', '')
                when_evt = pol.get('when_event_id', '')
                issues_cmd = pol.get('issues_command_id', '')
                md.append(f"| `{pol_id}` | {name} | `{when_evt}` | `{issues_cmd}` |\n")
            md.append("\n")

        # Generate Mermaid diagrams
        md.append("## Visualizations\n")

        # Sequence diagram
        if commands and actors:
            md.append("### Sequence Diagram\n")
            md.append(self.generate_mermaid_sequence(story))
            md.append("\n")

        # Command-Event-Policy flow
        if commands or events or policies:
            md.append("### Command-Event-Policy Flow\n")
            md.append(self.generate_mermaid_flow(story))
            md.append("\n")

        # Write story file
        filename = f"{story_id}.md"
        with open(self.output_dir / filename, 'w') as f:
            f.write(''.join(md))

    def generate_story_content(self, story: Dict[str, Any], story_num: int, single_file: bool = False) -> List[str]:
        """Generate markdown content for a single story as a list of strings."""
        story_id = story.get('domain_story_id', 'unknown')
        md = []

        # Header - use H2 for single file, H1 for multi-file
        header_level = "##" if single_file else "#"
        md.append(f"{header_level} {story.get('title', 'Untitled')}\n\n")

        if single_file:
            md.append(f"<a id=\"{story_id}\"></a>\n\n")
            md.append("[↑ Back to Top](#-table-of-contents)\n\n")

        md.append(f"**Story ID**: `{story_id}`  \n")
        md.append(f"**Tags**: {', '.join(story.get('tags', []))}  \n")
        md.append("\n")

        # Description
        if story.get('description'):
            md.append(f"{header_level}# Description\n\n")
            md.append(f"{story['description'].strip()}\n\n")

        # Actors
        actors = story.get('actors', [])
        if actors:
            md.append(f"{header_level}# Actors\n\n")
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
            md.append(f"{header_level}# Domain Model\n\n")

            if aggregates:
                md.append(f"{header_level}## Aggregates\n\n")
                for agg in aggregates:
                    agg_id = agg.get('aggregate_id', '')
                    name = agg.get('name', '')
                    desc = agg.get('description', '')
                    md.append(f"{header_level}### {name} (`{agg_id}`)\n\n")
                    if desc:
                        md.append(f"{desc}\n\n")

                    invariants = agg.get('invariants', [])
                    if invariants:
                        md.append("**Invariants**:\n")
                        for inv in invariants:
                            md.append(f"- {inv}\n")
                        md.append("\n")

            if work_objects:
                md.append(f"{header_level}## Work Objects\n\n")
                for wobj in work_objects:
                    wobj_id = wobj.get('work_object_id', '')
                    name = wobj.get('name', '')
                    desc = wobj.get('description', '')
                    md.append(f"{header_level}### {name} (`{wobj_id}`)\n\n")
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
            md.append(f"{header_level}# Commands\n\n")
            for cmd in commands:
                cmd_id = cmd.get('command_id', '')
                name = cmd.get('name', '')
                desc = cmd.get('description', '')
                md.append(f"{header_level}## {name} (`{cmd_id}`)\n\n")
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
            md.append(f"{header_level}# Events\n\n")
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
            md.append(f"{header_level}# Policies\n\n")
            md.append("| Policy ID | Name | When Event | Issues Command |\n")
            md.append("|-----------|------|------------|----------------|\n")
            for pol in policies:
                pol_id = pol.get('policy_id', '')
                name = pol.get('name', '')
                when_evt = pol.get('when_event_id', '')
                issues_cmd = pol.get('issues_command_id', '')
                md.append(f"| `{pol_id}` | {name} | `{when_evt}` | `{issues_cmd}` |\n")
            md.append("\n")

        # Generate Mermaid diagrams
        md.append(f"{header_level}# Visualizations\n\n")

        # Sequence diagram
        if commands and actors:
            md.append(f"{header_level}## Sequence Diagram\n\n")
            md.append(self.generate_mermaid_sequence(story))
            md.append("\n")

        # Command-Event-Policy flow
        if commands or events or policies:
            md.append(f"{header_level}## Command-Event-Policy Flow\n\n")
            md.append(self.generate_mermaid_flow(story))
            md.append("\n")

        return md

    def generate_mermaid_sequence(self, story: Dict[str, Any]) -> str:
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

    def generate_mermaid_flow(self, story: Dict[str, Any]) -> str:
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

    def generate_actor_catalog(self):
        """Generate catalog of all actors across all stories."""
        md = ["# Actor Catalog\n\n"]

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
            story_links = ', '.join([f"[{title}]({sid}.md)" for sid, title in actor['stories'][:3]])
            if len(actor['stories']) > 3:
                story_links += f" (+{len(actor['stories']) - 3} more)"
            md.append(f"| `{actor_id}` | {name} | {kind} | {story_links} |\n")

        with open(self.output_dir / 'actors.md', 'w') as f:
            f.write(''.join(md))

    def generate_aggregate_catalog(self):
        """Generate catalog of all aggregates across all stories."""
        md = ["# Aggregate Catalog\n\n"]

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
            story_links = ', '.join([f"[{title}]({sid}.md)" for sid, title in agg['stories'][:3]])
            if len(agg['stories']) > 3:
                story_links += f" (+{len(agg['stories']) - 3} more)"
            md.append(f"| `{agg_id}` | {name} | {story_links} |\n")

        with open(self.output_dir / 'aggregates.md', 'w') as f:
            f.write(''.join(md))

    def generate_command_catalog(self):
        """Generate catalog of all commands across all stories."""
        md = ["# Command Catalog\n\n"]

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
            story_links = ', '.join([f"[{title}]({sid}.md)" for sid, title in cmd['stories'][:3]])
            if len(cmd['stories']) > 3:
                story_links += f" (+{len(cmd['stories']) - 3} more)"
            md.append(f"| `{cmd_id}` | {name} | {story_links} |\n")

        with open(self.output_dir / 'commands.md', 'w') as f:
            f.write(''.join(md))

    def generate_actor_catalog_content(self) -> List[str]:
        """Generate actor catalog content as a list of strings."""
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

    def generate_aggregate_catalog_content(self) -> List[str]:
        """Generate aggregate catalog content as a list of strings."""
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

    def generate_command_catalog_content(self) -> List[str]:
        """Generate command catalog content as a list of strings."""
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


def main():
    if len(sys.argv) < 3:
        print("Usage: python convert_to_markdown.py <input.yaml> <output_dir> [--single-file]")
        print("Example: python convert_to_markdown.py cb-domain-stories.yaml output/")
        print("Example: python convert_to_markdown.py cb-domain-stories.yaml output/ --single-file")
        sys.exit(1)

    yaml_file = sys.argv[1]
    output_dir = sys.argv[2]
    single_file = '--single-file' in sys.argv

    if not os.path.exists(yaml_file):
        print(f"Error: File not found: {yaml_file}")
        sys.exit(1)

    converter = DomainStoryConverter(yaml_file, output_dir)

    if single_file:
        converter.convert_to_single_file()
    else:
        converter.convert_all()


if __name__ == '__main__':
    main()
