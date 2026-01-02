#!/usr/bin/env python
"""
Basic usage example for define.xml validator

This script demonstrates the simplest way to validate a define.xml file.
"""

import sys
from pathlib import Path

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from define_validator.validator import DefineXMLValidator


def main():
    """
    Run basic validation on a define.xml file
    """
    print("\n" + "="*80)
    print("Define.xml Validator - Basic Usage Example")
    print("="*80 + "\n")
    
    # Configure paths
    # NOTE: You need to download the actual CDISC schema first
    define_path = 'tests/fixtures/sample_define.xml'
    schema_path = 'schemas/define-xml-2.1.xsd'
    
    try:
        # Initialize validator
        print(f"Initializing validator...")
        validator = DefineXMLValidator(
            define_path=define_path,
            schema_path=schema_path
        )
        
        print(f"Validation ID: {validator.audit_trail['validation_id']}")
        print(f"File SHA-256: {validator.audit_trail['define_xml_sha256'][:16]}...\n")
        
        # Run full validation
        print("Running validation...\n")
        results = validator.run_full_validation()
        
        # Display results
        print("\n" + "="*80)
        print("VALIDATION RESULTS")
        print("="*80)
        print(f"Status: {results['final_status']}")
        print(f"Total Errors: {results['total_errors']}")
        print(f"Critical Errors: {results['critical_errors']}")
        
        # Export report
        report_path = 'validation_report.json'
        validator.export_report(report_path)
        print(f"\nDetailed report saved to: {report_path}")
        
        # Exit with appropriate code
        if results['final_status'] == 'PASS':
            print("\n✓ Validation PASSED - ready for submission")
            sys.exit(0)
        else:
            print("\n✗ Validation FAILED - fix errors before submission")
            sys.exit(1)
    
    except FileNotFoundError as e:
        print(f"\n✗ Error: {e}")
        print("\nPlease ensure:")
        print("  1. Your define.xml file exists at the specified path")
        print("  2. CDISC schema is downloaded to schemas/define-xml-2.1.xsd")
        print("\nTo download the schema:")
        print("  wget -O schemas/define-xml-2.1.xsd \\")
        print("    https://www.cdisc.org/sites/default/files/2021-09/define-xml-2.1.xsd")
        sys.exit(1)
    
    except Exception as e:
        print(f"\n✗ Unexpected error: {e}")
        sys.exit(1)


if __name__ == '__main__':
    main()
