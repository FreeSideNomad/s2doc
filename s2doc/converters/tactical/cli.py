"""Command-line interface for Tactical DDD converter"""

import argparse
import os
import sys
import yaml
from .converter import TacticalDDDConverter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Convert Tactical DDD YAML to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s payments-tactical.yaml
  %(prog)s payments-tactical.yaml -o output/
  %(prog)s payments-tactical.yaml --output docs/
        """
    )
    parser.add_argument('input', help='Input YAML file')
    parser.add_argument(
        '-o', '--output',
        help='Output directory (default: current directory)',
        default='.'
    )

    args = parser.parse_args()

    # Validate input file exists
    if not os.path.exists(args.input):
        print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
        sys.exit(1)

    # Load YAML
    try:
        with open(args.input, 'r') as f:
            data = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Error parsing YAML: {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error reading file: {e}", file=sys.stderr)
        sys.exit(1)

    # Validate YAML structure
    if 'bounded_context' not in data:
        print("Error: YAML file must contain 'bounded_context' key", file=sys.stderr)
        sys.exit(1)

    # Convert
    try:
        converter = TacticalDDDConverter(data)
        markdown = converter.convert_to_markdown()
    except Exception as e:
        print(f"Error converting to markdown: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)

    # Generate output filename from bounded context ID
    bc_id = data['bounded_context']['id']
    output_file = os.path.join(args.output, f"{bc_id}.md")

    # Create output directory if it doesn't exist
    os.makedirs(args.output, exist_ok=True)

    # Write output
    try:
        with open(output_file, 'w') as f:
            f.write(markdown)
    except Exception as e:
        print(f"Error writing output file: {e}", file=sys.stderr)
        sys.exit(1)

    print(f"✓ Generated {output_file}")


if __name__ == '__main__':
    main()
