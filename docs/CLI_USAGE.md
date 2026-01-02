# CLI Usage Guide

## Installation

```bash
# Install from source
git clone https://github.com/stiigg/define-xml-validator.git
cd define-xml-validator
pip install -e .

# Verify installation
define-validator info
```

## Quick Start

### Basic Validation

Validate a define.xml file (auto-downloads schema if needed):

```bash
define-validator validate define.xml
```

### With Custom Schema

```bash
define-validator validate define.xml --schema schemas/define-2.1.xsd
```

### Generate HTML Report

```bash
define-validator validate define.xml --output report.html --format html
```

### Generate JSON Report

```bash
define-validator validate define.xml --output results.json --format json
```

### Strict Mode (warnings = failure)

```bash
define-validator validate define.xml --strict
```

### Run Specific Layers

Run only layers 1, 2, and 3:

```bash
define-validator validate define.xml --layers 1 2 3
```

## Schema Management

### Download Schema

Download Define.xml 2.1 schema:

```bash
define-validator download-schema --version 2.1
```

Download to custom directory:

```bash
define-validator download-schema --version 2.1 --output-dir ./my-schemas
```

### Available Versions

- `2.0` - Define.xml 2.0
- `2.1` - Define.xml 2.1 (default)

## Commands

### validate

Validate a define.xml file.

**Usage:**
```bash
define-validator validate [OPTIONS] FILE
```

**Arguments:**
- `FILE` - Path to define.xml file (required)

**Options:**
- `--schema PATH` - Path to XSD schema (auto-downloads if omitted)
- `--output, -o PATH` - Output file for validation report
- `--format, -f {json,html,text}` - Output format (default: text)
- `--strict` - Exit with error code 1 if any warnings found
- `--layers N [N ...]` - Specific validation layers to run (1-7)

**Examples:**
```bash
# Basic validation
define-validator validate define.xml

# HTML report with strict mode
define-validator validate define.xml -o report.html -f html --strict

# Run only schema and structural validation
define-validator validate define.xml --layers 1 2
```

### download-schema

Download CDISC Define.xml schema.

**Usage:**
```bash
define-validator download-schema [OPTIONS]
```

**Options:**
- `--version {2.0,2.1}` - Schema version (default: 2.1)
- `--output-dir PATH` - Directory to save schema (default: ./schemas)

**Examples:**
```bash
# Download latest schema
define-validator download-schema

# Download specific version
define-validator download-schema --version 2.0

# Custom output directory
define-validator download-schema --output-dir ~/cdisc-schemas
```

### info

Show validator information.

**Usage:**
```bash
define-validator info
```

Displays:
- Validation layer descriptions
- Feature list
- Usage examples
- Documentation links

## Output Formats

### Text (Console)

Default output format, color-coded for terminal:

```
======================================================================
  DEFINE.XML VALIDATION REPORT
======================================================================

File: define.xml
SHA-256: abc123...
Timestamp: 2024-01-02 10:30:00

Status: PASSED
Errors: 0
Warnings: 2

──────────────────────────────────────────────────────────────────────
Layer 1: XSD Schema Validation
──────────────────────────────────────────────────────────────────────
  ✓ No issues found

──────────────────────────────────────────────────────────────────────
Layer 4: Controlled Terminology Validation
──────────────────────────────────────────────────────────────────────
  ⚠️  WARNINGS (2):
    1. Missing RACE codelist term: NATIVE HAWAIIAN OR OTHER PACIFIC ISLANDER
    2. ETHNIC codelist incomplete (6/8 required terms)
```

### JSON

Machine-readable format for CI/CD integration:

```json
{
  "metadata": {
    "file_path": "define.xml",
    "sha256": "abc123...",
    "timestamp": "2024-01-02T10:30:00"
  },
  "summary": {
    "status": "PASSED",
    "total_errors": 0,
    "total_warnings": 2
  },
  "layers": {
    "layer_1": {
      "name": "XSD Schema Validation",
      "errors": [],
      "warnings": []
    }
  }
}
```

### HTML

Interactive web report with visual styling:

- Color-coded status badges
- Collapsible sections
- Downloadable for sharing
- FDA reviewer-friendly format

## Exit Codes

- `0` - Success (no errors)
- `1` - Failure (errors found, or warnings in strict mode)

## Integration Examples

### CI/CD Pipeline (GitHub Actions)

```yaml
name: Validate Define.xml

on: [push, pull_request]

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      
      - name: Install validator
        run: |
          pip install git+https://github.com/stiigg/define-xml-validator.git
      
      - name: Validate
        run: |
          define-validator validate data/define.xml --strict
      
      - name: Generate report
        if: always()
        run: |
          define-validator validate data/define.xml \
            --output validation-report.html --format html
      
      - name: Upload report
        if: always()
        uses: actions/upload-artifact@v3
        with:
          name: validation-report
          path: validation-report.html
```

### Pre-commit Hook

```bash
#!/bin/bash
# .git/hooks/pre-commit

for file in $(git diff --cached --name-only | grep -E 'define\.xml$')
do
  echo "Validating $file..."
  define-validator validate "$file" --strict
  if [ $? -ne 0 ]; then
    echo "❌ Validation failed for $file"
    exit 1
  fi
done

echo "✅ All define.xml files validated"
```

### Batch Validation Script

```bash
#!/bin/bash
# validate-all.sh

mkdir -p reports

for define_file in data/*/define.xml; do
  study=$(basename $(dirname "$define_file"))
  echo "Validating study: $study"
  
  define-validator validate "$define_file" \
    --output "reports/${study}-report.html" \
    --format html
  
  if [ $? -eq 0 ]; then
    echo "✅ $study passed"
  else
    echo "❌ $study failed"
  fi
done

echo "Reports saved to reports/"
```

## Troubleshooting

### Schema Download Fails

**Problem:** `RuntimeError: Failed to download schema`

**Solution:**
1. Check internet connection
2. Verify CDISC website is accessible
3. Download manually and use `--schema` option:
   ```bash
   wget https://www.cdisc.org/sites/default/files/schema/define-xml-2.1/define2-1-0.xsd
   define-validator validate define.xml --schema define2-1-0.xsd
   ```

### File Not Found Error

**Problem:** `Error: File not found: define.xml`

**Solution:**
- Use absolute path: `define-validator validate /full/path/to/define.xml`
- Or navigate to directory: `cd study-dir && define-validator validate define.xml`

### Permission Denied

**Problem:** `PermissionError: [Errno 13] Permission denied: 'report.html'`

**Solution:**
- Check write permissions for output directory
- Use different output path: `define-validator validate define.xml -o ~/reports/output.html`

## Advanced Usage

### Custom Validation Workflow

```python
# custom_validation.py
from define_validator import DefineValidator, SchemaManager, ReportGenerator

# Initialize
schema_mgr = SchemaManager()
schema_path = schema_mgr.get_schema('2.1')

validator = DefineValidator(str(schema_path))

# Run validation
results = validator.run_full_validation('define.xml')

# Custom processing
for layer_name, layer_data in results['layers'].items():
    if layer_data['errors']:
        print(f"Layer {layer_name} failed!")
        for error in layer_data['errors']:
            print(f"  - {error}")

# Generate report
report_gen = ReportGenerator(results)
report_gen.generate_html('custom-report.html')
```

### Programmatic Access

```python
from define_validator.cli import CLI

# Run validation programmatically
cli = CLI()
exit_code = cli.run(['validate', 'define.xml', '--strict'])

if exit_code == 0:
    print("Validation passed!")
else:
    print("Validation failed!")
```

## Performance Tips

1. **Cache schemas**: First download saves to `./schemas/` for reuse
2. **Specific layers**: Use `--layers` for faster validation during development
3. **Batch processing**: Process multiple files in parallel with GNU parallel:
   ```bash
   find . -name 'define.xml' | parallel define-validator validate {}
   ```

## See Also

- [API Documentation](API.md)
- [Validation Rules Reference](VALIDATION_RULES.md)
- [FDA Submission Guide](FDA_GUIDE.md)
- [Contributing Guidelines](../CONTRIBUTING.md)
