---
type: reference-data
category: examples
title: DEX File Samples for Testing
status: active
last_updated: 2025-08-12
tags: [dex-parser, testing, samples, vending-machines]
cross_references:
  - /documentation/07-cvd-framework/dex-parser/OVERVIEW.md
  - /documentation/07-cvd-framework/dex-parser/TECHNICAL_IMPLEMENTATION.md
---

# DEX File Samples

## Purpose
Sample DEX files from various vending machine manufacturers used for testing and validating the DEX parser functionality.

## Contents

### AMS (Automatic Merchandising Systems)
- **AMS_39_VCF.txt** - AMS 39 VCF vending machine DEX output
- **AMS_Sensit_III.txt** - AMS Sensit III vending machine DEX output

### Dixie Narco
- **Dixie_Narco_501E.txt** - Dixie Narco 501E model DEX output  
- **Dixie_Narco_5800.txt** - Dixie Narco 5800 model DEX output

### Other Manufacturers
- **Crane_National_187.txt** - Crane National 187 model DEX output
- **Royal_660.txt** - Royal 660 model DEX output
- **Vendo_721.txt** - Vendo 721 model DEX output

## Usage

These files are used for:
1. **DEX Parser Testing** - Validating parser logic against real-world data
2. **Grid Pattern Analysis** - Testing grid pattern detection algorithms
3. **Integration Testing** - End-to-end testing of DEX processing pipeline
4. **Development** - Local testing during DEX parser development

## File Format

All DEX files follow the standard DEX format with:
- Header records (ID1, ID4, etc.)
- Transaction records (CA2, CA3, etc.)  
- Audit records (PA1, PA2, etc.)
- Various vendor-specific extensions

## Testing Notes

- Files contain real transaction data (anonymized)
- Grid patterns vary by manufacturer and model
- Some files contain multiple audit periods
- Record types supported vary by manufacturer

## Cross-References
- [DEX Parser Implementation](/documentation/07-cvd-framework/dex-parser/TECHNICAL_IMPLEMENTATION.md)
- [Grid Pattern Analysis](/documentation/07-cvd-framework/dex-parser/DATA_PIPELINE.md)
- [Testing Strategy](/documentation/05-development/testing/STRATEGY.md)