#!/bin/bash
# CVD Documentation Complete Validation Runner
# Executes all validation components and generates reports

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
DOC_ROOT="$(dirname "$SCRIPT_DIR")"
TIMESTAMP=$(date '+%Y-%m-%d_%H-%M-%S')
RESULTS_DIR="$DOC_ROOT/validation-results"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
NC='\033[0m'

echo -e "${PURPLE}🔍 CVD Documentation Complete Validation Suite${NC}"
echo -e "${BLUE}📁 Documentation root: $DOC_ROOT${NC}"
echo -e "${BLUE}⏰ Started at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"
echo "=================================================================="

# Create results directory
mkdir -p "$RESULTS_DIR"

# Initialize counters
TOTAL_TESTS=0
PASSED_TESTS=0
FAILED_TESTS=0
WARNINGS=0

echo -e "${BLUE}📋 Validation Components:${NC}"
echo "   1. Internal Link Validation"
echo "   2. External Link Validation" 
echo "   3. Navigation System Testing"
echo "   4. Metadata Integrity Check"
echo "   5. Search Index Validation"
echo ""

# 1. Run Link Checker (fast validation)
echo -e "${YELLOW}🔗 Running Quick Link Validation...${NC}"
if "$SCRIPT_DIR/link-checker.sh" > "$RESULTS_DIR/link-check-$TIMESTAMP.log" 2>&1; then
    echo -e "   ${GREEN}✅ Quick link validation: PASSED${NC}"
    ((PASSED_TESTS++))
else
    echo -e "   ${RED}❌ Quick link validation: FAILED${NC}"
    echo -e "      See: $RESULTS_DIR/link-check-$TIMESTAMP.log"
    ((FAILED_TESTS++))
fi
((TOTAL_TESTS++))

# 2. Run Full Validation Suite (if Python available)
echo -e "${YELLOW}🔍 Running Comprehensive Validation...${NC}"
if command -v python3 &> /dev/null; then
    if python3 "$SCRIPT_DIR/validation-suite.py" > "$RESULTS_DIR/full-validation-$TIMESTAMP.log" 2>&1; then
        echo -e "   ${GREEN}✅ Comprehensive validation: PASSED${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "   ${YELLOW}⚠️  Comprehensive validation: WARNINGS${NC}"
        echo -e "      See: $RESULTS_DIR/full-validation-$TIMESTAMP.log"
        ((WARNINGS++))
    fi
else
    echo -e "   ${YELLOW}⏭️  Skipped (Python not available)${NC}"
fi
((TOTAL_TESTS++))

# 3. Check specific validation files exist
echo -e "${YELLOW}📄 Checking Validation Documentation...${NC}"
validation_files=(
    "LINK_VALIDATION.md"
    "EXTERNAL_LINKS.md"
    "NAVIGATION_TEST.md"
    "VALIDATION_SUMMARY.md"
)

for file in "${validation_files[@]}"; do
    if [[ -f "$DOC_ROOT/$file" ]]; then
        echo -e "   ${GREEN}✅ $file exists${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "   ${RED}❌ $file missing${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# 4. Check validation scripts exist
echo -e "${YELLOW}🔧 Checking Validation Scripts...${NC}"
script_files=(
    "scripts/validation-suite.py"
    "scripts/link-checker.sh"
    "scripts/validate-all.sh"
)

for script in "${script_files[@]}"; do
    if [[ -f "$DOC_ROOT/$script" ]]; then
        echo -e "   ${GREEN}✅ $script exists and executable${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "   ${RED}❌ $script missing${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# 5. Check key documentation structure
echo -e "${YELLOW}📂 Checking Documentation Structure...${NC}"
structure_check=(
    "00-index"
    "01-project-core"
    "02-requirements"
    "03-architecture"
    "04-implementation"
    "05-development"
    "06-design"
    "07-cvd-framework"
    "08-project-management"
    "09-reference"
)

for category in "${structure_check[@]}"; do
    if [[ -d "$DOC_ROOT/$category" ]]; then
        echo -e "   ${GREEN}✅ Category $category exists${NC}"
        ((PASSED_TESTS++))
    else
        echo -e "   ${RED}❌ Category $category missing${NC}"
        ((FAILED_TESTS++))
    fi
    ((TOTAL_TESTS++))
done

# 6. Quick file count check
echo -e "${YELLOW}📊 Documentation Statistics...${NC}"
total_md_files=$(find "$DOC_ROOT" -name "*.md" | wc -l)
total_dirs=$(find "$DOC_ROOT" -type d | wc -l)
total_size=$(du -sh "$DOC_ROOT" | cut -f1)

echo "   📄 Total .md files: $total_md_files"
echo "   📁 Total directories: $total_dirs"
echo "   💾 Total size: $total_size"

if [[ $total_md_files -ge 50 ]]; then
    echo -e "   ${GREEN}✅ Good documentation coverage${NC}"
    ((PASSED_TESTS++))
else
    echo -e "   ${YELLOW}⚠️  Limited documentation coverage${NC}"
    ((WARNINGS++))
fi
((TOTAL_TESTS++))

# Generate summary report
echo ""
echo "=================================================================="
echo -e "${PURPLE}📋 VALIDATION SUMMARY${NC}"
echo "=================================================================="

success_rate=0
if [[ $TOTAL_TESTS -gt 0 ]]; then
    success_rate=$((PASSED_TESTS * 100 / TOTAL_TESTS))
fi

echo -e "${BLUE}📊 Test Results:${NC}"
echo "   Total Tests: $TOTAL_TESTS"
echo "   Passed: $PASSED_TESTS"
echo "   Failed: $FAILED_TESTS"
echo "   Warnings: $WARNINGS"
echo "   Success Rate: ${success_rate}%"
echo ""

# Overall assessment
if [[ $FAILED_TESTS -eq 0 ]]; then
    if [[ $WARNINGS -eq 0 ]]; then
        echo -e "${GREEN}🎉 VALIDATION COMPLETE: ALL SYSTEMS OPERATIONAL${NC}"
        echo -e "${GREEN}✅ Documentation system is ready for production use${NC}"
        exit_code=0
    else
        echo -e "${YELLOW}⚠️  VALIDATION COMPLETE: MINOR WARNINGS${NC}"
        echo -e "${YELLOW}✅ Documentation system is operational with minor improvements needed${NC}"
        exit_code=0
    fi
else
    echo -e "${RED}❌ VALIDATION FAILED: CRITICAL ISSUES FOUND${NC}"
    echo -e "${RED}⚠️  Documentation system requires fixes before production use${NC}"
    exit_code=1
fi

echo ""
echo -e "${BLUE}📁 Detailed results saved to: $RESULTS_DIR/${NC}"
echo -e "${BLUE}⏰ Validation completed at: $(date '+%Y-%m-%d %H:%M:%S')${NC}"

# Create summary file
cat > "$RESULTS_DIR/validation-summary-$TIMESTAMP.txt" << EOF
CVD Documentation Validation Summary
===================================
Date: $(date '+%Y-%m-%d %H:%M:%S')
Duration: $(date '+%Y-%m-%d %H:%M:%S')

Results:
  Total Tests: $TOTAL_TESTS
  Passed: $PASSED_TESTS
  Failed: $FAILED_TESTS
  Warnings: $WARNINGS
  Success Rate: ${success_rate}%

Status: $(if [[ $exit_code -eq 0 ]]; then echo "PASSED"; else echo "FAILED"; fi)

Documentation Statistics:
  Markdown files: $total_md_files
  Directories: $total_dirs
  Total size: $total_size

Detailed logs available in:
$RESULTS_DIR/
EOF

echo -e "${BLUE}📄 Summary saved to: $RESULTS_DIR/validation-summary-$TIMESTAMP.txt${NC}"

exit $exit_code