# S2Doc - Stories to Documentation

**Convert YAML domain models to beautiful Markdown documentation**

S2Doc is a unified command-line tool that automatically detects and converts four types of YAML schemas into comprehensive Markdown documentation with Mermaid diagrams: Domain Stories, Strategic DDD, Tactical DDD, and Data Engineering.

## Features

- 🔍 **Automatic Schema Detection** - Intelligently identifies Domain Stories, Strategic DDD, Tactical DDD, or Data Engineering schemas
- 📝 **Rich Documentation** - Generates comprehensive Markdown with Mermaid UML, sequence, and architecture diagrams
- 🎯 **Single Command** - One tool for all your documentation needs
- 🚀 **Easy Installation** - Install directly from GitHub with pip
- 🔧 **Extensible** - Built on modular architecture for easy customization

## Supported Schemas

### 1. Domain Stories
Narrative scenarios with actors, work objects, and activities. Perfect for capturing domain knowledge through storytelling.

**Example Output:**
- Story narrative with participant interactions
- Mermaid sequence diagrams
- Scenario tables with activities and outcomes

### 2. Strategic DDD
System architecture with domains, bounded contexts, and context mappings. Ideal for documenting your strategic design decisions.

**Example Output:**
- System architecture diagrams
- Domain and bounded context hierarchies
- Context mapping relationships
- BFF (Backend for Frontend) patterns

### 3. Tactical DDD
Detailed bounded context design with aggregates, entities, value objects, and services. Complete tactical patterns documentation.

**Example Output:**
- Aggregate UML class diagrams
- Entity and value object specifications
- Repository interfaces
- Domain and application services
- Command and query interfaces (CQRS)
- Domain events

### 4. Data Engineering
Comprehensive data pipeline and dataset modeling with lineage tracking, governance policies, and observability metrics. Perfect for documenting data platforms and ML systems.

**Example Output:**
- System architecture with domains, pipelines, and datasets
- Pipeline flow diagrams showing stages and data flows
- Dataset schemas with PII tracking
- Data lineage diagrams showing upstream/downstream relationships
- Data contracts with SLAs
- Quality checks and validation rules
- Governance policies (retention, access control, PII handling)
- Observability metrics, SLOs, and alerts

## Installation

### Prerequisites
- Python 3.8 or higher
- pip

### Method 1: Direct Installation from GitHub

```bash
pip install git+https://github.com/FreeSideNomad/s2doc.git
```

### Method 2: Clone and Install

```bash
# Clone the repository
git clone https://github.com/FreeSideNomad/s2doc.git
cd s2doc

# Install in development mode (recommended for contributors)
pip install -e .

# Or install normally
pip install .
```

### Method 3: Install Specific Version/Branch

```bash
# Install specific version tag
pip install git+https://github.com/FreeSideNomad/s2doc.git@v1.0.0

# Install from specific branch
pip install git+https://github.com/FreeSideNomad/s2doc.git@main
```

### Verify Installation

After installation, verify the command is available globally:

```bash
s2doc --version
s2doc --help
```

## Usage

### Basic Usage

The tool automatically detects your schema type:

```bash
# Auto-detect schema and generate documentation
s2doc payment-workflow.yaml
```

### Specify Output Directory

```bash
# Generate documentation in a specific directory
s2doc payments-strategic.yaml -o docs/
```

### Verbose Mode

```bash
# See detailed processing information
s2doc payments-tactical.yaml -v
```

### Command-Line Options

```
s2doc [-h] [-o OUTPUT] [-v] [--version] input

Positional Arguments:
  input                 Input YAML file

Options:
  -h, --help            Show help message and exit
  -o OUTPUT, --output OUTPUT
                        Output directory (default: current directory)
  -v, --verbose         Enable verbose output
  --version             Show version number and exit
```

## Examples

### Example 1: Domain Stories

```bash
$ s2doc payment-flow.yaml
Detected schema: Domain Stories (narrative scenarios)
✓ Generated payment-flow.md
```

**Input:** `payment-flow.yaml` with domain story structure
**Output:** `payment-flow.md` with narrative and sequence diagram

### Example 2: Strategic DDD

```bash
$ s2doc payments-strategic.yaml -o docs/
Detected schema: Strategic DDD (system architecture)
✓ Generated docs/payments-strategic.md
```

**Input:** `payments-strategic.yaml` with system, domains, and bounded contexts
**Output:** `docs/payments-strategic.md` with architecture documentation

### Example 3: Tactical DDD

```bash
$ s2doc payments-tactical.yaml -v
Detected schema: Tactical DDD (bounded context details)
Processing bounded context: bc_payment_scheduling
✓ Generated bc_payment_scheduling.md
```

**Input:** `payments-tactical.yaml` with bounded context, aggregates, and entities
**Output:** `bc_payment_scheduling.md` with tactical design documentation

### Example 4: Data Engineering

```bash
$ s2doc ml-feature-store.yaml -v
Detected schema: Data Engineering (pipeline and dataset modeling)
Processing system: ML Feature Store Platform
✓ Generated ml-feature-store.md
```

**Input:** `ml-feature-store.yaml` with system, domains, pipelines, and datasets
**Output:** `ml-feature-store.md` with comprehensive data platform documentation including:
- System architecture diagrams
- Domain and pipeline hierarchies
- Dataset catalogs with schemas and PII tracking
- Data lineage visualization
- Governance policies and observability metrics

## Schema Detection

S2Doc automatically detects your schema type using:

1. **`$schema` field** (most reliable) - Checks for schema URL containing "domain-stories", "strategic", "tactical", or "data-eng"
2. **Top-level keys**:
   - Domain Stories: `domain_story` or `stories`
   - Data Engineering: `system`, `pipelines`, and `datasets` together
   - Strategic DDD: `system` with `domains` or `bounded_contexts`
   - Tactical DDD: `bounded_context` with `aggregates` or `entities`
3. **Nested structure analysis** - Validates expected nested elements

If the schema cannot be detected, you'll receive a helpful error message:

```
Error: Unable to detect schema type for 'input.yaml'

The file does not match any of the supported schemas:
  - Domain Stories (expects 'domain_story' or 'stories' key)
  - Strategic DDD (expects 'system' key with domains/bounded_contexts)
  - Tactical DDD (expects 'bounded_context' key with aggregates/entities)
  - Data Engineering (expects 'system', 'pipelines', and 'datasets' keys)

Please verify your YAML file structure.
```

## Output Files

### Domain Stories
- **One file** named after the input: `input-name.md`

### Strategic DDD
- **One file** named after the input: `input-name.md`

### Tactical DDD
- **One file per bounded context** named after the bounded context ID: `bc_<id>.md`
- Example: `bc_payment_scheduling.md`

### Data Engineering
- **One file** named after the input: `input-name.md`
- Example: `ml-feature-store.md`

## Documentation Features

### Domain Stories Output Includes:
- Story title and description
- Actor and work object definitions
- Activity sequences
- Scenario narratives
- Mermaid sequence diagrams

### Strategic DDD Output Includes:
- System architecture overview
- Hierarchical index
- Domain descriptions
- Bounded context details (nested under domains)
- Context mapping relationships
- BFF patterns
- Mermaid architecture diagrams with stereotypes

### Tactical DDD Output Includes:
- Bounded context header
- Summary tables (Application Services, Domain Services, Aggregates, Repositories)
- Aggregate details with UML class diagrams
- Entity specifications with attributes and methods
- Value object definitions
- Repository interfaces
- Domain and application service documentation
- Domain events
- Command and query interfaces (CQRS pattern)
- Transaction boundaries and workflows

### Data Engineering Output Includes:
- System overview with metadata (owners, tags)
- Hierarchical index (domains → pipelines → stages → datasets)
- System architecture Mermaid diagram
- Domain details with pipeline summaries
- Pipeline specifications (mode, schedule, traits)
- Pipeline flow diagrams showing stages and data flows
- Stage details with transforms and dependencies
- Dataset catalog with schemas, partitioning, and PII tracking
- Data contracts with SLAs and consumers
- Data quality checks with thresholds and alerts
- Data lineage diagrams (upstream/downstream relationships)
- Governance policies (retention, access control, PII handling)
- Observability (metrics, SLOs, alerts)

## Troubleshooting

### Command not found after installation

If `s2doc` is not found after installation:

```bash
# Check if pip's script directory is in your PATH
python3 -m pip show s2doc

# Try running directly
python3 -m s2doc.cli input.yaml

# Or reinstall with user flag
pip install --user git+https://github.com/FreeSideNomad/s2doc.git
```

### YAML parsing errors

Ensure your YAML file is valid:

```bash
# Use a YAML validator
python3 -c "import yaml; yaml.safe_load(open('your-file.yaml'))"
```

### Schema not detected

Verify your YAML file has the required top-level keys:
- Domain Stories: `domain_story` or `stories`
- Strategic DDD: `system`
- Tactical DDD: `bounded_context`

## Uninstallation

```bash
pip uninstall s2doc
```

## Contributing

Contributions are welcome! The project structure is:

```
s2doc/
├── __init__.py              # Package initialization
├── __version__.py           # Version information
├── cli.py                   # Main CLI entry point
├── detector.py              # Schema detection logic
├── converters/
│   ├── domain_stories/      # Domain stories converter
│   ├── strategic/           # Strategic DDD converter
│   └── tactical/            # Tactical DDD converter
└── utils/                   # Common utilities
```

## License

MIT License - See LICENSE file for details

## Author

Igor Music

## Links

- **Repository**: https://github.com/FreeSideNomad/s2doc
- **Issues**: https://github.com/FreeSideNomad/s2doc/issues

## Version History

### 1.0.0 (Current)
- Initial unified release
- Automatic schema detection
- Support for Domain Stories, Strategic DDD, and Tactical DDD
- Humanized entity names in output
- Comprehensive Mermaid diagram generation
