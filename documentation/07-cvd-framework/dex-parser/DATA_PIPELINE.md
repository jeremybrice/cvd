# DEX Parser Data Pipeline


## Metadata
- **ID**: 07_CVD_FRAMEWORK_DEX_PARSER_DATA_PIPELINE
- **Type**: Documentation
- **Version**: 1.0.0
- **Last Updated**: 2025-08-12
- **Tags**: #ai #analytics #api #cvd-specific #data-exchange #data-layer #database #debugging #device-management #dex-parser #domain #integration #logistics #machine-learning #metrics #optimization #performance #planogram #product-placement #quality-assurance #reporting #route-management #testing #troubleshooting #vending #vending-machine
- **Intent**: The CVD DEX Parser data pipeline transforms raw vending machine audit files into structured, analyzable business data through a multi-stage processing system
- **Audience**: managers, architects
- **Prerequisites**: See context bridges for dependencies
- **Next Steps**: See context bridges for navigation

## Navigation
- **Parent**: /documentation/07-cvd-framework/dex-parser/
- **Category**: Dex Parser
- **Search Keywords**: ####, cabinet, content, cooler, data, device, dex, parser, pipeline, planogram, preprocessing, route, vending

## Pipeline Overview

The CVD DEX Parser data pipeline transforms raw vending machine audit files into structured, analyzable business data through a multi-stage processing system. The pipeline emphasizes data quality, error recovery, and intelligent pattern recognition to maximize the value extracted from machine-generated audit data.

## Data Flow Architecture

### Stage 1: Input Processing and Validation

#### File Upload and Initial Processing
```python
# API endpoint for DEX file upload
@app.route('/api/dex/parse', methods=['POST'])
@require_auth
def parse_dex_file():
    """Process uploaded DEX file through complete pipeline"""
    
    # Stage 1A: File validation and extraction
    if 'file' not in request.files:
        return jsonify({'error': 'No file uploaded'}), 400
    
    file = request.files['file']
    if not file.filename.lower().endswith(('.txt', '.dex')):
        return jsonify({'error': 'Invalid file type'}), 400
    
    # Stage 1B: Content extraction and encoding handling
    try:
        content = file.read().decode('utf-8', errors='replace')
    except UnicodeDecodeError:
        # Fallback to common encodings used by vending machines
        encodings_to_try = ['latin1', 'cp1252', 'ascii']
        for encoding in encodings_to_try:
            try:
                file.seek(0)
                content = file.read().decode(encoding)
                break
            except UnicodeDecodeError:
                continue
        else:
            return jsonify({'error': 'Unable to decode file'}), 400
    
    # Stage 1C: Basic content validation
    if not content.strip():
        return jsonify({'error': 'Empty file'}), 400
    
    filename = secure_filename(file.filename)
    
    # Stage 1D: Pipeline initiation
    try:
        pipeline_result = process_dex_pipeline(content, filename)
        return jsonify(pipeline_result)
    except Exception as e:
        return jsonify({'error': f'Pipeline processing failed: {str(e)}'}), 500
```

#### Content Preprocessing
```python
def preprocess_dex_content(content: str) -> tuple[list[str], dict]:
    """Preprocess DEX content for parsing pipeline"""
    
    preprocessing_stats = {
        'original_lines': 0,
        'cleaned_lines': 0,
        'empty_lines_removed': 0,
        'whitespace_normalized': 0,
        'encoding_issues_fixed': 0
    }
    
    # Split into lines and count original
    lines = content.split('\n')
    preprocessing_stats['original_lines'] = len(lines)
    
    # Clean and normalize lines
    cleaned_lines = []
    for line in lines:
        # Remove whitespace and normalize
        cleaned_line = line.strip()
        if not cleaned_line:
            preprocessing_stats['empty_lines_removed'] += 1
            continue
        
        # Normalize whitespace within line
        if cleaned_line != line.strip():
            preprocessing_stats['whitespace_normalized'] += 1
        
        # Fix common encoding issues
        fixed_line = fix_encoding_issues(cleaned_line)
        if fixed_line != cleaned_line:
            preprocessing_stats['encoding_issues_fixed'] += 1
        
        cleaned_lines.append(fixed_line)
    
    preprocessing_stats['cleaned_lines'] = len(cleaned_lines)
    
    return cleaned_lines, preprocessing_stats
```

### Stage 2: DEX Parsing and Record Extraction

#### Core Parsing Pipeline
```python
def process_dex_pipeline(content: str, filename: str) -> dict:
    """Main DEX processing pipeline orchestrator"""
    
    pipeline_start = datetime.now()
    pipeline_result = {
        'filename': filename,
        'processing_started': pipeline_start.isoformat(),
        'stages_completed': [],
        'total_processing_time_ms': 0,
        'success': False
    }
    
    try:
        # Stage 2A: Content preprocessing
        stage_start = datetime.now()
        cleaned_lines, preprocessing_stats = preprocess_dex_content(content)
        pipeline_result['preprocessing_stats'] = preprocessing_stats
        pipeline_result['stages_completed'].append({
            'stage': 'preprocessing',
            'duration_ms': (datetime.now() - stage_start).total_seconds() * 1000,
            'status': 'completed'
        })
        
        # Stage 2B: DEX parsing
        stage_start = datetime.now()
        parser = DEXParser()
        parse_result = parser.parse_file('\n'.join(cleaned_lines), filename)
        pipeline_result['stages_completed'].append({
            'stage': 'dex_parsing', 
            'duration_ms': (datetime.now() - stage_start).total_seconds() * 1000,
            'status': 'completed' if parse_result['success'] else 'failed'
        })
        
        if not parse_result['success']:
            pipeline_result['error'] = parse_result['error']
            return pipeline_result
        
        # Stage 2C: Data validation and quality assessment
        stage_start = datetime.now()
        validation_result = validate_parsed_data(parse_result)
        pipeline_result['validation_result'] = validation_result
        pipeline_result['stages_completed'].append({
            'stage': 'data_validation',
            'duration_ms': (datetime.now() - stage_start).total_seconds() * 1000,
            'status': 'completed'
        })
        
        # Stage 2D: Database persistence
        stage_start = datetime.now()
        persistence_result = persist_dex_data(parse_result, filename)
        pipeline_result['persistence_result'] = persistence_result
        pipeline_result['stages_completed'].append({
            'stage': 'database_persistence',
            'duration_ms': (datetime.now() - stage_start).total_seconds() * 1000,
            'status': 'completed' if persistence_result['success'] else 'failed'
        })
        
        # Stage 2E: Post-processing and analytics
        stage_start = datetime.now()
        analytics_result = generate_dex_analytics(parse_result, persistence_result)
        pipeline_result['analytics'] = analytics_result
        pipeline_result['stages_completed'].append({
            'stage': 'analytics_generation',
            'duration_ms': (datetime.now() - stage_start).total_seconds() * 1000,
            'status': 'completed'
        })
        
        # Pipeline completion
        pipeline_end = datetime.now()
        pipeline_result['processing_completed'] = pipeline_end.isoformat()
        pipeline_result['total_processing_time_ms'] = (pipeline_end - pipeline_start).total_seconds() * 1000
        pipeline_result['success'] = True
        
        return pipeline_result
        
    except Exception as e:
        pipeline_result['error'] = str(e)
        pipeline_result['processing_completed'] = datetime.now().isoformat()
        pipeline_result['total_processing_time_ms'] = (datetime.now() - pipeline_start).total_seconds() * 1000
        return pipeline_result
```

### Stage 3: Data Validation and Quality Assessment

#### Comprehensive Data Validation
```python
def validate_parsed_data(parse_result: dict) -> dict:
    """Comprehensive validation of parsed DEX data"""
    
    validation_result = {
        'overall_quality_score': 0.0,
        'validation_checks': [],
        'data_completeness': {},
        'data_consistency': {},
        'recommendations': []
    }
    
    # Check 1: Basic structure validation
    structure_check = validate_dex_structure(parse_result)
    validation_result['validation_checks'].append(structure_check)
    
    # Check 2: PA record completeness and consistency
    pa_completeness = validate_pa_record_completeness(parse_result.get('pa_records', []))
    validation_result['validation_checks'].append(pa_completeness)
    
    # Check 3: Revenue consistency validation
    revenue_consistency = validate_revenue_consistency(parse_result.get('pa_records', []))
    validation_result['validation_checks'].append(revenue_consistency)
    
    # Check 4: Grid pattern validation
    grid_validation = validate_grid_patterns(parse_result.get('grid_analysis', {}))
    validation_result['validation_checks'].append(grid_validation)
    
    # Check 5: Data range validation (detect outliers and anomalies)
    range_validation = validate_data_ranges(parse_result.get('pa_records', []))
    validation_result['validation_checks'].append(range_validation)
    
    # Calculate overall quality score
    validation_result['overall_quality_score'] = calculate_quality_score(validation_result['validation_checks'])
    
    # Generate recommendations based on validation results
    validation_result['recommendations'] = generate_data_quality_recommendations(validation_result)
    
    return validation_result


def validate_pa_record_completeness(pa_records: list) -> dict:
    """Validate completeness of PA record data"""
    
    completeness_check = {
        'check_name': 'PA Record Completeness',
        'status': 'passed',
        'score': 1.0,
        'details': {},
        'issues': []
    }
    
    if not pa_records:
        completeness_check.update({
            'status': 'failed',
            'score': 0.0,
            'issues': ['No PA records found in DEX file']
        })
        return completeness_check
    
    # Analyze record completeness
    total_records = len(pa_records)
    records_with_sales_data = 0
    records_with_pricing = 0
    records_with_timestamps = 0
    records_with_payment_breakdown = 0
    
    for record in pa_records:
        data = record.get('data', {})
        
        # Check for sales data
        if data.get('units_sold') is not None and data.get('revenue_cents') is not None:
            records_with_sales_data += 1
        
        # Check for pricing data
        if data.get('price_cents') is not None and data.get('price_cents') > 0:
            records_with_pricing += 1
        
        # Check for timestamp data
        if data.get('last_sale_date') is not None:
            records_with_timestamps += 1
        
        # Check for payment method breakdown
        if (data.get('cash_sales_cents') is not None or 
            data.get('cashless_sales_cents') is not None):
            records_with_payment_breakdown += 1
    
    # Calculate completeness percentages
    completeness_check['details'] = {
        'total_records': total_records,
        'sales_data_completeness': records_with_sales_data / total_records,
        'pricing_completeness': records_with_pricing / total_records,
        'timestamp_completeness': records_with_timestamps / total_records,
        'payment_breakdown_completeness': records_with_payment_breakdown / total_records
    }
    
    # Calculate overall completeness score
    avg_completeness = (
        completeness_check['details']['sales_data_completeness'] +
        completeness_check['details']['pricing_completeness'] +
        completeness_check['details']['timestamp_completeness'] +
        completeness_check['details']['payment_breakdown_completeness']
    ) / 4
    
    completeness_check['score'] = avg_completeness
    
    # Generate issues and recommendations
    if avg_completeness < 0.8:
        completeness_check['status'] = 'warning'
        completeness_check['issues'].append(f'Data completeness below 80% ({avg_completeness:.1%})')
    
    if completeness_check['details']['sales_data_completeness'] < 0.5:
        completeness_check['issues'].append('Less than 50% of records have sales data')
    
    return completeness_check
```

### Stage 4: Database Persistence and Storage

#### Structured Data Persistence
```python
def persist_dex_data(parse_result: dict, filename: str) -> dict:
    """Persist parsed DEX data to database with transaction safety"""
    
    persistence_result = {
        'success': False,
        'records_inserted': 0,
        'pa_records_inserted': 0,
        'dex_read_id': None,
        'errors': []
    }
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        db.execute('BEGIN TRANSACTION')
        
        # Stage 4A: Create DEX read record
        machine_info = parse_result.get('machine_info', {})
        
        cursor.execute('''
            INSERT INTO dex_reads 
            (filename, machine_serial, manufacturer, parsed_at, 
             total_records, pa_records_count, grid_pattern_type, 
             grid_confidence, parsing_errors, success)
            VALUES (?, ?, ?, CURRENT_TIMESTAMP, ?, ?, ?, ?, ?, ?)
        ''', (
            filename,
            machine_info.get('machine_serial', ''),
            machine_info.get('manufacturer', ''),
            parse_result.get('total_records', 0),
            len(parse_result.get('pa_records', [])),
            parse_result.get('grid_analysis', {}).get('pattern_type', 'unknown'),
            parse_result.get('grid_analysis', {}).get('confidence', 0.0),
            parse_result.get('error_message'),
            parse_result.get('success', False)
        ))
        
        dex_read_id = cursor.lastrowid
        persistence_result['dex_read_id'] = dex_read_id
        
        # Stage 4B: Insert PA records with grid assignments
        pa_records = parse_result.get('pa_records', [])
        for pa_record in pa_records:
            data = pa_record.get('data', {})
            
            cursor.execute('''
                INSERT INTO dex_pa_records
                (dex_read_id, selection_number, row_assignment, column_assignment,
                 price_cents, capacity, units_sold, revenue_cents,
                 cash_sales_cents, cashless_sales_cents, 
                 test_vends, free_vends, discount_sales_cents,
                 last_sale_date, last_sale_time)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                dex_read_id,
                data.get('selection_number'),
                data.get('row'),
                data.get('column'), 
                data.get('price_cents'),
                data.get('capacity'),
                data.get('units_sold'),
                data.get('revenue_cents'),
                data.get('cash_sales_cents'),
                data.get('cashless_sales_cents'),
                data.get('test_vends'),
                data.get('free_vends'),
                data.get('discount_sales_cents'),
                data.get('last_sale_date'),
                data.get('last_sale_time')
            ))
            
            persistence_result['pa_records_inserted'] += 1
        
        # Stage 4C: Insert non-PA records for complete audit trail
        other_records = parse_result.get('parsed_records', [])
        for record in other_records:
            cursor.execute('''
                INSERT INTO dex_other_records
                (dex_read_id, record_type, line_number, raw_record, parsed_data)
                VALUES (?, ?, ?, ?, ?)
            ''', (
                dex_read_id,
                record.get('record_type'),
                record.get('line_number'),
                record.get('raw_record'),
                json.dumps(record.get('parsed_data', {}))
            ))
            
            persistence_result['records_inserted'] += 1
        
        # Stage 4D: Update device linkage if possible
        if machine_info.get('machine_serial'):
            update_device_dex_linkage(cursor, dex_read_id, machine_info.get('machine_serial'))
        
        db.execute('COMMIT')
        persistence_result['success'] = True
        
    except Exception as e:
        db.execute('ROLLBACK')
        persistence_result['errors'].append(f'Database persistence failed: {str(e)}')
        raise e
    
    return persistence_result


def update_device_dex_linkage(cursor, dex_read_id: int, machine_serial: str):
    """Link DEX data to existing device records when possible"""
    
    # Try to find matching device by serial number
    cursor.execute('''
        SELECT id FROM devices 
        WHERE asset = ? OR cooler = ? OR LOWER(asset) = LOWER(?)
    ''', (machine_serial, machine_serial, machine_serial))
    
    device_match = cursor.fetchone()
    
    if device_match:
        # Update DEX read with device linkage
        cursor.execute('''
            UPDATE dex_reads 
            SET device_id = ? 
            WHERE id = ?
        ''', (device_match['id'], dex_read_id))
        
        # Update device last_dex_read timestamp
        cursor.execute('''
            UPDATE devices 
            SET last_dex_read = CURRENT_TIMESTAMP 
            WHERE id = ?
        ''', (device_match['id'],))
```

### Stage 5: Analytics Generation and Business Intelligence

#### Post-Processing Analytics Pipeline
```python
def generate_dex_analytics(parse_result: dict, persistence_result: dict) -> dict:
    """Generate analytics and business intelligence from parsed DEX data"""
    
    analytics = {
        'summary_metrics': {},
        'product_performance': {},
        'revenue_analysis': {},
        'grid_insights': {},
        'operational_metrics': {},
        'recommendations': []
    }
    
    pa_records = parse_result.get('pa_records', [])
    
    if not pa_records:
        analytics['summary_metrics'] = {'total_selections': 0}
        return analytics
    
    # Stage 5A: Summary metrics calculation
    analytics['summary_metrics'] = calculate_summary_metrics(pa_records)
    
    # Stage 5B: Product performance analysis
    analytics['product_performance'] = analyze_product_performance(pa_records)
    
    # Stage 5C: Revenue analysis
    analytics['revenue_analysis'] = analyze_revenue_patterns(pa_records)
    
    # Stage 5D: Grid pattern insights
    if parse_result.get('grid_analysis'):
        analytics['grid_insights'] = analyze_grid_effectiveness(pa_records, parse_result['grid_analysis'])
    
    # Stage 5E: Operational metrics
    analytics['operational_metrics'] = calculate_operational_metrics(pa_records)
    
    # Stage 5F: Generate business recommendations
    analytics['recommendations'] = generate_business_recommendations(analytics)
    
    return analytics


def calculate_summary_metrics(pa_records: list) -> dict:
    """Calculate high-level summary metrics from PA records"""
    
    total_selections = len(pa_records)
    active_selections = 0
    total_revenue = 0
    total_units_sold = 0
    selections_with_sales = 0
    
    for record in pa_records:
        data = record.get('data', {})
        
        revenue = data.get('revenue_cents', 0) or 0
        units = data.get('units_sold', 0) or 0
        
        total_revenue += revenue
        total_units_sold += units
        
        if units > 0:
            active_selections += 1
            selections_with_sales += 1
    
    avg_revenue_per_selection = total_revenue / max(active_selections, 1)
    avg_units_per_selection = total_units_sold / max(active_selections, 1)
    selection_activity_rate = selections_with_sales / total_selections if total_selections > 0 else 0
    
    return {
        'total_selections': total_selections,
        'active_selections': active_selections,
        'total_revenue_cents': total_revenue,
        'total_units_sold': total_units_sold,
        'avg_revenue_per_active_selection': avg_revenue_per_selection,
        'avg_units_per_active_selection': avg_units_per_selection,
        'selection_activity_rate': selection_activity_rate,
        'total_revenue_dollars': total_revenue / 100.0
    }


def analyze_product_performance(pa_records: list) -> dict:
    """Analyze individual product performance metrics"""
    
    performance_data = []
    
    for record in pa_records:
        data = record.get('data', {})
        selection = data.get('selection_number', 'Unknown')
        
        revenue_cents = data.get('revenue_cents', 0) or 0
        units_sold = data.get('units_sold', 0) or 0
        price_cents = data.get('price_cents', 0) or 0
        capacity = data.get('capacity', 0) or 0
        
        # Calculate performance metrics
        revenue_per_unit = revenue_cents / max(units_sold, 1)
        capacity_utilization = units_sold / max(capacity, 1)
        
        performance_record = {
            'selection_number': selection,
            'units_sold': units_sold,
            'revenue_cents': revenue_cents,
            'revenue_dollars': revenue_cents / 100.0,
            'price_cents': price_cents,
            'capacity': capacity,
            'revenue_per_unit': revenue_per_unit,
            'capacity_utilization': capacity_utilization,
            'row': data.get('row'),
            'column': data.get('column')
        }
        
        performance_data.append(performance_record)
    
    # Sort by revenue performance
    performance_data.sort(key=lambda x: x['revenue_cents'], reverse=True)
    
    # Identify top and bottom performers
    top_performers = performance_data[:5]
    bottom_performers = [p for p in performance_data if p['units_sold'] == 0]
    
    return {
        'all_selections': performance_data,
        'top_performers': top_performers,
        'zero_sales_selections': bottom_performers,
        'total_analyzed': len(performance_data)
    }
```

### Stage 6: Integration with Business Systems

#### Sales Data Integration
```python
def integrate_dex_with_sales_system(dex_read_id: int, pa_records: list):
    """Integrate DEX data with main sales tracking system"""
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Find linked device for this DEX read
        cursor.execute('''
            SELECT device_id FROM dex_reads WHERE id = ?
        ''', (dex_read_id,))
        
        dex_read = cursor.fetchone()
        if not dex_read or not dex_read['device_id']:
            return  # Cannot integrate without device linkage
        
        device_id = dex_read['device_id']
        
        # Create sales records from PA data
        for record in pa_records:
            data = record.get('data', {})
            
            units_sold = data.get('units_sold', 0) or 0
            revenue_cents = data.get('revenue_cents', 0) or 0
            selection_number = data.get('selection_number')
            
            if units_sold > 0 and selection_number:
                # Create sales entry
                cursor.execute('''
                    INSERT INTO sales 
                    (device_id, selection_number, sale_units, sale_cash, 
                     dex_read_id, created_at)
                    VALUES (?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
                ''', (device_id, selection_number, units_sold, revenue_cents, dex_read_id))
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
```

#### Inventory System Integration
```python
def update_inventory_from_dex(dex_read_id: int, pa_records: list):
    """Update planogram quantities based on DEX sales data"""
    
    db = get_db()
    cursor = db.cursor()
    
    try:
        # Get device ID from DEX read
        cursor.execute('''
            SELECT device_id FROM dex_reads WHERE id = ?
        ''', (dex_read_id,))
        
        dex_read = cursor.fetchone()
        if not dex_read or not dex_read['device_id']:
            return
        
        device_id = dex_read['device_id']
        
        # Update planogram slot quantities based on sales
        for record in pa_records:
            data = record.get('data', {})
            selection_number = data.get('selection_number')
            units_sold = data.get('units_sold', 0) or 0
            
            if selection_number and units_sold > 0:
                # Map selection number to slot position
                row = data.get('row')
                column = data.get('column')
                
                if row and column:
                    slot_position = f"{row}{column}"
                    
                    # Update planogram slot quantity
                    cursor.execute('''
                        UPDATE planogram_slots 
                        SET quantity = MAX(0, quantity - ?)
                        WHERE planogram_id IN (
                            SELECT p.id FROM planograms p
                            JOIN cabinet_configurations cc ON p.cabinet_id = cc.id
                            WHERE cc.device_id = ?
                        ) AND slot_position = ?
                    ''', (units_sold, device_id, slot_position))
        
        db.commit()
        
    except Exception as e:
        db.rollback()
        raise e
```

## Error Handling and Recovery Mechanisms

### Pipeline Error Classification
```python
class DEXPipelineError(Exception):
    """Base exception for DEX pipeline errors"""
    pass

class DEXValidationError(DEXPipelineError):
    """Error during data validation stage"""
    pass

class DEXPersistenceError(DEXPipelineError):
    """Error during database persistence stage"""
    pass

class DEXAnalyticsError(DEXPipelineError):
    """Error during analytics generation stage"""
    pass


def handle_pipeline_error(error: Exception, stage: str, context: dict) -> dict:
    """Centralized pipeline error handling"""
    
    error_response = {
        'error_type': type(error).__name__,
        'error_message': str(error),
        'failed_stage': stage,
        'context': context,
        'recovery_attempted': False,
        'recovery_successful': False
    }
    
    # Attempt recovery based on error type and stage
    if isinstance(error, DEXValidationError):
        error_response.update(attempt_validation_recovery(error, context))
    elif isinstance(error, DEXPersistenceError):
        error_response.update(attempt_persistence_recovery(error, context))
    elif isinstance(error, DEXAnalyticsError):
        # Analytics errors are non-critical, continue without analytics
        error_response['recovery_attempted'] = True
        error_response['recovery_successful'] = True
        
    return error_response
```

### Data Quality Monitoring
```python
def monitor_pipeline_quality(pipeline_results: list) -> dict:
    """Monitor pipeline processing quality over time"""
    
    quality_metrics = {
        'total_files_processed': len(pipeline_results),
        'successful_processing_rate': 0.0,
        'average_processing_time_ms': 0.0,
        'common_error_patterns': {},
        'data_quality_trends': {}
    }
    
    if not pipeline_results:
        return quality_metrics
    
    successful_runs = [r for r in pipeline_results if r.get('success')]
    quality_metrics['successful_processing_rate'] = len(successful_runs) / len(pipeline_results)
    
    # Calculate average processing time
    processing_times = [r.get('total_processing_time_ms', 0) for r in pipeline_results if r.get('total_processing_time_ms')]
    if processing_times:
        quality_metrics['average_processing_time_ms'] = sum(processing_times) / len(processing_times)
    
    # Analyze error patterns
    error_patterns = {}
    for result in pipeline_results:
        if not result.get('success') and result.get('error'):
            error_key = result['error'][:50]  # First 50 chars of error
            error_patterns[error_key] = error_patterns.get(error_key, 0) + 1
    
    quality_metrics['common_error_patterns'] = error_patterns
    
    return quality_metrics
```

This comprehensive data pipeline ensures robust, scalable processing of DEX files while maintaining data quality and providing valuable business intelligence for vending machine fleet management.