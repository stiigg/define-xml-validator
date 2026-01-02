# Test Fixtures

This directory contains sample define.xml files for testing.

## Files

- `sample_define.xml` - Minimal valid define.xml for basic testing
- `invalid_define.xml` - Intentionally invalid file for error testing

## Creating Test Fixtures

To create your own test fixtures:

1. Start with a minimal ODM structure
2. Add MetaDataVersion with define-xml extensions
3. Include at least one dataset (ItemGroupDef)
4. Include at least one variable (ItemDef)
5. For derived variables, include MethodDef

## Example Minimal Define.xml

See the test files in this directory for examples of:
- Valid define.xml structure
- Derived variables with methods
- CodeList definitions
- Controlled terminology

## Using Custom Test Files

To test with your own define.xml files:

```python
import pytest
from define_validator.validator import DefineXMLValidator

def test_my_define():
    validator = DefineXMLValidator(
        define_path='path/to/your/define.xml',
        schema_path='schemas/define-xml-2.1.xsd'
    )
    results = validator.run_full_validation()
    assert results['final_status'] == 'PASS'
```
