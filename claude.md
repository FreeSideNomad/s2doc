# Claude Code Development Notes

## Semantic Versioning

**Starting from this commit**, we will follow [Semantic Versioning](https://semver.org/) for all releases:

- **MAJOR** version (X.0.0): Breaking changes to CLI, schema structure, or output format
- **MINOR** version (0.X.0): New features (new schema support, new converters, new sections)
- **PATCH** version (0.0.X): Bug fixes, documentation updates, performance improvements

### Current Version: 1.0.0

### Version History

#### v1.1.0 (Next Release - In Progress)
- **NEW**: Data Engineering schema support
  - Complete pipeline and dataset modeling
  - Data lineage visualization
  - Governance policies (retention, access control, PII handling)
  - Observability (metrics, SLOs, alerts)
  - 3 types of Mermaid diagrams (system architecture, pipeline flows, lineage)
  - 25 comprehensive unit tests (97% coverage)
- **IMPROVED**: Multi-document YAML support (handles frontmatter)
- **IMPROVED**: README with data engineering documentation

#### v1.0.0 (Initial Release)
- Domain Stories converter
- Strategic DDD converter
- Tactical DDD converter
- Automatic schema detection
- Unified CLI interface
- 40 unit tests (76% coverage)

## Release Process

When ready to release:

1. **Update version** in `s2doc/__version__.py`
2. **Update CHANGELOG** (create if needed)
3. **Tag the release**: `git tag -a vX.Y.Z -m "Release vX.Y.Z"`
4. **Push with tags**: `git push origin main --tags`
5. **Create GitHub Release** with release notes:
   - New features
   - Breaking changes (if MAJOR)
   - Bug fixes
   - Known issues
   - Installation instructions

## Considerations for Releases

### What to include in a GitHub Release:

1. **Release Notes**
   - Summary of changes
   - New schema support
   - Breaking changes
   - Migration guide (if needed)

2. **Installation Instructions**
   ```bash
   pip install git+https://github.com/FreeSideNomad/s2doc.git@vX.Y.Z
   ```

3. **Example Outputs**
   - Sample generated markdown files
   - Screenshots of rendered diagrams (if applicable)

4. **Schema Files**
   - Reference to schema files in `schemas/`
   - Example YAML files in `examples/`

### When to create a release:

- **MAJOR**: Breaking changes (e.g., CLI argument changes, output format changes)
- **MINOR**: New features complete and tested (like the data engineering converter)
- **PATCH**: Bug fixes, documentation improvements

### Next Release Candidate: v1.1.0

**Reason**: New data engineering schema support (MINOR version bump)

**Suggested Release Name**: "Data Engineering Support"

**Release Notes Draft**:
- ✨ NEW: Data Engineering schema converter
  - Pipelines, datasets, lineage tracking
  - Governance and observability sections
  - System architecture and flow diagrams
- 🔧 IMPROVED: Multi-document YAML support
- 📚 UPDATED: Documentation with data engineering examples
- 🧪 TESTING: 25 new tests, 97% coverage for data engineering converter

**Breaking Changes**: None (backward compatible)

**Migration Guide**: Not needed (additive changes only)
