# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.1.0] - 2025-01-11

### Added

- **Data Engineering Schema Support**: Complete fourth schema type for data platform documentation
  - System architecture with domains, pipelines, and datasets
  - Three types of Mermaid diagrams (system architecture, pipeline flows, data lineage)
  - Dataset catalog with schemas, PII tracking, and partitioning strategies
  - Data contracts with SLAs, consumers, and evolution policies
  - Quality checks with thresholds, assertions, and alerts
  - Data lineage visualization (upstream/downstream relationships)
  - Governance policies (retention, access control, PII handling)
  - Observability section (metrics, SLOs, alerts)
  - 6-level heading hierarchy for deep documentation
  - Humanized entity names throughout
  - Cross-referenced navigation with anchor links
  - 25 comprehensive unit tests (97% coverage)

- **Multi-document YAML Support**: CLI now handles YAML files with frontmatter
  - Automatically extracts main document from multi-document YAML
  - Backwards compatible with single-document YAML files

- **Documentation**:
  - Data engineering schema description in README
  - Usage examples and sample outputs
  - Implementation specification (`data-eng-yaml-to-md-prompt.md`)
  - Relationship documentation (`data-eng-hierarchy.md`)
  - Semantic versioning guidelines (`claude.md`)
  - Example data engineering YAML (`examples/data-eng.yaml`)
  - JSON Schema validation (`schemas/data-eng.schema.yaml`)

### Changed

- Updated schema detection to prioritize data engineering schemas
- Enhanced error messages to include data engineering schema hints
- Improved README with comprehensive feature list

### Fixed

- None

## [1.0.0] - 2025-01-09

### Added

- **Initial Release**: Unified CLI for domain model documentation
  - Domain Stories converter (narrative scenarios with sequence diagrams)
  - Strategic DDD converter (system architecture with domains and bounded contexts)
  - Tactical DDD converter (aggregates, entities, value objects, services)
  - Automatic schema detection
  - Mermaid diagram generation
  - Entity name humanization
  - 40 unit tests (76% coverage)
  - Installation from GitHub via pip
  - Comprehensive README with examples

### Features

- Single command for multiple schema types
- Auto-detection based on `$schema` field or structure
- Rich Markdown output with tables and diagrams
- Verbose mode for debugging
- Configurable output directory

[1.1.0]: https://github.com/FreeSideNomad/s2doc/compare/v1.0.0...v1.1.0
[1.0.0]: https://github.com/FreeSideNomad/s2doc/releases/tag/v1.0.0
