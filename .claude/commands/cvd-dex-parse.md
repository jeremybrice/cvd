---
name: cvd-dex-parse
description: Parse and analyze DEX files from vending machines, extract sales data, detect grid patterns, and import into database
---

# CVD DEX Parser Command

Execute DEX file parsing and analysis for vending machine data import.

## Command Variations

### Parse DEX File
When asked to "parse dex file [filename]":
1. Validate DEX format and version
2. Extract all supported record types
3. Detect grid pattern (spiral, column, etc.)
4. Map products to positions
5. Import to database

### Analyze Grid Pattern
When asked to "analyze grid pattern from [dex_file]":
1. Extract PA1/PA2 records
2. Apply pattern detection algorithm
3. Visualize detected pattern
4. Validate against known configurations
5. Report confidence score

### Import Sales Data
When asked to "import sales from [dex_file]":
1. Parse VA1/VA2/VA3 records
2. Match products to database
3. Calculate transaction metrics
4. Update device statistics
5. Flag anomalies

## DEX Record Types

### Critical Records
- **DXS/DXE**: Start/End markers
- **ST/SE**: Transaction boundaries
- **PA1/PA2**: Product mapping (grid pattern)
- **VA1/VA2/VA3**: Vend activity (sales data)
- **CA1/CA2/CA3**: Cash accounting
- **DA1/DA2**: Discount activity

### Implementation Logic

```python
# Grid Pattern Detection
def detect_grid_pattern(pa_records):
    patterns = {
        'spiral': check_spiral_sequence,
        'column': check_column_sequence,
        'serpentine': check_serpentine_sequence,
        'horizontal': check_horizontal_sequence,
        'custom': analyze_custom_pattern
    }
    
    for pattern_name, checker in patterns.items():
        confidence = checker(pa_records)
        if confidence > 0.8:
            return pattern_name, confidence
```

### Data Validation
```python
# Validate DEX integrity
checks = {
    'header_valid': validate_dxs_record,
    'trailer_valid': validate_dxe_record,
    'checksum_match': verify_g85_checksum,
    'date_sequence': check_chronological_order,
    'product_mapping': validate_pa_records
}
```

## Multi-Manufacturer Support

### Crane/National
- Uses PA1 for product mapping
- Spiral grid pattern common
- CA15 for cashless transactions

### AMS/Sensit
- Extended PA2 records
- Column-based grids
- Enhanced error codes

### USI/Wittern
- Custom grid sequences
- Additional telemetry data
- Temperature monitoring

## Files to Reference
- `/home/jbrice/Projects/365/dex_parser.py`
- `/home/jbrice/Projects/365/grid_pattern_analyzer.py`
- `/home/jbrice/Projects/365/pages/dex-parser.html`
- `/home/jbrice/Projects/365/docs/examples/dex files/`

## Error Handling
- Invalid format → Return parsing report
- Unknown records → Log and continue
- Grid mismatch → Flag for manual review
- Duplicate data → Check timestamps

## Success Metrics
- Parse success rate > 99%
- Grid detection accuracy > 95%
- Import time < 2 seconds per file
- Zero data loss