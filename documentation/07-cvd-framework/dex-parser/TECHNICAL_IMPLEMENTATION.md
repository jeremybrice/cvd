# DEX Parser Technical Implementation


## Metadata
- **ID**: 07_CVD_FRAMEWORK_DEX_PARSER_TECHNICAL_IMPLEMENTATION
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #cvd-specific #data-exchange #data-layer #database #debugging #device-management #dex-parser #domain #machine-learning #metrics #optimization #quality-assurance #reporting #testing #troubleshooting #vending #vending-machine
- **Intent**: The DEX Parser system is built as a modular, extensible engine capable of processing industry-standard vending machine audit files
- **Audience**: developers, end users, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/dex-parser/
- **Category**: Dex Parser
- **Search Keywords**: ####, data, device, dex, implementation, integer, logic, merging, parser, parsing, safe, technical, vending

## Architecture Overview

The DEX Parser system is built as a modular, extensible engine capable of processing industry-standard vending machine audit files. The architecture emphasizes error resilience, multi-manufacturer compatibility, and intelligent data extraction with grid pattern recognition.

## Core Parser Implementation (dex_parser.py)

### Class Structure and Initialization

```python
class DEXParser:
    """DEX file parser with comprehensive error handling and validation"""
    
    def __init__(self):
        """Initialize DEX parser with manufacturer adapters and record processors"""
        
        # Manufacturer-specific processing adapters
        self.manufacturer_adapters = {
            'VA': self._vendo_adapter,      # Vendo machines
            'AMS': self._ams_adapter,       # AMS (Automatic Merchandising Systems)
            'CN': self._crane_adapter,      # Crane National
            'STF': self._crane_adapter      # Crane STF series
        }
        
        # Comprehensive record type processors (40+ types)
        self.record_processors = {
            # Core DEX structure
            'DXS': self._process_dxs,       # DEX Start
            'DXE': self._process_dxe,       # DEX End
            
            # Machine identification
            'ID1': self._process_id1,       # Machine Serial/Model
            'ID4': self._process_id4,       # Device Type/Number  
            'ID5': self._process_id5,       # Date/Time
            
            # Product Activity (PA) records - Core sales data
            'PA1': self._process_pa1,       # Product Setup (selection, price, capacity)
            'PA2': self._process_pa2,       # Product Sales (units, revenue, test/free vends)
            'PA3': self._process_pa3,       # Cash vs Cashless breakdown
            'PA4': self._process_pa4,       # Discount Sales
            'PA5': self._process_pa5,       # Last Sale Date/Time
            'PA7': self._process_pa7,       # Payment Type Details
            'PA8': self._process_pa8,       # Extended Product Data
            
            # Cash Management
            'VA1': self._process_va1,       # Bills in Validator
            'VA2': self._process_va2,       # Total Bills Value
            'VA3': self._process_va3,       # Coins in Tubes
            
            # Cashless Payment Systems (CA1-CA22)
            'CA1': self._process_ca1,       # Card Reader Serial/Model
            'CA2': self._process_ca2,       # Cashless Total
            'CA3': self._process_ca3,       # Cashless Transactions
            'CA4': self._process_ca4,       # Cashless Discount
            'CA6': self._process_ca6,       # Additional CA records...
            'CA7': self._process_ca7,
            'CA8': self._process_ca8,
            'CA9': self._process_ca9,
            'CA10': self._process_ca10,
            'CA15': self._process_ca15,
            'CA17': self._process_ca17,
            'CA22': self._process_ca22,
            
            # Diagnostic Data (DA1-DA10)
            'DA1': self._process_da1,       # Diagnostic Device Info
            'DA2': self._process_da2,       # Total Cash In
            'DA3': self._process_da3,       # Additional diagnostic records...
            'DA4': self._process_da4,
            'DA5': self._process_da5,
            'DA6': self._process_da6,
            'DA10': self._process_da10,
            
            # System Status and Events
            'ST': self._process_st,         # Status Code
            'CB1': self._process_cb1,       # Control Board Info
            'BA1': self._process_ba1,       # Bill Acceptor Info
            
            # Event Logging (EA1-EA7)
            'EA1': self._process_ea1,       # Event Type/Data
            'EA2': self._process_ea2,       # Additional event records...
            'EA3': self._process_ea3,
            'EA4': self._process_ea4,
            'EA5': self._process_ea5,
            'EA6': self._process_ea6,
            'EA7': self._process_ea7,
            
            # Tube and Coin Data
            'TA1': self._process_ta1,       # Tube Data
            'TA2': self._process_ta2,       # Coin Data
            
            # Line Control
            'LS': self._process_ls,         # Line Start
            'LE': self._process_le,         # Line End
            
            # Manufacturer Specific
            'MA5': self._process_ma5,       # Machine Specific Data
            'SD1': self._process_sd1,       # Sales Data
            'G85': self._process_g85,       # Glazer Specific
            'SE': self._process_se          # Sales End
        }
```

### Main Parsing Pipeline

#### File Processing Entry Point
```python
def parse_file(self, content: str, filename: str) -> dict:
    """Parse DEX file content with comprehensive error handling and PA record consolidation"""
    try:
        # Phase 1: Basic content validation
        lines = content.strip().split('\n')
        lines = [line.strip() for line in lines if line.strip()]
        
        if not lines:
            return self._error_response('Empty file or no valid content found')
        
        # Phase 2: DEX structure validation
        structure_result = self._validate_structure(lines)
        if not structure_result['success']:
            return structure_result
        
        # Phase 3: Record-by-record parsing
        parsed_records = []
        pa_records = []
        non_pa_records = []
        machine_info = {}
        
        for line_num, line in enumerate(lines, 1):
            record_result = self._parse_record(line, line_num)
            if not record_result['success']:
                return record_result
            
            record = record_result['record']
            parsed_records.append(record)
            
            # Extract machine info from DXS record
            if record['record_type'] == 'DXS':
                machine_info = record['parsed_data']
            
            # Separate PA and non-PA records for different processing
            if record['record_type'].startswith('PA'):
                pa_records.append(record)
            else:
                non_pa_records.append(record)
        
        # Phase 4: PA record consolidation by selection number
        consolidated_pa, pa_errors = self._consolidate_pa_records(pa_records)
        
        # Phase 5: Grid pattern analysis integration
        grid_result = self._analyze_grid_patterns(consolidated_pa)
        
        # Phase 6: Result compilation with error classification
        return self._compile_results(machine_info, non_pa_records, consolidated_pa, 
                                   grid_result, pa_errors, len(parsed_records))
                                   
    except Exception as e:
        return self._error_response(f'File parsing failed: {str(e)}')
```

#### DEX Structure Validation
```python
def _validate_structure(self, lines: list) -> dict:
    """Validate DEX file structure according to specification"""
    
    # Minimum file size check
    if len(lines) < 2:
        return {
            'success': False,
            'error': {
                'line': 0,
                'message': 'File too short - must contain at least DXS and DXE records',
                'field': 0
            }
        }
    
    # DEX Start (DXS) record validation
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
    
    # DEX End (DXE) record validation
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
```

### Record Processing Implementation

#### Individual Record Parsing
```python
def _parse_record(self, line: str, line_number: int) -> dict:
    """Parse individual DEX record with error handling"""
    try:
        # Split on asterisk delimiter (DEX standard)
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
        
        # Handle record subtypes (PA1, PA2, CA17, etc.)
        if len(record_type) > 2 and record_type[2:].isdigit():
            record_subtype = record_type
            record_type = record_type[:2]
        
        # Process with appropriate specialized handler
        processor = self.record_processors.get(record_subtype or record_type, 
                                             self._process_generic)
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
```

#### Core Record Type Processors

##### DXS (DEX Start) Record Processing
```python
def _process_dxs(self, fields: list, line_number: int) -> dict:
    """Process DXS (DEX Start) record - machine identification"""
    return {
        'machine_serial': fields[1] if len(fields) > 1 else '',
        'manufacturer': fields[2] if len(fields) > 2 else '',
        'version': fields[3] if len(fields) > 3 else '',
        'revision': fields[4] if len(fields) > 4 else '',
        'options': fields[5] if len(fields) > 5 else ''
    }
```

##### PA1 (Product Setup) Record Processing
```python
def _process_pa1(self, fields: list, line_number: int) -> dict:
    """Process PA1 (Product Setup) record"""
    return {
        'selection_number': fields[1] if len(fields) > 1 else '',
        'price_cents': self._parse_int(fields[2]) if len(fields) > 2 and fields[2] else 0,
        'capacity': self._parse_int(fields[3]) if len(fields) > 3 and fields[3] else 0
    }
```

##### PA2 (Product Sales) Record Processing  
```python
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
```

##### PA3 (Cash vs Cashless) Record Processing
```python
def _process_pa3(self, fields: list, line_number: int) -> dict:
    """Process PA3 (Cash vs Cashless) record"""
    return {
        'cash_sales': self._parse_int(fields[1]) if len(fields) > 1 else 0,
        'cash_sales_cents': self._parse_int(fields[2]) if len(fields) > 2 else 0,
        'cashless_sales': self._parse_int(fields[3]) if len(fields) > 3 else 0,
        'cashless_sales_cents': self._parse_int(fields[4]) if len(fields) > 4 else 0
    }
```

### PA Record Consolidation System

#### Selection-Based Record Grouping
```python
def _consolidate_pa_records(self, pa_records: list) -> tuple:
    """Consolidate PA records by selection_number with validation"""
    pa_groups = {}  # {selection_number: {PA1: record, PA2: record, ...}}
    errors = []
    current_selection = None
    
    # Group PA records by selection_number
    for record in pa_records:
        pa_type = record['record_type']
        
        if pa_type == 'PA1':
            # PA1 starts a new selection group and contains selection_number
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
            # PA7 records have their own selection_number
            pa7_selection = record['parsed_data'].get('selection_number', '')
            if pa7_selection:
                if pa7_selection not in pa_groups:
                    pa_groups[pa7_selection] = {}
                
                # PA7 can have multiple entries per selection (different payment types)
                if pa_type not in pa_groups[pa7_selection]:
                    pa_groups[pa7_selection][pa_type] = []
                pa_groups[pa7_selection][pa_type].append(record)
        
        elif current_selection and pa_type.startswith('PA'):
            # PA2, PA3, PA4, PA5, PA8 belong to current selection from last PA1
            if current_selection not in pa_groups:
                pa_groups[current_selection] = {}
            
            # Check for duplicates (except PA7 which can have multiples)
            if pa_type in pa_groups[current_selection] and pa_type != 'PA7':
                error_msg = f"Duplicate selections found: {current_selection}"
                if error_msg not in errors:
                    errors.append(error_msg)
            
            pa_groups[current_selection][pa_type] = record
    
    # Consolidate and validate each group
    consolidated = []
    for selection_number, pa_group in pa_groups.items():
        # PA1 is required for each selection
        if 'PA1' not in pa_group:
            errors.append(f"Selection {selection_number} missing PA1")
            continue
        
        # Merge data from all PA records for this selection
        consolidated_data = self._merge_pa_data(pa_group)
        
        # Validate revenue consistency between PA2 and PA3
        if not self._validate_pa_revenue(pa_group):
            errors.append("PA sales data mismatch")
        
        consolidated.append({
            'selection_number': selection_number,
            'data': consolidated_data,
            'line_number': pa_group['PA1']['line_number']  # Use PA1 line for reference
        })
    
    return consolidated, errors
```

#### PA Data Merging Logic
```python
def _merge_pa_data(self, pa_group: dict) -> dict:
    """Merge data from PA1-PA8 records into single structure"""
    merged = {
        # Initialize all fields for missing data handling
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
    
    # Merge PA1 data (required - selection setup)
    if 'PA1' in pa_group:
        pa1_data = pa_group['PA1']['parsed_data']
        merged.update({
            'selection_number': pa1_data.get('selection_number'),
            'price_cents': pa1_data.get('price_cents'),
            'capacity': pa1_data.get('capacity')
        })
    
    # Merge PA2 data (optional - sales totals)
    if 'PA2' in pa_group:
        pa2_data = pa_group['PA2']['parsed_data']
        merged.update({
            'units_sold': pa2_data.get('units_sold'),
            'revenue_cents': pa2_data.get('revenue_cents'),
            'test_vends': pa2_data.get('test_vends'),
            'free_vends': pa2_data.get('free_vends')
        })
    
    # Merge PA3 data (optional - payment method breakdown)
    if 'PA3' in pa_group:
        pa3_data = pa_group['PA3']['parsed_data']
        merged.update({
            'cash_sales': pa3_data.get('cash_sales'),
            'cash_sales_cents': pa3_data.get('cash_sales_cents'),
            'cashless_sales': pa3_data.get('cashless_sales'),
            'cashless_sales_cents': pa3_data.get('cashless_sales_cents')
        })
    
    # Merge PA4 data (optional - discount sales)
    if 'PA4' in pa_group:
        pa4_data = pa_group['PA4']['parsed_data']
        merged.update({
            'discount_sales': pa4_data.get('discount_sales'),
            'discount_sales_cents': pa4_data.get('discount_sales_cents')
        })
    
    # Merge PA5 data (optional - last sale timestamp)
    if 'PA5' in pa_group:
        pa5_data = pa_group['PA5']['parsed_data']
        merged.update({
            'last_sale_date': pa5_data.get('last_sale_date'),
            'last_sale_time': pa5_data.get('last_sale_time')
        })
    
    return merged
```

### Grid Pattern Analysis Integration

#### Grid Analysis Pipeline
```python
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
        
        # Extract selection numbers for pattern analysis
        selection_numbers = [
            record['selection_number'] 
            for record in consolidated_pa 
            if record.get('selection_number')
        ]
        
        if not selection_numbers:
            return {
                'pattern_type': 'unknown',
                'confidence': 0.0,
                'grid_dimensions': {'rows': 0, 'columns': 0},
                'errors': ['No valid selection numbers found']
            }
        
        # Perform grid pattern analysis
        analyzer = GridPatternAnalyzer()
        grid_result = analyzer.analyze_selections(selection_numbers)
        
        # Add row/column assignments to consolidated records
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
```

## Grid Pattern Analyzer Implementation (grid_pattern_analyzer.py)

### Pattern Detection Architecture

#### GridPatternAnalyzer Class Structure
```python
class GridPatternAnalyzer:
    """Analyzes selection numbers to detect vending machine grid patterns"""
    
    def __init__(self):
        """Initialize with pattern detection algorithms"""
        self.pattern_detectors = [
            self._detect_alphanumeric_pattern,        # A1, A2, B1, B2
            self._detect_numeric_tens_pattern,        # 10, 12, 14 → 20, 22, 24
            self._detect_sequential_blocks_pattern,   # 1-10 → 11-20 → 21-30
            self._detect_zero_padded_numeric_pattern, # 01, 02 → 11, 12
            self._detect_custom_numeric_pattern       # 101, 102 → 201, 202
        ]
```

#### Main Analysis Entry Point
```python
def analyze_selections(self, selections: List[str]) -> Dict:
    """
    Main entry point for pattern analysis
    
    Returns:
        {
            'assignments': {selection_number: {row, column}},
            'pattern_type': str,
            'confidence': float,
            'grid_dimensions': {rows, columns},
            'errors': [str]
        }
    """
    if not selections:
        return self._empty_result("No selections provided")
    
    # Clean and validate input
    clean_selections = [str(s).strip() for s in selections if s and str(s).strip()]
    if not clean_selections:
        return self._empty_result("No valid selections found")
    
    # Try each pattern detector and find best match
    best_result = None
    best_confidence = 0.0
    
    for detector in self.pattern_detectors:
        try:
            result = detector(clean_selections)
            if result['confidence'] > best_confidence:
                best_confidence = result['confidence']
                best_result = result
        except Exception as e:
            continue  # Try next detector
    
    # Return best result if confidence meets threshold
    if best_result and best_confidence >= 0.5:
        return best_result
    else:
        return self._empty_result("No clear pattern detected")
```

### Pattern Detection Algorithms

#### 1. Alphanumeric Grid Pattern Detection
```python
def _detect_alphanumeric_pattern(self, selections: List[str]) -> Dict:
    """
    Detect alphanumeric patterns: Letter prefix (row) + number suffix (column)
    Examples: A1, A2, B1, B2, C1, C2
    """
    pattern_type = "alphanumeric_grid"
    assignments = {}
    errors = []
    
    # Regex for letter+number pattern
    alpha_num_regex = re.compile(r'^([A-Za-z]+)(\d+)$')
    
    valid_selections = []
    for selection in selections:
        match = alpha_num_regex.match(selection)
        if match:
            letter_part = match.group(1).upper()
            number_part = int(match.group(2))
            valid_selections.append((selection, letter_part, number_part))
    
    # Require 80% match rate for pattern validity
    if len(valid_selections) < len(selections) * 0.8:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['Less than 80% match alphanumeric pattern']}
    
    # Group by row (letter part)
    rows = defaultdict(list)
    for selection, letter_part, number_part in valid_selections:
        rows[letter_part].append((selection, number_part))
    
    # Sort rows alphabetically and columns numerically
    sorted_rows = sorted(rows.keys())
    
    # Assign row/column coordinates
    for row_index, row_letter in enumerate(sorted_rows):
        columns_in_row = sorted(rows[row_letter], key=lambda x: x[1])
        for col_index, (selection, number_part) in enumerate(columns_in_row):
            assignments[selection] = {
                'row': row_letter,
                'column': str(number_part)
            }
    
    # Calculate grid dimensions and confidence
    max_columns = max(len(rows[row]) for row in rows) if rows else 0
    confidence = self._calculate_alphanumeric_confidence(rows, valid_selections, selections)
    
    return {
        'assignments': assignments,
        'pattern_type': pattern_type,
        'confidence': confidence,
        'grid_dimensions': {'rows': len(sorted_rows), 'columns': max_columns},
        'errors': errors
    }
```

#### 2. Numeric Tens Pattern Detection
```python
def _detect_numeric_tens_pattern(self, selections: List[str]) -> Dict:
    """
    Detect numeric tens patterns: 10, 12, 14 → 20, 22, 24
    Tens digit = row, units digit/increment = column
    """
    pattern_type = "numeric_tens"
    assignments = {}
    
    # Convert to integers and validate
    try:
        numeric_selections = [(sel, int(sel)) for sel in selections if sel.isdigit()]
    except ValueError:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['Non-numeric selections found']}
    
    if len(numeric_selections) < len(selections) * 0.9:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['Less than 90% numeric selections']}
    
    # Group by tens digit
    tens_groups = defaultdict(list)
    for selection, number in numeric_selections:
        tens_digit = number // 10
        tens_groups[tens_digit].append((selection, number))
    
    # Detect consistent increment pattern within tens groups
    increment = self._detect_increment_pattern(tens_groups)
    if not increment:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['No consistent increment pattern found']}
    
    # Assign coordinates based on tens grouping and increment
    for tens_digit, group in tens_groups.items():
        sorted_group = sorted(group, key=lambda x: x[1])
        for col_index, (selection, number) in enumerate(sorted_group):
            column_value = (number % 10) // (increment // 10) if increment >= 10 else (number % 10)
            assignments[selection] = {
                'row': str(tens_digit),
                'column': str(column_value)
            }
    
    # Calculate confidence based on pattern regularity
    confidence = min(1.0, len(assignments) / len(selections) * 0.9)
    if increment and len(tens_groups) > 1:
        confidence = min(1.0, confidence + 0.2)  # Bonus for multi-row pattern
    
    return {
        'assignments': assignments,
        'pattern_type': pattern_type,
        'confidence': confidence,
        'grid_dimensions': {'rows': len(tens_groups), 
                          'columns': max(len(group) for group in tens_groups.values())},
        'errors': []
    }
```

#### 3. Sequential Blocks Pattern Detection  
```python
def _detect_sequential_blocks_pattern(self, selections: List[str]) -> Dict:
    """
    Detect sequential block patterns: 1-10 → 11-20 → 21-30
    Numbers grouped in sequential blocks of consistent size
    """
    pattern_type = "sequential_blocks"
    assignments = {}
    
    # Convert to integers
    try:
        numeric_selections = [(sel, int(sel)) for sel in selections if sel.isdigit()]
    except ValueError:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['Non-numeric selections found']}
    
    if len(numeric_selections) < len(selections) * 0.9:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['Less than 90% numeric selections']}
    
    # Test different block sizes to find best fit
    numbers = [num for _, num in sorted(numeric_selections, key=lambda x: x[1])]
    best_block_size = None
    best_confidence = 0.0
    
    for block_size in [5, 6, 8, 9, 10, 12, 15, 16, 20]:
        confidence = self._test_block_size(numbers, block_size)
        if confidence > best_confidence:
            best_confidence = confidence
            best_block_size = block_size
    
    if best_block_size is None or best_confidence < 0.5:
        return {'confidence': 0.0, 'pattern_type': pattern_type, 
                'assignments': {}, 'errors': ['No clear block pattern detected']}
    
    # Assign coordinates based on block size
    for selection, number in numeric_selections:
        adjusted_number = number - 1 if min(numbers) == 1 else number
        row = adjusted_number // best_block_size
        column = adjusted_number % best_block_size
        
        assignments[selection] = {
            'row': str(row),
            'column': str(column)
        }
    
    max_row = max(int(assignments[sel]['row']) for sel in assignments) if assignments else 0
    
    return {
        'assignments': assignments,
        'pattern_type': pattern_type,
        'confidence': best_confidence,
        'grid_dimensions': {'rows': max_row + 1, 'columns': best_block_size},
        'errors': []
    }
```

### Manufacturer-Specific Adapters

#### Vendo Adapter Implementation
```python
def _vendo_adapter(self, fields: list) -> dict:
    """Vendo-specific field processing and interpretation"""
    # Vendo machines often have specific field arrangements
    # Handle Vendo-specific quirks like different field orders or special values
    return {
        'fields': fields,
        'manufacturer_specific': {
            'vendo_version': fields[1] if len(fields) > 1 else None,
            'model_info': fields[2] if len(fields) > 2 else None
        }
    }
```

#### AMS Adapter Implementation  
```python
def _ams_adapter(self, fields: list) -> dict:
    """AMS-specific field processing for Sensit and VCF series"""
    # AMS machines may have different PA record interpretations
    # Handle AMS-specific inventory tracking features
    return {
        'fields': fields,
        'manufacturer_specific': {
            'ams_inventory_mode': self._detect_ams_inventory_mode(fields),
            'vcf_specific_data': self._process_vcf_data(fields)
        }
    }
```

### Data Validation and Quality Assurance

#### Revenue Consistency Validation
```python
def _validate_pa_revenue(self, pa_group: dict) -> bool:
    """Validate revenue consistency between PA2 (total) and PA3 (breakdown)"""
    if 'PA2' not in pa_group or 'PA3' not in pa_group:
        return True  # Cannot validate without both records
    
    pa2_revenue = pa_group['PA2']['parsed_data'].get('revenue_cents', 0) or 0
    pa3_cash = pa_group['PA3']['parsed_data'].get('cash_sales_cents', 0) or 0
    pa3_cashless = pa_group['PA3']['parsed_data'].get('cashless_sales_cents', 0) or 0
    pa3_total = pa3_cash + pa3_cashless
    
    # Allow small discrepancies due to rounding
    return abs(pa2_revenue - pa3_total) <= 1
```

#### Safe Integer Parsing
```python
def _parse_int(self, value: str) -> int:
    """Safely parse integer from string with error handling"""
    try:
        return int(value) if value and value.strip() else 0
    except ValueError:
        return 0  # Return 0 for invalid values rather than crashing
```

### Error Handling and Recovery

#### Error Message Formatting
```python
def _format_error_messages(self, errors: list) -> str:
    """Format error messages for database storage and user display"""
    if not errors:
        return None
    
    # Group similar errors for cleaner reporting
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
        selections = list(set(error_groups["duplicates"]))
        messages.append(f"Duplicate selections found: {', '.join(selections)}")
    if "revenue_mismatch" in error_groups:
        messages.append("PA sales data mismatch")
    if "missing_pa1" in error_groups:
        selections = list(set(error_groups["missing_pa1"]))
        messages.append(f"Missing PA1 for selections: {', '.join(selections)}")
    
    return "; ".join(messages)
```

This technical implementation provides a robust, extensible foundation for processing diverse DEX file formats while maintaining data quality and providing intelligent grid pattern recognition for improved data analysis and visualization.