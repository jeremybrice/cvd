#!/usr/bin/env python3
"""
Grid Pattern Analyzer

Analyzes vending machine selection numbers to detect grid patterns and assign
row/column coordinates. Supports multiple common vending machine numbering schemes.

Features:
- Alphanumeric Grid: A1, A2, B1, B2 patterns
- Numeric Incremental Tens: 10, 12, 14 → 20, 22, 24 patterns  
- Sequential Blocks: 1-10 → 11-20 patterns
- Zero-padded Numeric: 01, 02 → 11, 12 patterns
- Custom Numeric: 101, 102 → 201, 202 patterns

Author: CVD System
Version: 1.0
"""

import re
from typing import List, Dict, Tuple, Optional
from collections import defaultdict
import math


class GridPatternAnalyzer:
    """Analyzes selection numbers to detect vending machine grid patterns"""
    
    def __init__(self):
        """Initialize the pattern analyzer with detection algorithms"""
        self.pattern_detectors = [
            self._detect_alphanumeric_pattern,
            self._detect_numeric_tens_pattern,
            self._detect_sequential_blocks_pattern,
            self._detect_zero_padded_numeric_pattern,
            self._detect_custom_numeric_pattern
        ]
    
    def analyze_selections(self, selections: List[str]) -> Dict:
        """
        Main entry point for pattern analysis
        
        Args:
            selections: List of selection numbers (e.g., ['A1', 'A2', 'B1'])
            
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
        
        # Clean and sort selections
        clean_selections = [str(s).strip() for s in selections if s and str(s).strip()]
        if not clean_selections:
            return self._empty_result("No valid selections found")
        
        # Try each pattern detector
        best_result = None
        best_confidence = 0.0
        
        for detector in self.pattern_detectors:
            try:
                result = detector(clean_selections)
                if result['confidence'] > best_confidence:
                    best_confidence = result['confidence']
                    best_result = result
            except Exception as e:
                # Log error but continue with other detectors
                continue
        
        if best_result and best_confidence >= 0.5:  # Minimum confidence threshold
            return best_result
        else:
            return self._empty_result("No clear pattern detected")
    
    def _empty_result(self, error_message: str) -> Dict:
        """Return empty result with error message"""
        return {
            'assignments': {},
            'pattern_type': 'unknown',
            'confidence': 0.0,
            'grid_dimensions': {'rows': 0, 'columns': 0},
            'errors': [error_message]
        }
    
    def _detect_alphanumeric_pattern(self, selections: List[str]) -> Dict:
        """
        Detect alphanumeric grid patterns like A1, A2, B1, B2
        
        Pattern: Letter prefix (row) + number suffix (column)
        """
        pattern_type = "alphanumeric_grid"
        assignments = {}
        errors = []
        
        # Regex to match letter+number pattern
        alpha_num_regex = re.compile(r'^([A-Za-z]+)(\d+)$')
        
        valid_selections = []
        for selection in selections:
            match = alpha_num_regex.match(selection)
            if match:
                letter_part = match.group(1).upper()
                number_part = int(match.group(2))
                valid_selections.append((selection, letter_part, number_part))
        
        if len(valid_selections) < len(selections) * 0.8:  # 80% must match pattern
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Less than 80% match alphanumeric pattern']}
        
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
        
        # Calculate grid dimensions
        max_columns = max(len(rows[row]) for row in rows) if rows else 0
        
        # Calculate confidence based on pattern regularity
        confidence = self._calculate_alphanumeric_confidence(rows, valid_selections, selections)
        
        return {
            'assignments': assignments,
            'pattern_type': pattern_type,
            'confidence': confidence,
            'grid_dimensions': {'rows': len(sorted_rows), 'columns': max_columns},
            'errors': errors
        }
    
    def _detect_numeric_tens_pattern(self, selections: List[str]) -> Dict:
        """
        Detect numeric incremental tens patterns like 10, 12, 14 → 20, 22, 24
        
        Pattern: Tens digit = row, units/increment = column
        """
        pattern_type = "numeric_tens"
        assignments = {}
        errors = []
        
        # Convert to integers
        try:
            numeric_selections = [(sel, int(sel)) for sel in selections if sel.isdigit()]
        except ValueError:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Non-numeric selections found']}
        
        if len(numeric_selections) < len(selections) * 0.9:  # 90% must be numeric
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Less than 90% numeric selections']}
        
        # Group by tens digit
        tens_groups = defaultdict(list)
        for selection, number in numeric_selections:
            tens_digit = number // 10
            tens_groups[tens_digit].append((selection, number))
        
        # Check for consistent incremental pattern within each tens group
        increment = None
        for tens_digit, group in tens_groups.items():
            if len(group) < 2:
                continue
                
            sorted_group = sorted(group, key=lambda x: x[1])
            group_increments = []
            for i in range(1, len(sorted_group)):
                inc = sorted_group[i][1] - sorted_group[i-1][1]
                group_increments.append(inc)
            
            # Check if increments are consistent
            if len(set(group_increments)) == 1:  # All increments are the same
                if increment is None:
                    increment = group_increments[0]
                elif increment != group_increments[0]:
                    # Inconsistent increments across tens groups
                    return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Inconsistent increments across tens groups']}
        
        if increment is None or increment <= 0:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['No consistent increment pattern found']}
        
        # Assign coordinates
        for tens_digit, group in tens_groups.items():
            sorted_group = sorted(group, key=lambda x: x[1])
            for col_index, (selection, number) in enumerate(sorted_group):
                # Calculate column based on position within tens group
                column_value = (number % 10) // (increment // 10) if increment >= 10 else (number % 10)
                assignments[selection] = {
                    'row': str(tens_digit),
                    'column': str(column_value)
                }
        
        # Calculate confidence
        total_expected = sum(len(group) for group in tens_groups.values())
        confidence = min(1.0, len(assignments) / len(selections) * 0.9) if total_expected > 0 else 0.0
        
        # Boost confidence if pattern is very regular
        if increment and len(tens_groups) > 1:
            confidence = min(1.0, confidence + 0.2)
        
        return {
            'assignments': assignments,
            'pattern_type': pattern_type,
            'confidence': confidence,
            'grid_dimensions': {'rows': len(tens_groups), 'columns': max(len(group) for group in tens_groups.values()) if tens_groups else 0},
            'errors': errors
        }
    
    def _detect_sequential_blocks_pattern(self, selections: List[str]) -> Dict:
        """
        Detect sequential block patterns like 1-10 → 11-20 → 21-30
        
        Pattern: Numbers grouped in sequential blocks
        """
        pattern_type = "sequential_blocks"
        assignments = {}
        errors = []
        
        # Convert to integers
        try:
            numeric_selections = [(sel, int(sel)) for sel in selections if sel.isdigit()]
        except ValueError:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Non-numeric selections found']}
        
        if len(numeric_selections) < len(selections) * 0.9:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Less than 90% numeric selections']}
        
        # Sort by number
        sorted_selections = sorted(numeric_selections, key=lambda x: x[1])
        
        # Detect block size by looking for gaps or patterns
        numbers = [num for _, num in sorted_selections]
        
        # Try different block sizes
        best_block_size = None
        best_confidence = 0.0
        
        for block_size in [5, 6, 8, 9, 10, 12, 15, 16, 20]:
            test_confidence = self._test_block_size(numbers, block_size)
            if test_confidence > best_confidence:
                best_confidence = test_confidence
                best_block_size = block_size
        
        if best_block_size is None or best_confidence < 0.5:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['No clear block pattern detected']}
        
        # Assign coordinates based on best block size
        for selection, number in sorted_selections:
            # Adjust for 1-based numbering
            adjusted_number = number - 1 if min(numbers) == 1 else number
            row = adjusted_number // best_block_size
            column = adjusted_number % best_block_size
            
            assignments[selection] = {
                'row': str(row),
                'column': str(column)
            }
        
        # Calculate grid dimensions
        max_row = max(int(assignments[sel]['row']) for sel in assignments) if assignments else 0
        
        return {
            'assignments': assignments,
            'pattern_type': pattern_type,
            'confidence': best_confidence,
            'grid_dimensions': {'rows': max_row + 1, 'columns': best_block_size},
            'errors': errors
        }
    
    def _detect_zero_padded_numeric_pattern(self, selections: List[str]) -> Dict:
        """
        Detect zero-padded numeric patterns like 01, 02, 03 → 11, 12, 13
        
        Pattern: Similar to sequential blocks but handles leading zeros
        """
        pattern_type = "zero_padded_numeric"
        assignments = {}
        errors = []
        
        # Check if selections have leading zeros
        has_leading_zeros = any(sel.startswith('0') and len(sel) > 1 for sel in selections)
        
        if not has_leading_zeros:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['No zero-padded selections found']}
        
        # Convert to integers while preserving original format info
        try:
            numeric_selections = []
            for sel in selections:
                if sel.isdigit():
                    numeric_selections.append((sel, int(sel), len(sel)))
        except ValueError:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Non-numeric selections found']}
        
        # Use sequential blocks logic but with zero-padding awareness
        numbers = [num for _, num, _ in numeric_selections]
        
        # Detect block size
        best_block_size = None
        best_confidence = 0.0
        
        for block_size in [5, 8, 9, 10, 12, 16]:
            test_confidence = self._test_block_size(numbers, block_size)
            if test_confidence > best_confidence:
                best_confidence = test_confidence
                best_block_size = block_size
        
        if best_block_size is None or best_confidence < 0.5:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['No clear zero-padded block pattern']}
        
        # Assign coordinates
        for selection, number, orig_length in numeric_selections:
            # Handle different starting points (0-based vs 1-based)
            adjusted_number = number if min(numbers) == 0 else number - 1
            row = adjusted_number // best_block_size
            column = adjusted_number % best_block_size
            
            assignments[selection] = {
                'row': str(row),
                'column': str(column)
            }
        
        return {
            'assignments': assignments,
            'pattern_type': pattern_type,
            'confidence': best_confidence,
            'grid_dimensions': {'rows': (max(numbers) // best_block_size) + 1, 'columns': best_block_size},
            'errors': errors
        }
    
    def _detect_custom_numeric_pattern(self, selections: List[str]) -> Dict:
        """
        Detect custom numeric patterns like 101, 102, 103 → 201, 202, 203
        
        Pattern: Hundreds digit = row, remainder = column
        """
        pattern_type = "custom_numeric"
        assignments = {}
        errors = []
        
        # Convert to integers
        try:
            numeric_selections = [(sel, int(sel)) for sel in selections if sel.isdigit()]
        except ValueError:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Non-numeric selections found']}
        
        if len(numeric_selections) < len(selections) * 0.9:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Less than 90% numeric selections']}
        
        # Check if numbers are in hundreds range (100+)
        numbers = [num for _, num in numeric_selections]
        if min(numbers) < 100:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['Numbers not in hundreds range']}
        
        # Group by hundreds digit
        hundreds_groups = defaultdict(list)
        for selection, number in numeric_selections:
            hundreds_digit = number // 100
            remainder = number % 100
            hundreds_groups[hundreds_digit].append((selection, number, remainder))
        
        # Check for consistent patterns within hundreds groups
        consistent_pattern = True
        remainders_per_group = []
        
        for hundreds_digit, group in hundreds_groups.items():
            remainders = [remainder for _, _, remainder in group]
            remainders_per_group.append(len(remainders))
            
            # Check if remainders are sequential or have a pattern
            sorted_remainders = sorted(remainders)
            gaps = [sorted_remainders[i+1] - sorted_remainders[i] for i in range(len(sorted_remainders)-1)]
            
            if gaps and len(set(gaps)) > 2:  # Too many different gap sizes
                consistent_pattern = False
                break
        
        if not consistent_pattern:
            return {'confidence': 0.0, 'pattern_type': pattern_type, 'assignments': {}, 'errors': ['No consistent pattern within hundreds groups']}
        
        # Assign coordinates
        for hundreds_digit, group in hundreds_groups.items():
            sorted_group = sorted(group, key=lambda x: x[2])  # Sort by remainder
            for col_index, (selection, number, remainder) in enumerate(sorted_group):
                assignments[selection] = {
                    'row': str(hundreds_digit),
                    'column': str(remainder)
                }
        
        # Calculate confidence based on pattern consistency
        confidence = 0.8 if consistent_pattern and len(hundreds_groups) > 1 else 0.6
        
        return {
            'assignments': assignments,
            'pattern_type': pattern_type,
            'confidence': confidence,
            'grid_dimensions': {'rows': len(hundreds_groups), 'columns': max(remainders_per_group) if remainders_per_group else 0},
            'errors': errors
        }
    
    def _test_block_size(self, numbers: List[int], block_size: int) -> float:
        """Test how well a block size fits the number sequence"""
        if not numbers:
            return 0.0
        
        # Check if numbers fit well into blocks of this size
        min_num = min(numbers)
        blocks = defaultdict(list)
        
        for num in numbers:
            adjusted = num - min_num if min_num > 0 else num
            block_index = adjusted // block_size
            position_in_block = adjusted % block_size
            blocks[block_index].append(position_in_block)
        
        # Calculate confidence based on:
        # 1. How many blocks are used
        # 2. How evenly filled blocks are
        # 3. How sequential positions within blocks are
        
        total_positions = len(numbers)
        expected_blocks = math.ceil(total_positions / block_size)
        actual_blocks = len(blocks)
        
        # Penalty for too many sparse blocks
        block_usage_score = min(1.0, expected_blocks / actual_blocks) if actual_blocks > 0 else 0.0
        
        # Check sequentiality within blocks
        sequentiality_score = 0.0
        for block_positions in blocks.values():
            sorted_positions = sorted(block_positions)
            if len(sorted_positions) > 1:
                gaps = [sorted_positions[i+1] - sorted_positions[i] for i in range(len(sorted_positions)-1)]
                # Prefer smaller, consistent gaps
                avg_gap = sum(gaps) / len(gaps)
                sequentiality_score += 1.0 / (1.0 + avg_gap)
        
        sequentiality_score = sequentiality_score / len(blocks) if blocks else 0.0
        
        return (block_usage_score + sequentiality_score) / 2.0
    
    def _calculate_alphanumeric_confidence(self, rows: Dict, valid_selections: List, all_selections: List) -> float:
        """Calculate confidence for alphanumeric pattern detection"""
        if not valid_selections:
            return 0.0
        
        # Base confidence on percentage of selections that match pattern
        match_percentage = len(valid_selections) / len(all_selections)
        
        # Bonus for consistent row sizes
        row_sizes = [len(rows[row]) for row in rows]
        size_consistency = 1.0 - (len(set(row_sizes)) - 1) * 0.1  # Penalty for varying row sizes
        
        # Bonus for sequential column numbers within rows
        sequential_bonus = 0.0
        for row_letter, row_selections in rows.items():
            numbers = sorted([num for _, num in row_selections])
            if len(numbers) > 1:
                gaps = [numbers[i+1] - numbers[i] for i in range(len(numbers)-1)]
                if all(gap == 1 for gap in gaps):  # Perfect sequence
                    sequential_bonus += 0.1
        
        return min(1.0, match_percentage * size_consistency + sequential_bonus)


# Test function for development
def test_grid_pattern_analyzer():
    """Test the grid pattern analyzer with sample data"""
    analyzer = GridPatternAnalyzer()
    
    # Test alphanumeric pattern
    alphanumeric_selections = ['A1', 'A2', 'A3', 'B1', 'B2', 'B3', 'C1', 'C2', 'C3']
    result = analyzer.analyze_selections(alphanumeric_selections)
    print(f"Alphanumeric test: {result['pattern_type']}, confidence: {result['confidence']:.2f}")
    
    # Test numeric tens pattern
    numeric_tens_selections = ['10', '12', '14', '16', '20', '22', '24', '26']
    result = analyzer.analyze_selections(numeric_tens_selections)
    print(f"Numeric tens test: {result['pattern_type']}, confidence: {result['confidence']:.2f}")
    
    # Test sequential blocks
    sequential_selections = ['1', '2', '3', '4', '5', '6', '7', '8', '9']
    result = analyzer.analyze_selections(sequential_selections)
    print(f"Sequential test: {result['pattern_type']}, confidence: {result['confidence']:.2f}")


if __name__ == "__main__":
    test_grid_pattern_analyzer()