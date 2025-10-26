#!/bin/bash
set -e

SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
cd "$PROJECT_ROOT"

if ! command -v python3 &> /dev/null; then
    echo "ERROR: Python 3 is not installed"
    exit 1
fi

if [ ! -d "venv" ]; then
    echo "Creating virtual environment..."
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q --upgrade pip
pip install -q -r requirements.txt

if [ -z "$1" ]; then
    echo "Usage: $0 <input-yaml-file> [output-directory]"
    echo "Example: $0 cb-domain-stories.yaml output"
    deactivate
    exit 1
fi

INPUT_FILE="$1"
OUTPUT_DIR="${2:-output}"

if [ ! -f "$INPUT_FILE" ]; then
    echo "ERROR: Input file not found: $INPUT_FILE"
    deactivate
    exit 1
fi

mkdir -p "$OUTPUT_DIR"

echo "Converting $INPUT_FILE to single markdown file..."
python3 scripts/convert_to_markdown.py "$INPUT_FILE" "$OUTPUT_DIR" --single-file

echo "Done! Output: $OUTPUT_DIR/domain-stories-complete.md"
deactivate
