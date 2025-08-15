#!/usr/bin/env python3
"""
Update Existing Grid Patterns

Batch process existing dex_pa_records to populate row/column fields
using the GridPatternAnalyzer for all historical data.

Usage:
    python update_existing_grid_patterns.py

Author: CVD System
Version: 1.0
"""

import sqlite3
from typing import Dict, List
from grid_pattern_analyzer import GridPatternAnalyzer
import time


def update_existing_pa_records():
    """Process all existing dex_pa_records and populate row/column fields"""
    
    print("=== UPDATING EXISTING PA RECORDS WITH GRID PATTERNS ===")
    
    # Connect to database
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    try:
        # Get all unique dex_read_ids
        cursor.execute('SELECT DISTINCT dex_read_id FROM dex_pa_records ORDER BY dex_read_id')
        dex_read_ids = [row[0] for row in cursor.fetchall()]
        
        print(f"Found {len(dex_read_ids)} DEX files to process")
        
        analyzer = GridPatternAnalyzer()
        total_updated = 0
        successful_analyses = 0
        failed_analyses = 0
        
        # Process each DEX file
        for i, dex_read_id in enumerate(dex_read_ids, 1):
            print(f"\\nProcessing DEX_READ {dex_read_id} ({i}/{len(dex_read_ids)})...")
            
            # Get all PA records for this DEX file
            cursor.execute('''
                SELECT id, selection_number 
                FROM dex_pa_records 
                WHERE dex_read_id = ? 
                ORDER BY selection_number
            ''', (dex_read_id,))
            
            records = cursor.fetchall()
            if not records:
                print(f"  No records found for DEX_READ {dex_read_id}")
                continue
            
            # Extract selection numbers
            selection_numbers = [record[1] for record in records if record[1]]
            record_ids = [record[0] for record in records]
            
            if not selection_numbers:
                print(f"  No valid selection numbers in DEX_READ {dex_read_id}")
                continue
            
            print(f"  Analyzing {len(selection_numbers)} selections: {selection_numbers[:5]}{'...' if len(selection_numbers) > 5 else ''}")
            
            # Analyze grid pattern
            try:
                grid_result = analyzer.analyze_selections(selection_numbers)
                
                print(f"  Pattern: {grid_result['pattern_type']}")
                print(f"  Confidence: {grid_result['confidence']:.2f}")
                print(f"  Grid: {grid_result['grid_dimensions']['rows']}x{grid_result['grid_dimensions']['columns']}")
                
                if grid_result['confidence'] >= 0.5:  # Only update if confident
                    # Update records with row/column assignments
                    updates_made = 0
                    for record_id, selection_number in zip(record_ids, selection_numbers):
                        if selection_number in grid_result.get('assignments', {}):
                            assignment = grid_result['assignments'][selection_number]
                            
                            cursor.execute('''
                                UPDATE dex_pa_records 
                                SET row = ?, "column" = ? 
                                WHERE id = ?
                            ''', (assignment['row'], assignment['column'], record_id))
                            
                            updates_made += 1
                    
                    print(f"  ✅ Updated {updates_made} records")
                    total_updated += updates_made
                    successful_analyses += 1
                    
                else:
                    print(f"  ⚠️ Low confidence ({grid_result['confidence']:.2f}), skipping updates")
                    failed_analyses += 1
                    
            except Exception as e:
                print(f"  ❌ Analysis failed: {str(e)}")
                failed_analyses += 1
                continue
        
        # Commit all changes
        db.commit()
        
        print(f"\\n=== BATCH UPDATE COMPLETE ===")
        print(f"Total records updated: {total_updated}")
        print(f"Successful analyses: {successful_analyses}")
        print(f"Failed analyses: {failed_analyses}")
        print(f"Success rate: {successful_analyses/(successful_analyses+failed_analyses)*100:.1f}%" if (successful_analyses+failed_analyses) > 0 else "N/A")
        
        # Verify results
        cursor.execute('SELECT COUNT(*) FROM dex_pa_records WHERE row IS NOT NULL AND "column" IS NOT NULL')
        total_with_grid = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM dex_pa_records')
        total_records = cursor.fetchone()[0]
        
        print(f"\\n=== VERIFICATION ===")
        print(f"Records with grid data: {total_with_grid}/{total_records} ({total_with_grid/total_records*100:.1f}%)")
        
        # Show sample results
        print(f"\\n=== SAMPLE RESULTS ===")
        cursor.execute('''
            SELECT dex_read_id, selection_number, row, "column" 
            FROM dex_pa_records 
            WHERE row IS NOT NULL AND "column" IS NOT NULL 
            ORDER BY dex_read_id, selection_number 
            LIMIT 10
        ''')
        
        samples = cursor.fetchall()
        for sample in samples:
            print(f"DEX {sample[0]}: Selection {sample[1]} → Row {sample[2]}, Column {sample[3]}")
        
    except Exception as e:
        print(f"❌ Batch update failed: {str(e)}")
        db.rollback()
        
    finally:
        db.close()


def verify_grid_patterns():
    """Verify the grid pattern assignments are correct"""
    
    print("\\n=== VERIFYING GRID PATTERNS ===")
    
    db = sqlite3.connect('cvd.db')
    cursor = db.cursor()
    
    try:
        # Get pattern distribution
        cursor.execute('''
            SELECT dex_read_id, COUNT(*) as record_count,
                   COUNT(CASE WHEN row IS NOT NULL THEN 1 END) as with_grid
            FROM dex_pa_records 
            GROUP BY dex_read_id 
            ORDER BY dex_read_id
        ''')
        
        results = cursor.fetchall()
        print("DEX File | Total Records | With Grid | Coverage")
        print("-" * 50)
        
        for dex_id, total, with_grid in results:
            coverage = (with_grid / total * 100) if total > 0 else 0
            print(f"DEX {dex_id:3d}  | {total:11d} | {with_grid:7d} | {coverage:6.1f}%")
        
        # Check for any inconsistencies
        cursor.execute('''
            SELECT dex_read_id, COUNT(DISTINCT row) as row_count, 
                   COUNT(DISTINCT "column") as col_count,
                   GROUP_CONCAT(DISTINCT row ORDER BY row) as rows,
                   GROUP_CONCAT(DISTINCT "column" ORDER BY "column") as columns
            FROM dex_pa_records 
            WHERE row IS NOT NULL AND "column" IS NOT NULL
            GROUP BY dex_read_id
        ''')
        
        grid_info = cursor.fetchall()
        print(f"\\n=== GRID DIMENSIONS ===")
        
        for dex_id, row_count, col_count, rows, columns in grid_info:
            print(f"DEX {dex_id}: {row_count}x{col_count} grid")
            print(f"  Rows: {rows}")
            print(f"  Columns: {columns[:50]}{'...' if len(columns) > 50 else ''}")
        
    except Exception as e:
        print(f"❌ Verification failed: {str(e)}")
        
    finally:
        db.close()


if __name__ == "__main__":
    start_time = time.time()
    
    update_existing_pa_records()
    verify_grid_patterns()
    
    end_time = time.time()
    print(f"\\n⏱️ Total processing time: {end_time - start_time:.2f} seconds")