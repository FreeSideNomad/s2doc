"""Main CLI entry point for s2doc"""

import argparse
import os
import sys
import yaml
from pathlib import Path

from .detector import detect_schema_type, get_schema_description, get_error_message, SchemaType
from .converters.domain_stories import DomainStoryConverter
from .converters.strategic import StrategicDDDConverter
from .converters.tactical import TacticalDDDConverter
from .converters.data_eng import DataEngConverter
from .__version__ import __version__


def main():
    """Main entry point for s2doc CLI"""
    parser = argparse.ArgumentParser(
        prog='s2doc',
        description='Convert YAML domain models to Markdown documentation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  s2doc payment-workflow.yaml
  s2doc payments-strategic.yaml -o docs/
  s2doc payments-tactical.yaml -o output/ -v

Supported schemas:
  - Domain Stories (narrative scenarios with actors and activities)
  - Strategic DDD (domains, bounded contexts, context mappings)
  - Tactical DDD (aggregates, entities, value objects, services)
  - Data Engineering (pipelines, datasets, lineage, governance)

For more information: https://github.com/FreeSideNomad/s2doc
        """
    )

    parser.add_argument('input', help='Input YAML file')
    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: current directory)',
        default='.'
    )
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version=f'%(prog)s {__version__}'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(4)

    # Create output directory if needed
    try:
        os.makedirs(args.output, exist_ok=True)
    except Exception as e:
        print(f"Error: Could not create output directory '{args.output}': {e}", file=sys.stderr)
        sys.exit(4)

    # Load YAML (handle multi-document YAML with frontmatter)
    try:
        with open(args.input, 'r', encoding='utf-8') as f:
            docs = list(yaml.safe_load_all(f))
            # If multiple documents, use the last one (frontmatter comes first)
            data = docs[-1] if docs else None
            if data is None:
                raise ValueError("Empty YAML file")
    except yaml.YAMLError as e:
        print(f"Error: Failed to parse YAML file '{args.input}'", file=sys.stderr)
        print(f"  {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: Failed to read file '{args.input}': {e}", file=sys.stderr)
        sys.exit(4)

    # Detect schema type
    schema_type = detect_schema_type(data)

    if schema_type == SchemaType.UNKNOWN:
        print(f"Error: Unable to detect schema type for '{args.input}'", file=sys.stderr)
        print(get_error_message(), file=sys.stderr)
        sys.exit(2)

    if args.verbose:
        print(f"Detected schema: {get_schema_description(schema_type)}")

    # Convert based on schema type
    try:
        if schema_type == SchemaType.DOMAIN_STORIES:
            convert_domain_stories(data, args.input, args.output, args.verbose)
        elif schema_type == SchemaType.STRATEGIC_DDD:
            convert_strategic_ddd(data, args.input, args.output, args.verbose)
        elif schema_type == SchemaType.TACTICAL_DDD:
            convert_tactical_ddd(data, args.input, args.output, args.verbose)
        elif schema_type == SchemaType.DATA_ENGINEERING:
            convert_data_engineering(data, args.input, args.output, args.verbose)
    except Exception as e:
        print(f"Error: Conversion failed: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(3)


def convert_domain_stories(data: dict, input_file: str, output_dir: str, verbose: bool):
    """Convert domain stories YAML to markdown"""
    # DomainStoryConverter expects a file path and writes directly to output
    converter = DomainStoryConverter(input_file)

    # Generate output filename from input filename
    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.md")

    # DomainStoryConverter.convert() writes to the file and returns the path
    converter.convert(output_file)

    print(f"✓ Generated {output_file}")


def convert_strategic_ddd(data: dict, input_file: str, output_dir: str, verbose: bool):
    """Convert strategic DDD YAML to markdown"""
    converter = StrategicDDDConverter(data)
    markdown = converter.convert_to_markdown()

    # Generate output filename from input filename
    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.md")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Generated {output_file}")


def convert_tactical_ddd(data: dict, input_file: str, output_dir: str, verbose: bool):
    """Convert tactical DDD YAML to markdown (one file per bounded context)"""
    converter = TacticalDDDConverter(data)
    markdown = converter.convert_to_markdown()

    # Generate output filename from bounded context ID
    bc_id = data['bounded_context']['id']
    output_file = os.path.join(output_dir, f"{bc_id}.md")

    if verbose:
        print(f"Processing bounded context: {bc_id}")

    with open(output_file, 'w', encoding='utf-8') as f:
        f.write(markdown)

    print(f"✓ Generated {output_file}")


def convert_data_engineering(data: dict, input_file: str, output_dir: str, verbose: bool):
    """Convert data engineering YAML to markdown"""
    converter = DataEngConverter(data)

    # Generate output filename from input filename
    input_path = Path(input_file)
    output_file = os.path.join(output_dir, f"{input_path.stem}.md")

    if verbose:
        system_name = data.get('system', {}).get('name', 'Unknown System')
        print(f"Processing system: {system_name}")

    converter.convert_to_markdown(output_file)

    print(f"✓ Generated {output_file}")


if __name__ == '__main__':
    main()
