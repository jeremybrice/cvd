#!/usr/bin/env python3
"""
DEX Parser Engine

Standalone DEX (Data Exchange) file parser for vending machine audit data.
Supports comprehensive record types, PA record consolidation, and multi-manufacturer compatibility.

Features:
- PA Record Consolidation: Groups PA1-PA8 records by selection_number
- Error Validation: Duplicate detection, revenue consistency checks
- Multi-Manufacturer Support: Vendo, AMS, Crane adapters
- Comprehensive Record Types: 40+ DEX record type processors

Usage:
    from dex_parser import DEXParser
    
    parser = DEXParser()
    result = parser.parse_file(dex_content, filename)
    
    if result['success']:
        print(f"Parsed {len(result['pa_records'])} consolidated PA records")
    else:
        print(f"Parse failed: {result['error']['message']}")

Author: CVD System
Version: 2.0 (with PA consolidation)
"""

class DEXParser:
    """DEX file parser with comprehensive error handling and validation"""
    
    def __init__(self):
        """Initialize DEX parser with manufacturer adapters and record processors"""
        self.manufacturer_adapters = {
            'VA': self._vendo_adapter,
            'AMS': self._ams_adapter,
            'CN': self._crane_adapter,
            'STF': self._crane_adapter  # Crane uses STF prefix sometimes
        }
        self.record_processors = {
            'DXS': self._process_dxs,
            'DXE': self._process_dxe,
            'ID1': self._process_id1,
            'ID4': self._process_id4,
            'ID5': self._process_id5,
            'PA1': self._process_pa1,
            'PA2': self._process_pa2,
            'PA3': self._process_pa3,
            'PA4': self._process_pa4,
            'PA5': self._process_pa5,
            'PA7': self._process_pa7,
            'PA8': self._process_pa8,
            'VA1': self._process_va1,
            'VA2': self._process_va2,
            'VA3': self._process_va3,
            'CA1': self._process_ca1,
            'CA2': self._process_ca2,
            'CA3': self._process_ca3,
            'CA4': self._process_ca4,
            'CA6': self._process_ca6,
            'CA7': self._process_ca7,
            'CA8': self._process_ca8,
            'CA9': self._process_ca9,
            'CA10': self._process_ca10,
            'CA15': self._process_ca15,
            'CA17': self._process_ca17,
            'CA22': self._process_ca22,
            'DA1': self._process_da1,
            'DA2': self._process_da2,
            'DA3': self._process_da3,
            'DA4': self._process_da4,
            'DA5': self._process_da5,
            'DA6': self._process_da6,
            'DA10': self._process_da10,
            'ST': self._process_st,
            'CB1': self._process_cb1,
            'BA1': self._process_ba1,
            'EA1': self._process_ea1,
            'EA2': self._process_ea2,
            'EA3': self._process_ea3,
            'EA4': self._process_ea4,
            'EA5': self._process_ea5,
            'EA6': self._process_ea6,
            'EA7': self._process_ea7,
            'TA1': self._process_ta1,
            'TA2': self._process_ta2,
            'LS': self._process_ls,
            'LE': self._process_le,
            'MA5': self._process_ma5,
            'SD1': self._process_sd1,
            'G85': self._process_g85,
            'SE': self._process_se
        }
    
    def parse_file(self, content: str, filename: str) -> dict:
        """Parse DEX file content with comprehensive error handling and PA record consolidation"""
        try:
            lines = content.strip().split('\n')
            lines = [line.strip() for line in lines if line.strip()]
            
            if not lines:
                return {
                    'success': False,
                    'error': {
                        'line': 0,
                        'message': 'Empty file or no valid content found',
                        'field': 0
                    }
                }
            
            # Validate file structure
            structure_result = self._validate_structure(lines)
            if not structure_result['success']:
                return structure_result
            
            # Parse records
            parsed_records = []
            pa_records = []
            non_pa_records = []
            machine_info = {}
            
            for line_num, line in enumerate(lines, 1):
                try:
                    record_result = self._parse_record(line, line_num)
                    if not record_result['success']:
                        return record_result
                    
                    record = record_result['record']
                    parsed_records.append(record)
                    
                    # Extract machine info from DXS
                    if record['record_type'] == 'DXS':
                        machine_info = record['parsed_data']
                    
                    # Separate PA and non-PA records
                    if record['record_type'].startswith('PA'):
                        pa_records.append(record)
                    else:
                        non_pa_records.append(record)
                
                except Exception as e:
                    return {
                        'success': False,
                        'error': {
                            'line': line_num,
                            'record': line,
                            'message': f'Unexpected error parsing record: {str(e)}',
                            'field': 0
                        }
                    }
            
            # Consolidate PA records by selection_number
            consolidated_pa, pa_errors = self._consolidate_pa_records(pa_records)
            
            # NEW: Add grid pattern analysis
            grid_result = self._analyze_grid_patterns(consolidated_pa)
            
            # PA sales data mismatch is common and shouldn't fail parsing
            # Only fail on critical errors
            non_critical_errors = ["PA sales data mismatch", "Duplicate selections found"]
            has_only_non_critical = len(pa_errors) == 0 or all(
                any(non_critical in error for non_critical in non_critical_errors)
                for error in pa_errors
            )
            
            return {
                'success': has_only_non_critical,
                'machine_info': machine_info,
                'total_records': len(parsed_records),
                'parsed_records': non_pa_records,  # Only non-PA records
                'pa_records': consolidated_pa,
                'grid_analysis': grid_result,
                'errors': pa_errors,
                'parsed_successfully': has_only_non_critical,
                'error_message': self._format_error_messages(pa_errors) if pa_errors else None
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'line': 0,
                    'message': f'File parsing failed: {str(e)}',
                    'field': 0
                }
            }
    
    def _validate_structure(self, lines: list) -> dict:
        """Validate DEX file structure"""
        if len(lines) < 2:
            return {
                'success': False,
                'error': {
                    'line': 0,
                    'message': 'File too short - must contain at least DXS and DXE records',
                    'field': 0
                }
            }
        
        # Check for DXS header
        first_line = lines[0]
        if not first_line.startswith('DXS*'):
            return {
                'success': False,
                'error': {
                    'line': 1,
                    'record': first_line,
                    'message': 'File must start with DXS record',
                    'field': 0
                }
            }
        
        # Check for DXE trailer
        last_line = lines[-1]
        if not last_line.startswith('DXE*'):
            return {
                'success': False,
                'error': {
                    'line': len(lines),
                    'record': last_line,
                    'message': 'File must end with DXE record',
                    'field': 0
                }
            }
        
        return {'success': True}
    
    def _consolidate_pa_records(self, pa_records: list) -> tuple:
        """Consolidate PA records by selection_number with validation"""
        pa_groups = {}  # {selection_number: {PA1: record, PA2: record, ...}}
        errors = []
        current_selection = None
        
        # Group PA records by selection_number
        # PA1 contains selection_number, subsequent PA records belong to same selection
        for record in pa_records:
            pa_type = record['record_type']
            
            if pa_type == 'PA1':
                # PA1 starts a new selection group
                current_selection = record['parsed_data'].get('selection_number', '')
                if not current_selection:
                    continue  # Skip PA1 without selection number
                
                if current_selection not in pa_groups:
                    pa_groups[current_selection] = {}
                
                # Check for duplicate PA1 for same selection
                if pa_type in pa_groups[current_selection]:
                    error_msg = f"Duplicate selections found: {current_selection}"
                    if error_msg not in errors:
                        errors.append(error_msg)
                
                pa_groups[current_selection][pa_type] = record
            
            elif pa_type == 'PA7':
                # PA7 records have their own selection_number in the data
                pa7_selection = record['parsed_data'].get('selection_number', '')
                if pa7_selection:
                    if pa7_selection not in pa_groups:
                        pa_groups[pa7_selection] = {}
                    
                    # PA7 records can have multiple entries per selection (different payment types)
                    # Store them in a list
                    if pa_type not in pa_groups[pa7_selection]:
                        pa_groups[pa7_selection][pa_type] = []
                    pa_groups[pa7_selection][pa_type].append(record)
            
            elif current_selection and pa_type.startswith('PA'):
                # PA2, PA3, PA4, PA5, PA8 belong to current selection
                if current_selection not in pa_groups:
                    pa_groups[current_selection] = {}
                
                # Check for duplicate PA types within same selection (except PA7 which can have multiples)
                if pa_type in pa_groups[current_selection] and pa_type != 'PA7':
                    error_msg = f"Duplicate selections found: {current_selection}"
                    if error_msg not in errors:
                        errors.append(error_msg)
                
                pa_groups[current_selection][pa_type] = record
        
        # Validate and consolidate each group
        consolidated = []
        for selection_number, pa_group in pa_groups.items():
            # Validate PA1 exists (required)
            if 'PA1' not in pa_group:
                errors.append(f"Selection {selection_number} missing PA1")
                continue
            
            # Consolidate data from all PA records
            consolidated_data = self._merge_pa_data(pa_group)
            
            # Validate revenue consistency
            if not self._validate_pa_revenue(pa_group):
                errors.append("PA sales data mismatch")
            
            consolidated.append({
                'selection_number': selection_number,
                'data': consolidated_data,
                'line_number': pa_group['PA1']['line_number']  # Use PA1 line for reference
            })
        
        return consolidated, errors
    
    def _analyze_grid_patterns(self, consolidated_pa: list) -> dict:
        """Analyze PA records for grid patterns and add row/column assignments"""
        try:
            from grid_pattern_analyzer import GridPatternAnalyzer
            
            if not consolidated_pa:
                return {
                    'pattern_type': 'unknown',
                    'confidence': 0.0,
                    'grid_dimensions': {'rows': 0, 'columns': 0},
                    'errors': ['No PA records to analyze']
                }
            
            # Extract selection numbers
            selection_numbers = [record['selection_number'] for record in consolidated_pa if record.get('selection_number')]
            
            if not selection_numbers:
                return {
                    'pattern_type': 'unknown',
                    'confidence': 0.0,
                    'grid_dimensions': {'rows': 0, 'columns': 0},
                    'errors': ['No valid selection numbers found']
                }
            
            # Analyze patterns
            analyzer = GridPatternAnalyzer()
            grid_result = analyzer.analyze_selections(selection_numbers)
            
            # Add row/column data to consolidated records
            for record in consolidated_pa:
                selection = record.get('selection_number')
                if selection and selection in grid_result.get('assignments', {}):
                    assignment = grid_result['assignments'][selection]
                    record['data']['row'] = assignment['row']
                    record['data']['column'] = assignment['column']
                else:
                    record['data']['row'] = None
                    record['data']['column'] = None
            
            return grid_result
            
        except ImportError:
            return {
                'pattern_type': 'unknown',
                'confidence': 0.0,
                'grid_dimensions': {'rows': 0, 'columns': 0},
                'errors': ['Grid pattern analyzer not available']
            }
        except Exception as e:
            return {
                'pattern_type': 'unknown',
                'confidence': 0.0,
                'grid_dimensions': {'rows': 0, 'columns': 0},
                'errors': [f'Grid analysis failed: {str(e)}']
            }
    
    def _merge_pa_data(self, pa_group: dict) -> dict:
        """Merge data from PA1-PA5 records into single structure"""
        merged = {
            # Initialize all fields as None for missing data handling
            'selection_number': None,
            'price_cents': None,
            'capacity': None,
            'units_sold': None,
            'revenue_cents': None,
            'test_vends': None,
            'free_vends': None,
            'cash_sales': None,
            'cash_sales_cents': None,
            'cashless_sales': None,
            'cashless_sales_cents': None,
            'discount_sales': None,
            'discount_sales_cents': None,
            'last_sale_date': None,
            'last_sale_time': None
        }
        
        # Merge PA1 data (required)
        if 'PA1' in pa_group:
            pa1_data = pa_group['PA1']['parsed_data']
            merged.update({
                'selection_number': pa1_data.get('selection_number'),
                'price_cents': pa1_data.get('price_cents'),
                'capacity': pa1_data.get('capacity')
            })
        
        # Merge PA2 data (optional)
        if 'PA2' in pa_group:
            pa2_data = pa_group['PA2']['parsed_data']
            merged.update({
                'units_sold': pa2_data.get('units_sold'),
                'revenue_cents': pa2_data.get('revenue_cents'),
                'test_vends': pa2_data.get('test_vends'),
                'free_vends': pa2_data.get('free_vends')
            })
        
        # Merge PA3 data (optional)
        if 'PA3' in pa_group:
            pa3_data = pa_group['PA3']['parsed_data']
            merged.update({
                'cash_sales': pa3_data.get('cash_sales'),
                'cash_sales_cents': pa3_data.get('cash_sales_cents'),
                'cashless_sales': pa3_data.get('cashless_sales'),
                'cashless_sales_cents': pa3_data.get('cashless_sales_cents')
            })
        
        # Merge PA4 data (optional)
        if 'PA4' in pa_group:
            pa4_data = pa_group['PA4']['parsed_data']
            merged.update({
                'discount_sales': pa4_data.get('discount_sales'),
                'discount_sales_cents': pa4_data.get('discount_sales_cents', pa4_data.get('discount_sales', 0))  # Handle both field names
            })
        
        # Merge PA5 data (optional)
        if 'PA5' in pa_group:
            pa5_data = pa_group['PA5']['parsed_data']
            merged.update({
                'last_sale_date': pa5_data.get('last_sale_date'),
                'last_sale_time': pa5_data.get('last_sale_time')
            })
        
        return merged
    
    def _validate_pa_revenue(self, pa_group: dict) -> bool:
        """Validate revenue consistency between PA2 and PA3"""
        if 'PA2' not in pa_group or 'PA3' not in pa_group:
            return True  # Cannot validate without both records
        
        pa2_revenue = pa_group['PA2']['parsed_data'].get('revenue_cents', 0) or 0
        pa3_cash = pa_group['PA3']['parsed_data'].get('cash_sales_cents', 0) or 0
        pa3_cashless = pa_group['PA3']['parsed_data'].get('cashless_sales_cents', 0) or 0
        pa3_total = pa3_cash + pa3_cashless
        
        return pa2_revenue == pa3_total
    
    def _format_error_messages(self, errors: list) -> str:
        """Format error messages for database storage"""
        if not errors:
            return None
        
        # Group similar errors
        error_groups = {}
        for error in errors:
            if "Duplicate selections found:" in error:
                if "duplicates" not in error_groups:
                    error_groups["duplicates"] = []
                selection = error.split(": ")[1]
                error_groups["duplicates"].append(selection)
            elif error == "PA sales data mismatch":
                error_groups["revenue_mismatch"] = True
            elif "missing PA1" in error:
                if "missing_pa1" not in error_groups:
                    error_groups["missing_pa1"] = []
                selection = error.split()[1]
                error_groups["missing_pa1"].append(selection)
        
        # Format consolidated messages
        messages = []
        if "duplicates" in error_groups:
            selections = list(set(error_groups["duplicates"]))  # Remove duplicates
            messages.append(f"Duplicate selections found: {', '.join(selections)}")
        if "revenue_mismatch" in error_groups:
            messages.append("PA sales data mismatch")
        if "missing_pa1" in error_groups:
            selections = list(set(error_groups["missing_pa1"]))  # Remove duplicates
            messages.append(f"Missing PA1 for selections: {', '.join(selections)}")
        
        return "; ".join(messages)
    
    def _parse_record(self, line: str, line_number: int) -> dict:
        """Parse individual DEX record"""
        try:
            fields = line.split('*')
            if len(fields) < 2:
                return {
                    'success': False,
                    'error': {
                        'line': line_number,
                        'record': line,
                        'message': 'Invalid record format - must contain at least one asterisk delimiter',
                        'field': 0
                    }
                }
            
            record_type = fields[0]
            record_subtype = None
            
            # Handle record subtypes (e.g., PA1, PA2, CA17)
            if len(record_type) > 2 and record_type[2:].isdigit():
                record_subtype = record_type
                record_type = record_type[:2]
            
            # Process record based on type
            processor = self.record_processors.get(record_subtype or record_type, self._process_generic)
            parsed_data = processor(fields, line_number)
            
            return {
                'success': True,
                'record': {
                    'record_type': record_subtype or record_type,
                    'record_subtype': record_subtype,
                    'line_number': line_number,
                    'raw_record': line,
                    'parsed_data': parsed_data
                }
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': {
                    'line': line_number,
                    'record': line,
                    'message': f'Record parsing error: {str(e)}',
                    'field': 0
                }
            }
    
    def _process_dxs(self, fields: list, line_number: int) -> dict:
        """Process DXS (DEX Start) record"""
        return {
            'machine_serial': fields[1] if len(fields) > 1 else '',
            'manufacturer': fields[2] if len(fields) > 2 else '',
            'version': fields[3] if len(fields) > 3 else '',
            'revision': fields[4] if len(fields) > 4 else '',
            'options': fields[5] if len(fields) > 5 else ''
        }
    
    def _process_dxe(self, fields: list, line_number: int) -> dict:
        """Process DXE (DEX End) record"""
        return {
            'transmission_count': fields[1] if len(fields) > 1 else '',
            'checksum': fields[2] if len(fields) > 2 else ''
        }
    
    def _process_pa1(self, fields: list, line_number: int) -> dict:
        """Process PA1 (Product Setup) record"""
        return {
            'selection_number': fields[1] if len(fields) > 1 else '',
            'price_cents': self._parse_int(fields[2]) if len(fields) > 2 and fields[2] else 0,
            'capacity': self._parse_int(fields[3]) if len(fields) > 3 and fields[3] else 0
        }
    
    def _process_pa2(self, fields: list, line_number: int) -> dict:
        """Process PA2 (Product Sales) record"""
        return {
            'units_sold': self._parse_int(fields[1]) if len(fields) > 1 else 0,
            'revenue_cents': self._parse_int(fields[2]) if len(fields) > 2 else 0,
            'test_vends': self._parse_int(fields[3]) if len(fields) > 3 else 0,
            'test_vends_cents': self._parse_int(fields[4]) if len(fields) > 4 else 0,
            'free_vends': self._parse_int(fields[5]) if len(fields) > 5 else 0,
            'free_vends_cents': self._parse_int(fields[6]) if len(fields) > 6 else 0
        }
    
    def _process_pa3(self, fields: list, line_number: int) -> dict:
        """Process PA3 (Cash vs Cashless) record"""
        return {
            'cash_sales': self._parse_int(fields[1]) if len(fields) > 1 else 0,
            'cash_sales_cents': self._parse_int(fields[2]) if len(fields) > 2 else 0,
            'cashless_sales': self._parse_int(fields[3]) if len(fields) > 3 else 0,
            'cashless_sales_cents': self._parse_int(fields[4]) if len(fields) > 4 else 0
        }
    
    def _process_generic(self, fields: list, line_number: int) -> dict:
        """Process generic record - store fields as-is"""
        return {
            'fields': fields[1:] if len(fields) > 1 else []
        }
    
    # Add other record processors as needed
    def _process_id1(self, fields: list, line_number: int) -> dict:
        return {'machine_serial': fields[1] if len(fields) > 1 else '', 'model': fields[2] if len(fields) > 2 else ''}
    
    def _process_id4(self, fields: list, line_number: int) -> dict:
        return {'device_type': fields[1] if len(fields) > 1 else '', 'device_number': fields[2] if len(fields) > 2 else ''}
    
    def _process_id5(self, fields: list, line_number: int) -> dict:
        return {'date': fields[1] if len(fields) > 1 else '', 'time': fields[2] if len(fields) > 2 else ''}
    
    def _process_pa4(self, fields: list, line_number: int) -> dict:
        return {
            'discount_sales': self._parse_int(fields[1]) if len(fields) > 1 else 0,
            'discount_sales_cents': self._parse_int(fields[2]) if len(fields) > 2 else 0
        }
    
    def _process_pa5(self, fields: list, line_number: int) -> dict:
        return {'last_sale_date': fields[1] if len(fields) > 1 else '', 'last_sale_time': fields[2] if len(fields) > 2 else ''}
    
    def _process_pa7(self, fields: list, line_number: int) -> dict:
        return {
            'selection_number': fields[1] if len(fields) > 1 else '',
            'payment_type': fields[2] if len(fields) > 2 else '',
            'payment_data': fields[3:] if len(fields) > 3 else []
        }
    
    def _process_pa8(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_va1(self, fields: list, line_number: int) -> dict:
        return {'bills_in_validator': fields[1:] if len(fields) > 1 else []}
    
    def _process_va2(self, fields: list, line_number: int) -> dict:
        return {'total_bills_value': self._parse_int(fields[1]) if len(fields) > 1 else 0}
    
    def _process_va3(self, fields: list, line_number: int) -> dict:
        return {'coins_in_tubes': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca1(self, fields: list, line_number: int) -> dict:
        return {'card_reader_serial': fields[1] if len(fields) > 1 else '', 'card_reader_model': fields[2] if len(fields) > 2 else ''}
    
    def _process_ca2(self, fields: list, line_number: int) -> dict:
        return {'cashless_total_cents': self._parse_int(fields[1]) if len(fields) > 1 else 0}
    
    def _process_ca3(self, fields: list, line_number: int) -> dict:
        return {'cashless_transactions': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca4(self, fields: list, line_number: int) -> dict:
        return {'cashless_discount': self._parse_int(fields[1]) if len(fields) > 1 else 0}
    
    def _process_ca6(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca7(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca8(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca9(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca10(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca15(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca17(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ca22(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_da1(self, fields: list, line_number: int) -> dict:
        return {'diagnostic_device': fields[1] if len(fields) > 1 else '', 'device_model': fields[2] if len(fields) > 2 else ''}
    
    def _process_da2(self, fields: list, line_number: int) -> dict:
        return {'total_cash_in': self._parse_int(fields[1]) if len(fields) > 1 else 0}
    
    def _process_da3(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_da4(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_da5(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_da6(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_da10(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_st(self, fields: list, line_number: int) -> dict:
        return {'status_code': fields[1] if len(fields) > 1 else '', 'machine_number': fields[2] if len(fields) > 2 else ''}
    
    def _process_cb1(self, fields: list, line_number: int) -> dict:
        return {'control_board_serial': fields[1] if len(fields) > 1 else '', 'control_board_model': fields[2] if len(fields) > 2 else ''}
    
    def _process_ba1(self, fields: list, line_number: int) -> dict:
        return {'bill_acceptor_serial': fields[1] if len(fields) > 1 else '', 'bill_acceptor_model': fields[2] if len(fields) > 2 else ''}
    
    def _process_ea1(self, fields: list, line_number: int) -> dict:
        return {'event_type': fields[1] if len(fields) > 1 else '', 'event_data': fields[2:] if len(fields) > 2 else []}
    
    def _process_ea2(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ea3(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ea4(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ea5(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ea6(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ea7(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ta1(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ta2(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ls(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_le(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_ma5(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_sd1(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_g85(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _process_se(self, fields: list, line_number: int) -> dict:
        return {'fields': fields[1:] if len(fields) > 1 else []}
    
    def _parse_int(self, value: str) -> int:
        """Safely parse integer from string"""
        try:
            return int(value) if value and value.strip() else 0
        except ValueError:
            return 0
    
    def _vendo_adapter(self, fields: list) -> dict:
        """Vendo-specific field processing"""
        return {'fields': fields}
    
    def _ams_adapter(self, fields: list) -> dict:
        """AMS-specific field processing"""
        return {'fields': fields}
    
    def _crane_adapter(self, fields: list) -> dict:
        """Crane-specific field processing"""
        return {'fields': fields}