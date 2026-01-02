#!/usr/bin/env python3
"""
CLI interface for Define.xml Validator
"""
import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .validator import DefineValidator
from .schema_manager import SchemaManager
from .report_generator import ReportGenerator


class CLI:
    """Command-line interface for Define.xml validation"""
    
    def __init__(self):
        self.parser = self._create_parser()
        self.schema_manager = SchemaManager()
    
    def _create_parser(self) -> argparse.ArgumentParser:
        """Create argument parser"""
        parser = argparse.ArgumentParser(
            prog='define-validator',
            description='FDA-compliant Define.xml Validator with 7-layer validation',
            formatter_class=argparse.RawDescriptionHelpFormatter,
            epilog="""
Examples:
  # Basic validation
  define-validator validate define.xml
  
  # Validate with custom schema
  define-validator validate define.xml --schema custom-schema.xsd
  
  # Generate HTML report
  define-validator validate define.xml --output report.html --format html
  
  # Download latest CDISC schemas
  define-validator download-schema --version 2.1
            """
        )
        
        subparsers = parser.add_subparsers(dest='command', help='Available commands')
        
        # Validate command
        validate_parser = subparsers.add_parser(
            'validate',
            help='Validate a define.xml file'
        )
        validate_parser.add_argument(
            'file',
            type=Path,
            help='Path to define.xml file'
        )
        validate_parser.add_argument(
            '--schema',
            type=Path,
            help='Path to XSD schema (auto-downloads if not provided)'
        )
        validate_parser.add_argument(
            '--output', '-o',
            type=Path,
            help='Output file for validation report'
        )
        validate_parser.add_argument(
            '--format', '-f',
            choices=['json', 'html', 'text'],
            default='text',
            help='Output format (default: text)'
        )
        validate_parser.add_argument(
            '--strict',
            action='store_true',
            help='Exit with error code 1 if any warnings found'
        )
        validate_parser.add_argument(
            '--layers',
            nargs='+',
            type=int,
            choices=range(1, 8),
            help='Specific validation layers to run (1-7)'
        )
        
        # Download schema command
        schema_parser = subparsers.add_parser(
            'download-schema',
            help='Download CDISC Define.xml schema'
        )
        schema_parser.add_argument(
            '--version',
            default='2.1',
            choices=['2.0', '2.1'],
            help='Schema version (default: 2.1)'
        )
        schema_parser.add_argument(
            '--output-dir',
            type=Path,
            help='Directory to save schema (default: ./schemas)'
        )
        
        # Info command
        info_parser = subparsers.add_parser(
            'info',
            help='Show validator information'
        )
        
        return parser
    
    def run(self, args: Optional[list] = None) -> int:
        """Run CLI application
        
        Args:
            args: Command line arguments (uses sys.argv if None)
            
        Returns:
            Exit code (0 for success, 1 for failure)
        """
        parsed_args = self.parser.parse_args(args)
        
        if not parsed_args.command:
            self.parser.print_help()
            return 0
        
        try:
            if parsed_args.command == 'validate':
                return self._validate(parsed_args)
            elif parsed_args.command == 'download-schema':
                return self._download_schema(parsed_args)
            elif parsed_args.command == 'info':
                return self._show_info()
        except Exception as e:
            print(f"\033[91mError: {str(e)}\033[0m", file=sys.stderr)
            return 1
    
    def _validate(self, args) -> int:
        """Execute validation command"""
        # Check file exists
        if not args.file.exists():
            print(f"\033[91mError: File not found: {args.file}\033[0m", file=sys.stderr)
            return 1
        
        # Get schema path
        schema_path = args.schema
        if not schema_path:
            print("\033[93mNo schema provided, auto-downloading...\033[0m")
            schema_path = self.schema_manager.get_schema('2.1')
            print(f"\033[92m✓ Schema downloaded: {schema_path}\033[0m")
        
        # Create validator
        print(f"\n\033[96mValidating: {args.file}\033[0m")
        validator = DefineValidator(str(schema_path))
        
        # Run validation
        if args.layers:
            print(f"\033[93mRunning layers: {', '.join(map(str, args.layers))}\033[0m")
            results = validator.run_partial_validation(str(args.file), args.layers)
        else:
            print("\033[93mRunning full 7-layer validation...\033[0m")
            results = validator.run_full_validation(str(args.file))
        
        # Generate report
        report_gen = ReportGenerator(results)
        
        if args.output:
            # Save to file
            if args.format == 'html':
                report_gen.generate_html(args.output)
                print(f"\n\033[92m✓ HTML report saved: {args.output}\033[0m")
            elif args.format == 'json':
                report_gen.generate_json(args.output)
                print(f"\n\033[92m✓ JSON report saved: {args.output}\033[0m")
            else:
                report_text = report_gen.generate_text()
                args.output.write_text(report_text)
                print(f"\n\033[92m✓ Text report saved: {args.output}\033[0m")
        else:
            # Print to console
            print(report_gen.generate_text())
        
        # Determine exit code
        error_count = sum(len(layer.get('errors', [])) for layer in results.get('layers', {}).values())
        warning_count = sum(len(layer.get('warnings', [])) for layer in results.get('layers', {}).values())
        
        if error_count > 0:
            print(f"\n\033[91m✗ Validation FAILED: {error_count} errors\033[0m")
            return 1
        elif warning_count > 0 and args.strict:
            print(f"\n\033[93m⚠ Validation WARNING: {warning_count} warnings (strict mode)\033[0m")
            return 1
        else:
            print(f"\n\033[92m✓ Validation PASSED\033[0m")
            if warning_count > 0:
                print(f"\033[93m  ({warning_count} warnings)\033[0m")
            return 0
    
    def _download_schema(self, args) -> int:
        """Execute download-schema command"""
        output_dir = args.output_dir or Path('./schemas')
        output_dir.mkdir(parents=True, exist_ok=True)
        
        print(f"\033[93mDownloading Define.xml {args.version} schema...\033[0m")
        schema_path = self.schema_manager.download_schema(args.version, output_dir)
        
        print(f"\033[92m✓ Schema downloaded: {schema_path}\033[0m")
        return 0
    
    def _show_info(self) -> int:
        """Show validator information"""
        print("""
\033[96m╔══════════════════════════════════════════════════════════════╗
║         Define.xml Validator - FDA Compliance Tool          ║
╚══════════════════════════════════════════════════════════════╝\033[0m

\033[93mValidation Layers:\033[0m
  1. XSD Schema Validation       - XML structure compliance
  2. Structural Validation       - Required ODM elements
  3. Cross-Reference Validation  - OID integrity checks
  4. Controlled Terminology      - CDISC CT compliance
  5. Completeness Validation     - Metadata coverage
  6. Computational Methods       - Method quality assessment
  7. Advanced Pattern Detection  - Consistency checks

\033[93mFeatures:\033[0m
  ✓ FDA 21 CFR Part 11 compliant
  ✓ CDISC Define.xml 2.0/2.1 support
  ✓ SHA-256 file integrity
  ✓ Comprehensive audit trail
  ✓ Multi-format reports (JSON/HTML/Text)

\033[93mUsage:\033[0m
  define-validator validate define.xml
  define-validator download-schema --version 2.1
  define-validator info

\033[93mDocumentation:\033[0m
  https://github.com/stiigg/define-xml-validator
        """)
        return 0


def main():
    """Entry point for CLI"""
    cli = CLI()
    sys.exit(cli.run())


if __name__ == '__main__':
    main()
