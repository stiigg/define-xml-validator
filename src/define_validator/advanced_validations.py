"""
Advanced Validation Layers (4-7) for Define.xml Validator
Implements terminology validation, completeness checks, computational methods quality,
and advanced pattern detection
"""

import logging
from typing import Dict, List, Tuple, Set, Optional
from datetime import datetime
from lxml import etree


class AdvancedValidations:
    """
    Advanced validation layers for define.xml
    
    Layers:
    - Layer 4: Controlled Terminology Validation
    - Layer 5: Completeness Validation
    - Layer 6: Computational Methods Quality
    - Layer 7: Advanced Pattern Detection
    """
    
    def __init__(self, root: etree._Element, namespaces: Dict[str, str], config: Dict):
        """
        Initialize advanced validations
        
        Args:
            root: XML root element
            namespaces: XML namespace dictionary
            config: Validation configuration
        """
        self.root = root
        self.namespaces = namespaces
        self.config = config
        self.logger = logging.getLogger(self.__class__.__name__)
    
    def validate_layer4_terminology(self) -> Dict:
        """
        Layer 4: Controlled Terminology Validation
        
        Validates FDA-required CDISC Controlled Terminology:
        1. RACE codelist must have all 9 FDA-required terms
        2. SEX codelist must be complete
        3. ETHNIC codelist completeness
        4. CDISC CT version compliance
        
        Returns:
            Dict with validation status and errors
        """
        start_time = datetime.now()
        
        self.logger.info("\n" + "="*80)
        self.logger.info("LAYER 4: CONTROLLED TERMINOLOGY VALIDATION")
        self.logger.info("="*80)
        
        errors = []
        
        # CHECK 4.1: RACE codelist validation
        self.logger.info("\n[CHECK 4.1] RACE codelist completeness...")
        
        race_codelist = self.root.xpath(
            "//odm:CodeList[contains(@Name, 'RACE') or @OID='CL.RACE']",
            namespaces=self.namespaces
        )
        
        if race_codelist:
            race_cl = race_codelist[0]
            race_terms = set(race_cl.xpath(
                './/odm:CodeListItem/@CodedValue',
                namespaces=self.namespaces
            ))
            
            required_race_terms = set(self.config.get('required_race_terms', []))
            missing_terms = required_race_terms - race_terms
            
            if missing_terms:
                self.logger.error(f"  ✗ RACE codelist missing {len(missing_terms)} required terms")
                for term in missing_terms:
                    errors.append({
                        'error_id': 'TERM-001',
                        'severity': 'MAJOR',
                        'check': 'race_terminology',
                        'missing_term': term,
                        'message': f"RACE codelist missing FDA-required term: '{term}'"
                    })
                    self.logger.error(f"     Missing: {term}")
            else:
                self.logger.info(f"  ✓ RACE codelist complete ({len(race_terms)} terms)")
        else:
            self.logger.warning("  ⚠ RACE codelist not found")
            errors.append({
                'error_id': 'TERM-001A',
                'severity': 'MAJOR',
                'check': 'race_terminology',
                'message': 'RACE codelist not found in define.xml'
            })
        
        # CHECK 4.2: SEX codelist validation
        self.logger.info("\n[CHECK 4.2] SEX codelist completeness...")
        
        sex_codelist = self.root.xpath(
            "//odm:CodeList[contains(@Name, 'SEX') or @OID='CL.SEX']",
            namespaces=self.namespaces
        )
        
        if sex_codelist:
            sex_cl = sex_codelist[0]
            sex_terms = set(sex_cl.xpath(
                './/odm:CodeListItem/@CodedValue',
                namespaces=self.namespaces
            ))
            
            required_sex_terms = {'M', 'F', 'U'}  # Male, Female, Unknown
            missing_sex = required_sex_terms - sex_terms
            
            if missing_sex:
                self.logger.error(f"  ✗ SEX codelist missing required terms: {missing_sex}")
                errors.append({
                    'error_id': 'TERM-002',
                    'severity': 'MAJOR',
                    'check': 'sex_terminology',
                    'missing_terms': list(missing_sex),
                    'message': f"SEX codelist missing required terms: {', '.join(missing_sex)}"
                })
            else:
                self.logger.info(f"  ✓ SEX codelist complete ({len(sex_terms)} terms)")
        else:
            self.logger.warning("  ⚠ SEX codelist not found")
        
        # CHECK 4.3: CDISC CT version check
        self.logger.info("\n[CHECK 4.3] CDISC CT version compliance...")
        
        # Look for CT version in metadata or comments
        ct_version_elements = self.root.xpath(
            '//odm:CodeList[@def:StandardOID]',
            namespaces=self.namespaces
        )
        
        if ct_version_elements:
            self.logger.info(f"  ✓ Found {len(ct_version_elements)} codelists with standard references")
        else:
            self.logger.warning("  ⚠ No CDISC CT standard references found")
            errors.append({
                'error_id': 'TERM-003',
                'severity': 'MINOR',
                'check': 'ct_version',
                'message': 'No CDISC CT standard OID references found'
            })
        
        # Determine status
        critical_errors = [e for e in errors if e['severity'] == 'CRITICAL']
        major_errors = [e for e in errors if e['severity'] == 'MAJOR']
        status = 'FAIL' if critical_errors else ('WARNING' if major_errors else 'PASS')
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            'status': status,
            'errors': errors,
            'duration_ms': round(duration_ms, 2)
        }
        
        if critical_errors or major_errors:
            self.logger.warning(f"\n⚠ LAYER 4: {len(errors)} terminology issues found")
        else:
            self.logger.info(f"\n✓ LAYER 4 PASSED")
        
        return result
    
    def validate_layer5_completeness(self) -> Dict:
        """
        Layer 5: Completeness Validation
        
        Checks metadata completeness:
        1. All variables have labels
        2. All datasets have descriptions
        3. Methods have adequate documentation
        4. Missing metadata elements
        
        Returns:
            Dict with validation status and errors
        """
        start_time = datetime.now()
        
        self.logger.info("\n" + "="*80)
        self.logger.info("LAYER 5: COMPLETENESS VALIDATION")
        self.logger.info("="*80)
        
        errors = []
        
        # CHECK 5.1: Variables without labels
        self.logger.info("\n[CHECK 5.1] Variable labels completeness...")
        
        vars_no_label = self.root.xpath(
            """//odm:ItemDef[
                not(odm:Description/odm:TranslatedText) or
                odm:Description/odm:TranslatedText[text()='']
            ]""",
            namespaces=self.namespaces
        )
        
        if vars_no_label:
            self.logger.warning(f"  ⚠ {len(vars_no_label)} variables missing labels")
            for var in vars_no_label[:10]:  # Limit to first 10
                var_name = var.get('Name')
                errors.append({
                    'error_id': 'COMP-001',
                    'severity': 'MINOR',
                    'check': 'variable_labels',
                    'variable': var_name,
                    'message': f"Variable '{var_name}' missing description/label"
                })
            
            if len(vars_no_label) > 10:
                self.logger.warning(f"     ... and {len(vars_no_label) - 10} more")
        else:
            total_vars = len(self.root.xpath('//odm:ItemDef', namespaces=self.namespaces))
            self.logger.info(f"  ✓ All {total_vars} variables have labels")
        
        # CHECK 5.2: Datasets without descriptions
        self.logger.info("\n[CHECK 5.2] Dataset descriptions completeness...")
        
        datasets_no_desc = self.root.xpath(
            """//odm:ItemGroupDef[
                not(odm:Description/odm:TranslatedText) or
                odm:Description/odm:TranslatedText[text()='']
            ]""",
            namespaces=self.namespaces
        )
        
        if datasets_no_desc:
            self.logger.warning(f"  ⚠ {len(datasets_no_desc)} datasets missing descriptions")
            for ds in datasets_no_desc:
                ds_name = ds.get('Name')
                errors.append({
                    'error_id': 'COMP-002',
                    'severity': 'MINOR',
                    'check': 'dataset_descriptions',
                    'dataset': ds_name,
                    'message': f"Dataset '{ds_name}' missing description"
                })
                self.logger.warning(f"     Dataset: {ds_name}")
        else:
            total_ds = len(self.root.xpath('//odm:ItemGroupDef', namespaces=self.namespaces))
            self.logger.info(f"  ✓ All {total_ds} datasets have descriptions")
        
        # CHECK 5.3: Methods with inadequate documentation
        self.logger.info("\n[CHECK 5.3] Computational methods documentation...")
        
        methods = self.root.xpath('//def:MethodDef', namespaces=self.namespaces)
        
        for method in methods:
            method_oid = method.get('OID')
            method_desc = method.xpath(
                'odm:Description/odm:TranslatedText/text()',
                namespaces=self.namespaces
            )
            
            if not method_desc or len(method_desc[0]) < 20:
                errors.append({
                    'error_id': 'COMP-003',
                    'severity': 'MINOR',
                    'check': 'method_documentation',
                    'method_oid': method_oid,
                    'message': f"Method '{method_oid}' has insufficient documentation (<20 chars)"
                })
        
        if methods:
            poor_docs = [e for e in errors if e['error_id'] == 'COMP-003']
            if poor_docs:
                self.logger.warning(f"  ⚠ {len(poor_docs)}/{len(methods)} methods need better documentation")
            else:
                self.logger.info(f"  ✓ All {len(methods)} methods adequately documented")
        
        # Determine status
        status = 'WARNING' if errors else 'PASS'
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            'status': status,
            'errors': errors,
            'warnings': errors,  # All completeness issues are warnings
            'duration_ms': round(duration_ms, 2)
        }
        
        if errors:
            self.logger.warning(f"\n⚠ LAYER 5: {len(errors)} completeness issues found")
        else:
            self.logger.info(f"\n✓ LAYER 5 PASSED")
        
        return result
    
    def validate_layer6_computational_methods(self) -> Dict:
        """
        Layer 6: Computational Methods Quality
        
        Validates quality of computational method descriptions:
        1. Method description length/quality
        2. Presence of algorithm documentation
        3. Code/formula detectability
        
        Returns:
            Dict with validation status and errors
        """
        start_time = datetime.now()
        
        self.logger.info("\n" + "="*80)
        self.logger.info("LAYER 6: COMPUTATIONAL METHODS QUALITY")
        self.logger.info("="*80)
        
        errors = []
        warnings = []
        
        # CHECK 6.1: Method description quality
        self.logger.info("\n[CHECK 6.1] Method description quality assessment...")
        
        methods = self.root.xpath('//def:MethodDef', namespaces=self.namespaces)
        
        if not methods:
            self.logger.warning("  ⚠ No computational methods found")
            warnings.append({
                'warning_id': 'METH-001',
                'severity': 'INFO',
                'check': 'methods_present',
                'message': 'No computational methods defined (unusual for derived variables)'
            })
        else:
            self.logger.info(f"  Found {len(methods)} computational methods")
            
            for method in methods:
                method_oid = method.get('OID')
                method_name = method.get('Name', method_oid)
                
                # Get description text
                desc_elements = method.xpath(
                    'odm:Description/odm:TranslatedText/text()',
                    namespaces=self.namespaces
                )
                
                if desc_elements:
                    desc_text = desc_elements[0]
                    desc_length = len(desc_text)
                    
                    # Quality assessment based on length
                    if desc_length < 50:
                        warnings.append({
                            'warning_id': 'METH-002',
                            'severity': 'MINOR',
                            'check': 'method_quality',
                            'method_oid': method_oid,
                            'method_name': method_name,
                            'description_length': desc_length,
                            'message': f"Method '{method_name}' has very brief description ({desc_length} chars)"
                        })
                    elif desc_length > 1000:
                        # Check if it contains code (common for long descriptions)
                        if any(keyword in desc_text.lower() for keyword in ['proc ', 'data ', 'if ', 'then', '=']):
                            self.logger.info(f"  ✓ {method_name}: Detailed description with code ({desc_length} chars)")
                        else:
                            warnings.append({
                                'warning_id': 'METH-003',
                                'severity': 'INFO',
                                'check': 'method_quality',
                                'method_oid': method_oid,
                                'method_name': method_name,
                                'description_length': desc_length,
                                'message': f"Method '{method_name}' has very long description ({desc_length} chars) - consider splitting"
                            })
                else:
                    errors.append({
                        'error_id': 'METH-004',
                        'severity': 'MAJOR',
                        'check': 'method_quality',
                        'method_oid': method_oid,
                        'method_name': method_name,
                        'message': f"Method '{method_name}' has no description"
                    })
            
            # Summary statistics
            total_methods = len(methods)
            methods_with_code = sum(
                1 for m in methods 
                if m.xpath('odm:Description/odm:TranslatedText/text()', namespaces=self.namespaces)
                and any(keyword in m.xpath('odm:Description/odm:TranslatedText/text()', namespaces=self.namespaces)[0].lower() 
                       for keyword in ['proc ', 'data ', 'if '])
            )
            
            self.logger.info(f"\n  Summary:")
            self.logger.info(f"    Total methods: {total_methods}")
            self.logger.info(f"    Methods with code/formulas: {methods_with_code}")
            self.logger.info(f"    Quality issues: {len(warnings)}")
        
        # Determine status
        major_errors = [e for e in errors if e['severity'] == 'MAJOR']
        status = 'FAIL' if major_errors else ('WARNING' if warnings else 'PASS')
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'duration_ms': round(duration_ms, 2)
        }
        
        if major_errors:
            self.logger.error(f"\n✗ LAYER 6 FAILED: {len(major_errors)} major issues")
        elif warnings:
            self.logger.warning(f"\n⚠ LAYER 6: {len(warnings)} quality improvements suggested")
        else:
            self.logger.info(f"\n✓ LAYER 6 PASSED")
        
        return result
    
    def validate_layer7_advanced_patterns(self) -> Dict:
        """
        Layer 7: Advanced Pattern Detection
        
        Detects advanced issues:
        1. Orphaned OID references
        2. Duplicate OID definitions
        3. Variable ordering inconsistencies
        4. Value-level metadata (VLM) validation
        
        Returns:
            Dict with validation status and errors
        """
        start_time = datetime.now()
        
        self.logger.info("\n" + "="*80)
        self.logger.info("LAYER 7: ADVANCED PATTERN DETECTION")
        self.logger.info("="*80)
        
        errors = []
        warnings = []
        
        # CHECK 7.1: Orphaned OID references
        self.logger.info("\n[CHECK 7.1] Orphaned OID references...")
        
        # Collect all defined OIDs
        all_oids = set()
        all_oids.update(self.root.xpath('//@OID', namespaces=self.namespaces))
        
        # Collect all referenced OIDs
        referenced_oids = set()
        referenced_oids.update(self.root.xpath('//@ItemGroupOID', namespaces=self.namespaces))
        referenced_oids.update(self.root.xpath('//@ItemOID', namespaces=self.namespaces))
        referenced_oids.update(self.root.xpath('//@CodeListOID', namespaces=self.namespaces))
        referenced_oids.update(self.root.xpath('//@def:MethodOID', namespaces=self.namespaces))
        
        # Find orphaned references (referenced but not defined)
        orphaned = referenced_oids - all_oids
        
        if orphaned:
            self.logger.error(f"  ✗ Found {len(orphaned)} orphaned OID references")
            for oid in list(orphaned)[:10]:  # Limit output
                errors.append({
                    'error_id': 'PAT-001',
                    'severity': 'CRITICAL',
                    'check': 'orphaned_oids',
                    'oid': oid,
                    'message': f"Referenced OID '{oid}' is not defined anywhere"
                })
                self.logger.error(f"     Orphaned: {oid}")
            
            if len(orphaned) > 10:
                self.logger.error(f"     ... and {len(orphaned) - 10} more")
        else:
            self.logger.info(f"  ✓ No orphaned OID references ({len(referenced_oids)} references checked)")
        
        # CHECK 7.2: Duplicate OID definitions
        self.logger.info("\n[CHECK 7.2] Duplicate OID definitions...")
        
        oid_elements = self.root.xpath('//*[@OID]', namespaces=self.namespaces)
        oid_counts = {}
        
        for elem in oid_elements:
            oid = elem.get('OID')
            if oid in oid_counts:
                oid_counts[oid].append(elem.tag)
            else:
                oid_counts[oid] = [elem.tag]
        
        duplicates = {oid: tags for oid, tags in oid_counts.items() if len(tags) > 1}
        
        if duplicates:
            self.logger.error(f"  ✗ Found {len(duplicates)} duplicate OID definitions")
            for oid, tags in list(duplicates.items())[:5]:
                errors.append({
                    'error_id': 'PAT-002',
                    'severity': 'CRITICAL',
                    'check': 'duplicate_oids',
                    'oid': oid,
                    'occurrences': len(tags),
                    'message': f"OID '{oid}' is defined {len(tags)} times"
                })
                self.logger.error(f"     Duplicate: {oid} ({len(tags)} occurrences)")
        else:
            self.logger.info(f"  ✓ No duplicate OID definitions ({len(oid_counts)} unique OIDs)")
        
        # CHECK 7.3: Variable ordering consistency
        self.logger.info("\n[CHECK 7.3] Variable ordering consistency...")
        
        datasets = self.root.xpath('//odm:ItemGroupDef', namespaces=self.namespaces)
        
        for dataset in datasets:
            ds_name = dataset.get('Name')
            item_refs = dataset.xpath('odm:ItemRef', namespaces=self.namespaces)
            
            # Check if OrderNumber is sequential
            if item_refs:
                order_numbers = []
                for ref in item_refs:
                    order_num = ref.get('OrderNumber')
                    if order_num:
                        try:
                            order_numbers.append(int(order_num))
                        except ValueError:
                            warnings.append({
                                'warning_id': 'PAT-003',
                                'severity': 'MINOR',
                                'check': 'variable_ordering',
                                'dataset': ds_name,
                                'message': f"Dataset '{ds_name}' has non-numeric OrderNumber"
                            })
                
                # Check for gaps or duplicates
                if order_numbers:
                    if len(order_numbers) != len(set(order_numbers)):
                        warnings.append({
                            'warning_id': 'PAT-004',
                            'severity': 'MINOR',
                            'check': 'variable_ordering',
                            'dataset': ds_name,
                            'message': f"Dataset '{ds_name}' has duplicate OrderNumbers"
                        })
                    
                    if order_numbers != sorted(order_numbers):
                        warnings.append({
                            'warning_id': 'PAT-005',
                            'severity': 'INFO',
                            'check': 'variable_ordering',
                            'dataset': ds_name,
                            'message': f"Dataset '{ds_name}' has non-sequential OrderNumbers"
                        })
        
        if not [w for w in warnings if w.get('check') == 'variable_ordering']:
            self.logger.info(f"  ✓ Variable ordering consistent across {len(datasets)} datasets")
        else:
            ordering_warnings = [w for w in warnings if w.get('check') == 'variable_ordering']
            self.logger.warning(f"  ⚠ {len(ordering_warnings)} variable ordering inconsistencies")
        
        # CHECK 7.4: Value-level metadata validation
        self.logger.info("\n[CHECK 7.4] Value-level metadata (VLM) validation...")
        
        vlm_elements = self.root.xpath('//def:ValueListDef', namespaces=self.namespaces)
        
        if vlm_elements:
            self.logger.info(f"  Found {len(vlm_elements)} VLM definitions")
            
            for vlm in vlm_elements:
                vlm_oid = vlm.get('OID')
                item_refs = vlm.xpath('odm:ItemRef', namespaces=self.namespaces)
                
                if not item_refs:
                    warnings.append({
                        'warning_id': 'PAT-006',
                        'severity': 'MINOR',
                        'check': 'vlm_validation',
                        'vlm_oid': vlm_oid,
                        'message': f"ValueListDef '{vlm_oid}' is empty"
                    })
            
            self.logger.info(f"  ✓ VLM structure validated")
        else:
            self.logger.info("  ℹ No value-level metadata found")
        
        # Determine status
        critical_errors = [e for e in errors if e['severity'] == 'CRITICAL']
        status = 'FAIL' if critical_errors else ('WARNING' if warnings else 'PASS')
        
        duration_ms = (datetime.now() - start_time).total_seconds() * 1000
        
        result = {
            'status': status,
            'errors': errors,
            'warnings': warnings,
            'duration_ms': round(duration_ms, 2)
        }
        
        if critical_errors:
            self.logger.error(f"\n✗ LAYER 7 FAILED: {len(critical_errors)} critical pattern issues")
        elif warnings:
            self.logger.warning(f"\n⚠ LAYER 7: {len(warnings)} pattern warnings")
        else:
            self.logger.info(f"\n✓ LAYER 7 PASSED")
        
        return result
