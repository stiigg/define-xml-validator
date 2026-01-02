#!/usr/bin/env python
"""
CI/CD Integration Example

This script shows how to integrate the validator into your CI/CD pipeline.
It validates all define.xml files in a directory and generates a summary report.
"""

import sys
import json
from pathlib import Path
from typing import List, Dict

# Add src to path for development
sys.path.insert(0, str(Path(__file__).parent.parent / 'src'))

from define_validator.validator import DefineXMLValidator


def validate_directory(define_dir: Path, schema_path: Path) -> Dict:
    """
    Validate all define.xml files in a directory
    
    Args:
        define_dir: Directory containing define.xml files
        schema_path: Path to CDISC schema
    
    Returns:
        Summary of all validation results
    """
    results_summary = {
        'total_files': 0,
        'passed': 0,
        'failed': 0,
        'files': []
    }
    
    # Find all XML files
    xml_files = list(define_dir.glob('**/*.xml'))
    results_summary['total_files'] = len(xml_files)
    
    print(f"\nFound {len(xml_files)} XML files to validate\n")
    
    for xml_file in xml_files:
        print(f"\nValidating: {xml_file.name}")
        print("-" * 60)
        
        try:
            validator = DefineXMLValidator(
                define_path=str(xml_file),
                schema_path=str(schema_path)
            )
            
            result = validator.run_full_validation()
            
            file_result = {
                'file': xml_file.name,
                'status': result['final_status'],
                'total_errors': result['total_errors'],
                'critical_errors': result['critical_errors'],
                'validation_id': result['validation_id']
            }
            
            results_summary['files'].append(file_result)
            
            if result['final_status'] == 'PASS':
                results_summary['passed'] += 1
                print(f"✓ PASSED")
            else:
                results_summary['failed'] += 1
                print(f"✗ FAILED ({result['critical_errors']} critical errors)")
            
            # Export individual report
            report_name = f"{xml_file.stem}_validation.json"
            validator.export_report(report_name)
        
        except Exception as e:
            print(f"✗ ERROR: {e}")
            results_summary['failed'] += 1
            results_summary['files'].append({
                'file': xml_file.name,
                'status': 'ERROR',
                'error': str(e)
            })
    
    return results_summary


def main():
    """
    Main CI/CD validation workflow
    """
    print("\n" + "="*80)
    print("Define.xml Validator - CI/CD Integration")
    print("="*80)
    
    # Configure paths
    define_dir = Path('define')
    schema_path = Path('schemas/define-xml-2.1.xsd')
    summary_report = Path('validation_summary.json')
    
    # Check if directory exists
    if not define_dir.exists():
        print(f"\n✗ Error: Directory not found: {define_dir}")
        print("Please create the 'define' directory and add your define.xml files.")
        sys.exit(1)
    
    # Check if schema exists
    if not schema_path.exists():
        print(f"\n✗ Error: Schema not found: {schema_path}")
        print("Please download the CDISC schema first.")
        sys.exit(1)
    
    # Validate all files
    results = validate_directory(define_dir, schema_path)
    
    # Print summary
    print("\n" + "="*80)
    print("VALIDATION SUMMARY")
    print("="*80)
    print(f"Total Files: {results['total_files']}")
    print(f"Passed: {results['passed']} ✓")
    print(f"Failed: {results['failed']} ✗")
    print("\nFile Details:")
    
    for file_result in results['files']:
        status_icon = "✓" if file_result['status'] == 'PASS' else "✗"
        print(f"  {status_icon} {file_result['file']}: {file_result['status']}")
    
    # Save summary report
    with open(summary_report, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\nSummary report saved to: {summary_report}")
    
    # Exit with appropriate code
    if results['failed'] == 0:
        print("\n✓ All validations PASSED")
        sys.exit(0)
    else:
        print(f"\n✗ {results['failed']} validation(s) FAILED")
        sys.exit(1)


if __name__ == '__main__':
    main()
