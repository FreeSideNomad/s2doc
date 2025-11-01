#!/usr/bin/env python3
"""
Domain Stories Toolkit CLI
Command-line interface for converting domain stories YAML to documentation.
"""

import argparse
import sys
import yaml
from pathlib import Path
from typing import Dict, Any

from . import __version__
from .converter import DomainStoryConverter
from .docx_converter import convert_md_to_docx
from .comment_extractor import extract_comments_to_yaml


def cmd_review(args) -> int:
    """
    Main workflow: YAML → MD + DOCX
    Creates both markdown and Word document from YAML input.
    Output files inherit the basename from the input YAML file.
    """
    yaml_path = Path(args.input)
    output_dir = Path(args.output_dir)

    # Validate input
    if not yaml_path.exists():
        print(f"Error: Input file not found: {yaml_path}", file=sys.stderr)
        return 1

    # Determine output file names (same basename as input YAML)
    base_name = yaml_path.stem
    md_path = output_dir / f"{base_name}.md"
    docx_path = output_dir / f"{base_name}.docx"

    # Temporary DOCX-specific markdown file
    docx_md_path = output_dir / f"{base_name}_docx.md"

    try:
        # Step 1: Convert YAML to Markdown (clean, with Mermaid)
        print(f"Step 1/3: Converting YAML to Markdown...")
        converter = DomainStoryConverter(str(yaml_path))
        converter.convert(str(md_path))

        # Step 2: Create DOCX-specific markdown (with PNG images)
        print(f"\nStep 2/3: Creating DOCX-specific markdown with diagrams...")
        converter.create_docx_markdown(str(md_path), str(docx_md_path))

        # Step 3: Convert DOCX markdown to DOCX
        print(f"\nStep 3/3: Converting to DOCX (landscape)...")
        convert_md_to_docx(docx_md_path, docx_path)

        # Clean up temporary DOCX markdown file
        docx_md_path.unlink()

        print(f"\n{'='*60}")
        print(f"✓ Review documents created successfully!")
        print(f"{'='*60}")
        print(f"Markdown: {md_path}")
        print(f"DOCX:     {docx_path} (landscape orientation)")
        print(f"\nNext steps:")
        print(f"1. Open {docx_path} in Microsoft Word")
        print(f"2. Add comments and review the content")
        print(f"3. Save the reviewed document")
        print(f"4. Extract comments: dst extract-comments <reviewed.docx> <output.yaml>")

        return 0

    except Exception as e:
        print(f"Error during conversion: {e}", file=sys.stderr)
        # Clean up temporary file if it exists
        if docx_md_path.exists():
            docx_md_path.unlink()
        return 1


def cmd_extract_comments(args) -> int:
    """Extract comments from a reviewed DOCX file to YAML."""
    docx_path = Path(args.docx)
    yaml_path = Path(args.output)

    if not docx_path.exists():
        print(f"Error: DOCX file not found: {docx_path}", file=sys.stderr)
        return 1

    try:
        extract_comments_to_yaml(
            docx_path=docx_path,
            yaml_path=yaml_path,
            context_chars=args.context_chars,
            include_replies=args.include_replies
        )

        print(f"\n{'='*60}")
        print(f"✓ Comments extracted successfully!")
        print(f"{'='*60}")
        print(f"Output: {yaml_path}")
        print(f"\nYou can now process the comments with an LLM or review manually.")

        return 0

    except Exception as e:
        print(f"Error extracting comments: {e}", file=sys.stderr)
        return 1


def cmd_validate(args) -> int:
    """Validate YAML file structure."""
    yaml_path = Path(args.input)

    if not yaml_path.exists():
        print(f"Error: Input file not found: {yaml_path}", file=sys.stderr)
        return 1

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        # Basic validation
        errors = []

        if not isinstance(data, dict):
            errors.append("YAML root must be a dictionary")
        else:
            if 'domain_stories' not in data:
                errors.append("Missing required field: 'domain_stories'")
            elif not isinstance(data['domain_stories'], list):
                errors.append("'domain_stories' must be a list")
            else:
                stories = data['domain_stories']
                for idx, story in enumerate(stories):
                    if not isinstance(story, dict):
                        errors.append(f"Story {idx + 1} is not a dictionary")
                        continue

                    # Check required fields
                    if 'domain_story_id' not in story:
                        errors.append(f"Story {idx + 1}: missing 'domain_story_id'")
                    elif not story['domain_story_id'].startswith('dst_'):
                        errors.append(
                            f"Story {idx + 1}: domain_story_id should start with 'dst_' "
                            f"(got: {story['domain_story_id']})"
                        )

                    if 'title' not in story:
                        errors.append(f"Story {idx + 1}: missing 'title'")

        if errors:
            print(f"Validation failed with {len(errors)} error(s):\n", file=sys.stderr)
            for error in errors:
                print(f"  ✗ {error}", file=sys.stderr)
            return 1
        else:
            print(f"✓ Validation successful!")
            print(f"  File: {yaml_path}")
            print(f"  Stories: {len(data.get('domain_stories', []))}")
            return 0

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error validating file: {e}", file=sys.stderr)
        return 1


def cmd_info(args) -> int:
    """Show statistics about the domain stories YAML file."""
    yaml_path = Path(args.input)

    if not yaml_path.exists():
        print(f"Error: Input file not found: {yaml_path}", file=sys.stderr)
        return 1

    try:
        with open(yaml_path, 'r') as f:
            data = yaml.safe_load(f)

        stories = data.get('domain_stories', [])

        # Collect statistics
        actors = set()
        aggregates = set()
        commands = set()
        events = set()
        policies = set()
        work_objects = set()

        for story in stories:
            for actor in story.get('actors', []):
                actors.add(actor.get('actor_id', ''))

            for agg in story.get('aggregates', []):
                aggregates.add(agg.get('aggregate_id', ''))

            for cmd in story.get('commands', []):
                commands.add(cmd.get('command_id', ''))

            for evt in story.get('events', []):
                events.add(evt.get('event_id', ''))

            for pol in story.get('policies', []):
                policies.add(pol.get('policy_id', ''))

            for wobj in story.get('work_objects', []):
                work_objects.add(wobj.get('work_object_id', ''))

        # Display statistics
        print(f"\n{'='*60}")
        print(f"Domain Stories Model Information")
        print(f"{'='*60}")
        print(f"File:              {yaml_path}")
        print(f"Version:           {data.get('version', 'N/A')}")
        print(f"\nStories:           {len(stories)}")
        print(f"\nUnique Entities:")
        print(f"  Actors:          {len(actors)}")
        print(f"  Aggregates:      {len(aggregates)}")
        print(f"  Commands:        {len(commands)}")
        print(f"  Events:          {len(events)}")
        print(f"  Policies:        {len(policies)}")
        print(f"  Work Objects:    {len(work_objects)}")
        print(f"{'='*60}\n")

        return 0

    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        return 1


def cmd_version(args) -> int:
    """Display version information."""
    print(f"Domain Stories Toolkit v{__version__}")
    return 0


def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Domain Stories Toolkit - Convert YAML domain stories to documentation",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Generate Markdown + DOCX for review
  dst review domain-model/stories.yaml docs/

  # Extract comments from reviewed DOCX
  dst extract-comments docs/stories.docx docs/comments.yaml

  # Validate YAML structure
  dst validate domain-model/stories.yaml

  # Show model statistics
  dst info domain-model/stories.yaml

For more information, visit: https://github.com/FreeSideNomad/domain-stories-toolkit
        """
    )

    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    subparsers = parser.add_subparsers(dest='command', help='Available commands')

    # dst review command
    parser_review = subparsers.add_parser(
        'review',
        help='Generate Markdown + DOCX from YAML (complete workflow)',
        description='Converts domain stories YAML to both Markdown and DOCX documents. '
                    'Output files inherit the basename from the input YAML file.'
    )
    parser_review.add_argument(
        'input',
        help='Path to input YAML file (e.g., stories.yaml)'
    )
    parser_review.add_argument(
        'output_dir',
        help='Output directory (will create <basename>.md and <basename>.docx)'
    )
    parser_review.set_defaults(func=cmd_review)

    # dst extract-comments command
    parser_extract = subparsers.add_parser(
        'extract-comments',
        help='Extract comments from reviewed DOCX to YAML',
        description='Extracts comments from a Word document with domain story context mapping.'
    )
    parser_extract.add_argument(
        'docx',
        help='Path to DOCX file with comments'
    )
    parser_extract.add_argument(
        'output',
        help='Path to output YAML file'
    )
    parser_extract.add_argument(
        '--context-chars',
        type=int,
        default=220,
        help='Number of context characters to include (default: 220)'
    )
    parser_extract.add_argument(
        '--include-replies',
        action='store_true',
        default=True,
        help='Include comment replies (default: True)'
    )
    parser_extract.set_defaults(func=cmd_extract_comments)

    # dst validate command
    parser_validate = subparsers.add_parser(
        'validate',
        help='Validate YAML file structure',
        description='Validates the domain stories YAML file against expected structure.'
    )
    parser_validate.add_argument(
        'input',
        help='Path to input YAML file'
    )
    parser_validate.set_defaults(func=cmd_validate)

    # dst info command
    parser_info = subparsers.add_parser(
        'info',
        help='Show statistics about the domain model',
        description='Displays statistics and information about the domain stories model.'
    )
    parser_info.add_argument(
        'input',
        help='Path to input YAML file'
    )
    parser_info.set_defaults(func=cmd_info)

    # dst version command
    parser_version = subparsers.add_parser(
        'version',
        help='Show version information'
    )
    parser_version.set_defaults(func=cmd_version)

    # Parse arguments
    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 1

    # Execute command
    return args.func(args)


if __name__ == '__main__':
    sys.exit(main())
