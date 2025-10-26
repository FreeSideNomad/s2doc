# Domain Stories Tool Setup - Instructions for Claude Code

This document provides instructions for Claude Code on how to integrate the domain-stories-visual tool into another project as a git submodule.

## Prerequisites

The parent repository must be initialized as a git repository. If not, run:
```bash
git init
```

## Step 1: Add Git Submodule

From the parent project root directory, add this repository as a git submodule in a `tools` directory:

```bash
git submodule add git@github.com:FreeSideNomad/model-tools.git tools/model-tools
```

This will:
- Clone the model-tools repository into `tools/model-tools`
- Create a `.gitmodules` file in the parent repository
- Track the submodule reference in the parent repository

## Step 2: Initialize and Update Submodule (for existing repos)

If cloning a repository that already has submodules configured, run:

```bash
git submodule init
git submodule update
```

Or use the shorthand when cloning:
```bash
git clone --recurse-submodules <parent-repo-url>
```

## Step 3: Use the Conversion Tool

From the parent project root, run the conversion script:

```bash
bash tools/model-tools/scripts/convert_domain_stories.sh <input-yaml-file> <output-directory>
```

Example:
```bash
bash tools/model-tools/scripts/convert_domain_stories.sh ./domain-models/my-stories.yaml ./docs
```

This will generate: `./docs/domain-stories-complete.md`

## Step 4: Create Slash Command in Parent Project (Optional)

To make the tool available as a slash command in the parent project, create:
`.claude/commands/convert-stories.md`

```markdown
---
description: Convert domain stories YAML to markdown
---

Convert domain stories from YAML to markdown using the model-tools.

1. Ask user for input YAML file path
2. Ask user for output directory (default: "output")
3. Run: bash tools/model-tools/scripts/convert_domain_stories.sh <input> <output>
4. Report the generated file location
```

## Step 5: Update Submodule (when needed)

To update the submodule to the latest version from the remote repository:

```bash
cd tools/model-tools
git pull origin main
cd ../..
git add tools/model-tools
git commit -m "Update model-tools submodule"
```

## Step 6: Remove Submodule (if needed)

To remove the submodule:

```bash
git submodule deinit -f tools/model-tools
git rm -f tools/model-tools
rm -rf .git/modules/tools/model-tools
```

Then commit the changes.

## Typical Workflow for Claude Code

When a user asks to convert domain stories in a parent project:

1. Check if submodule exists: `ls tools/model-tools`
2. If not, add submodule: `git submodule add git@github.com:FreeSideNomad/model-tools.git tools/model-tools`
3. Ask user for input YAML file path and output directory
4. Run conversion: `bash tools/model-tools/scripts/convert_domain_stories.sh <input> <output>`
5. Report success and file location

## Directory Structure Example

```
parent-project/
├── .git/
├── .gitmodules                           # Submodule configuration
├── .claude/
│   └── commands/
│       └── convert-stories.md            # Optional: parent project slash command
├── domain-models/
│   └── my-stories.yaml                   # Input YAML files
├── docs/
│   └── domain-stories-complete.md        # Generated output
└── tools/
    └── model-tools/                      # Git submodule
        ├── .claude/
        │   └── commands/
        │       └── convert-domain-stories.md
        ├── scripts/
        │   ├── convert_domain_stories.sh # Conversion script
        │   └── convert_to_markdown.py    # Python converter
        ├── requirements.txt
        └── venv/                         # Created on first run
```

## Troubleshooting for Claude Code

### Issue: Submodule directory is empty
**Solution:** Run `git submodule update --init --recursive`

### Issue: Permission denied when running script
**Solution:** Run `chmod +x tools/model-tools/scripts/convert_domain_stories.sh`

### Issue: Python not found
**Solution:** Verify Python 3.8+ is installed with `python3 --version`

### Issue: Submodule changes not reflected
**Solution:**
```bash
cd tools/model-tools
git pull origin main
cd ../..
git add tools/model-tools
git commit -m "Update submodule"
```

## Git Submodule Best Practices for Claude Code

1. Always use `--recurse-submodules` when cloning parent repositories
2. Before updating submodules, check current branch: `cd tools/model-tools && git branch`
3. Submodules track specific commits, not branches - remember to update after pulling changes
4. When committing in parent repo, the submodule reference (commit SHA) is stored, not the submodule's files
5. Use relative paths when possible for cross-platform compatibility
