"""Command-line interface for Strategic DDD YAML to Markdown converter"""

import argparse
import sys
import yaml
from pathlib import Path
from .converter import StrategicDDDConverter


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description='Convert Strategic DDD YAML to Markdown',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Convert strategic YAML to markdown
  python -m strategic_ddd_converter.cli payments-strategic.yaml payments-strategic.md

  # Validate YAML before conversion
  python -m strategic_ddd_converter.cli payments-strategic.yaml output.md --validate
        """
    )
    parser.add_argument('input', help='Input YAML file')
    parser.add_argument('output', help='Output Markdown file')
    parser.add_argument('--validate', action='store_true',
                       help='Validate YAML against schema (basic validation)')

    args = parser.parse_args()

    try:
        # Load YAML
        input_path = Path(args.input)
        if not input_path.exists():
            print(f"Error: Input file '{args.input}' not found", file=sys.stderr)
            sys.exit(1)

        print(f"Loading {args.input}...")
        with open(input_path) as f:
            data = yaml.safe_load(f)

        # Basic validation
        if args.validate or True:  # Always validate
            if 'system' not in data:
                print("Error: YAML must contain 'system' key", file=sys.stderr)
                sys.exit(1)

            system = data['system']
            required_fields = ['id', 'name']
            for field in required_fields:
                if field not in system:
                    print(f"Error: System must have '{field}' field", file=sys.stderr)
                    sys.exit(1)

            print(f"✓ Validation successful")
            print(f"  System: {system.get('name')}")
            print(f"  Domains: {len(system.get('domains', []))}")
            print(f"  Bounded Contexts: {len(system.get('bounded_contexts', []))}")
            print(f"  Context Mappings: {len(system.get('context_mappings', []))}")
            print(f"  BFF Scopes: {len(system.get('bff_scopes', []))}")
            print(f"  BFF Interfaces: {len(system.get('bff_interfaces', []))}")
            print()

        # Convert
        print(f"Converting to Markdown...")
        converter = StrategicDDDConverter(data)
        markdown = converter.convert_to_markdown()

        # Write output
        output_path = Path(args.output)
        output_path.parent.mkdir(parents=True, exist_ok=True)

        with open(output_path, 'w') as f:
            f.write(markdown)

        size_kb = len(markdown) / 1024
        print(f"✓ Generated {args.output} ({size_kb:.1f} KB)")

    except yaml.YAMLError as e:
        print(f"Error: Invalid YAML - {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
