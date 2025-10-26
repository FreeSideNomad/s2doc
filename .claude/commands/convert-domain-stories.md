---
description: Convert domain stories YAML to single markdown file with Mermaid diagrams
---

You are tasked with converting domain stories from YAML format to a single markdown file.

## Instructions

1. Ask the user for the input YAML file path (relative to current working directory)
2. Ask the user for the output directory (default: "output")
3. Run the conversion script using Bash tool:
   ```
   bash scripts/convert_domain_stories.sh <input-yaml-file> <output-directory>
   ```
4. Report the location of the generated markdown file
5. If there are errors, help the user troubleshoot

## Script Location

The conversion script is located at: `scripts/convert_domain_stories.sh` in the model-tools directory.

## What the script does

- Initializes Python virtual environment (if not exists)
- Installs PyYAML dependency
- Runs scripts/convert_to_markdown.py with --single-file flag
- Generates domain-stories-complete.md in the output directory

## Example Usage

For a YAML file at `./my-domain.yaml` with output to `./docs`:
```
bash scripts/convert_domain_stories.sh my-domain.yaml docs
```

This will create: `docs/domain-stories-complete.md`
