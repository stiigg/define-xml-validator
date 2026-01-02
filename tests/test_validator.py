"""
Unit tests for define.xml validator
"""

import pytest
import json
from pathlib import Path
from define_validator.validator import DefineXMLValidator


@pytest.fixture
def sample_define_xml(tmp_path):
    """Create a minimal valid define.xml for testing"""
    define_content = '''<?xml version="1.0" encoding="UTF-8"?>
<ODM xmlns="http://www.cdisc.org/ns/odm/v1.3"
     xmlns:def="http://www.cdisc.org/ns/def/v2.1"
     xmlns:xlink="http://www.w3.org/1999/xlink"
     FileOID="TEST.DEFINE.001"
     FileType="Snapshot"
     CreationDateTime="2026-01-02T10:00:00"
     ODMVersion="1.3.2">
  <Study OID="TEST.STUDY">
    <GlobalVariables>
      <StudyName>Test Study</StudyName>
      <StudyDescription>Test Description</StudyDescription>
      <ProtocolName>TEST-001</ProtocolName>
    </GlobalVariables>
    <MetaDataVersion OID="MDV.TEST" Name="Test MetaData" def:DefineVersion="2.1.0">
      <def:Standard OID="STD.SDTM" Name="SDTMIG" Type="IG" Version="3.4"/>
      
      <!-- Dataset Definition -->
      <ItemGroupDef OID="IG.DM" Name="DM" Repeating="No" def:Structure="One record per subject">
        <Description><TranslatedText>Demographics</TranslatedText></Description>
        <ItemRef ItemOID="IT.STUDYID" Mandatory="Yes"/>
        <ItemRef ItemOID="IT.USUBJID" Mandatory="Yes"/>
      </ItemGroupDef>
      
      <!-- Variable Definitions -->
      <ItemDef OID="IT.STUDYID" Name="STUDYID" DataType="text" Length="12" def:Origin="CRF">
        <Description><TranslatedText>Study Identifier</TranslatedText></Description>
      </ItemDef>
      
      <ItemDef OID="IT.USUBJID" Name="USUBJID" DataType="text" Length="20" def:Origin="Derived" def:MethodOID="MT.USUBJID">
        <Description><TranslatedText>Unique Subject Identifier</TranslatedText></Description>
      </ItemDef>
      
      <!-- Computational Method -->
      <def:MethodDef OID="MT.USUBJID" Name="USUBJID Derivation" Type="Computation">
        <Description><TranslatedText>USUBJID = STUDYID || "-" || SUBJID</TranslatedText></Description>
      </def:MethodDef>
    </MetaDataVersion>
  </Study>
</ODM>
'''
    
    define_file = tmp_path / "test_define.xml"
    define_file.write_text(define_content)
    return define_file


@pytest.fixture
def sample_schema(tmp_path):
    """Create a minimal XSD schema for testing"""
    # For testing, we'll just check if schema path exists
    # In production, you'd download the actual CDISC schema
    schema_file = tmp_path / "test_schema.xsd"
    schema_content = '''<?xml version="1.0" encoding="UTF-8"?>
<xs:schema xmlns:xs="http://www.w3.org/2001/XMLSchema">
  <xs:element name="ODM" type="xs:anyType"/>
</xs:schema>
'''
    schema_file.write_text(schema_content)
    return schema_file


class TestValidatorInitialization:
    """Test validator initialization and configuration"""
    
    def test_validator_init_success(self, sample_define_xml, sample_schema):
        """Test successful validator initialization"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        assert validator.root is not None
        assert validator.audit_trail['validation_id'].startswith('VAL-')
        assert len(validator.audit_trail['define_xml_sha256']) == 64
    
    def test_validator_init_missing_file(self, sample_schema):
        """Test initialization with missing define.xml"""
        with pytest.raises(FileNotFoundError):
            DefineXMLValidator(
                define_path="nonexistent.xml",
                schema_path=str(sample_schema)
            )
    
    def test_validator_init_missing_schema(self, sample_define_xml):
        """Test initialization with missing schema"""
        with pytest.raises(FileNotFoundError):
            DefineXMLValidator(
                define_path=str(sample_define_xml),
                schema_path="nonexistent.xsd"
            )


class TestFileIntegrity:
    """Test file integrity and security features"""
    
    def test_sha256_hash_generation(self, sample_define_xml, sample_schema):
        """Test SHA-256 hash generation for audit trail"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        file_hash = validator.audit_trail['define_xml_sha256']
        
        # SHA-256 produces 64-character hex string
        assert len(file_hash) == 64
        assert all(c in '0123456789abcdef' for c in file_hash)
    
    def test_validation_id_uniqueness(self, sample_define_xml, sample_schema):
        """Test that each validation generates unique ID"""
        validator1 = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        validator2 = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        assert validator1.audit_trail['validation_id'] != validator2.audit_trail['validation_id']


class TestBusinessRules:
    """Test business rule validations"""
    
    def test_derived_variables_with_methods(self, sample_define_xml, sample_schema):
        """Test that derived variables have MethodOID"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        result = validator.validate_layer3_business_rules()
        
        # Our sample has a properly defined derived variable
        derived_errors = [e for e in result['errors'] if e['error_id'] == 'BUS-001']
        assert len(derived_errors) == 0
    
    def test_codelist_reference_integrity(self, sample_define_xml, sample_schema):
        """Test CodeListOID reference validation"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        result = validator.validate_layer3_business_rules()
        
        # Check for invalid CodeList references
        codelist_errors = [e for e in result['errors'] if e['error_id'] == 'BUS-002']
        assert isinstance(codelist_errors, list)


class TestFullValidation:
    """Test complete validation workflow"""
    
    def test_run_full_validation(self, sample_define_xml, sample_schema):
        """Test complete validation workflow"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        results = validator.run_full_validation()
        
        assert 'final_status' in results
        assert 'validation_id' in results
        assert 'total_errors' in results
        assert 'results' in results
        assert results['final_status'] in ['PASS', 'FAIL']
    
    def test_export_report(self, sample_define_xml, sample_schema, tmp_path):
        """Test report export functionality"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        validator.run_full_validation()
        
        report_path = tmp_path / "test_report.json"
        validator.export_report(str(report_path))
        
        # Verify report was created
        assert report_path.exists()
        
        # Verify report content
        with open(report_path, 'r') as f:
            report = json.load(f)
        
        assert 'validation_id' in report
        assert 'timestamp' in report
        assert 'file_hash' in report
        assert 'results' in report


class TestConfiguration:
    """Test configuration loading"""
    
    def test_default_configuration(self, sample_define_xml, sample_schema):
        """Test default configuration is loaded"""
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema)
        )
        
        assert 'required_race_terms' in validator.config
        assert 'validation_criticality' in validator.config
        assert len(validator.config['required_race_terms']) == 9
    
    def test_custom_configuration(self, sample_define_xml, sample_schema, tmp_path):
        """Test custom configuration loading"""
        config_content = {
            "validation_criticality": {
                "derived_no_method": "MAJOR"
            }
        }
        
        config_file = tmp_path / "config.json"
        with open(config_file, 'w') as f:
            json.dump(config_content, f)
        
        validator = DefineXMLValidator(
            define_path=str(sample_define_xml),
            schema_path=str(sample_schema),
            config_path=str(config_file)
        )
        
        assert validator.config['validation_criticality']['derived_no_method'] == 'MAJOR'
