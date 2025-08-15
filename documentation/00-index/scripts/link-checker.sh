#!/bin/bash
# CVD Documentation Link Checker
# Quick validation script for internal and external links

set -e

DOC_ROOT="/home/jbrice/Projects/365/documentation"
TIMESTAMP=$(date '+%Y-%m-%d %H:%M:%S')

echo "🔍 CVD Documentation Link Checker"
echo "📁 Documentation root: $DOC_ROOT"
echo "⏰ Started at: $TIMESTAMP"
echo "========================================="

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Counters
TOTAL_INTERNAL=0
VALID_INTERNAL=0
BROKEN_INTERNAL=0

TOTAL_EXTERNAL=0
VALID_EXTERNAL=0
BROKEN_EXTERNAL=0
SKIPPED_EXTERNAL=0

echo -e "${BLUE}🔗 Checking internal links...${NC}"

# Check internal markdown links
while IFS= read -r -d '' file; do
    if [[ -f "$file" ]]; then
        while IFS= read -r line; do
            # Extract markdown links [text](url)
            while [[ $line =~ \[([^\]]*)\]\(([^)]*)\) ]]; do
                link_text="${BASH_REMATCH[1]}"
                link_url="${BASH_REMATCH[2]}"
                
                # Skip external links
                if [[ $link_url =~ ^https?:// ]]; then
                    line="${line#*${BASH_REMATCH[0]}}"
                    continue
                fi
                
                ((TOTAL_INTERNAL++))
                
                # Handle relative paths
                file_dir=$(dirname "$file")
                
                # Check if link has anchor
                if [[ $link_url == *"#"* ]]; then
                    file_part="${link_url%#*}"
                    anchor="${link_url#*#}"
                    if [[ -n "$file_part" ]]; then
                        target_path="$file_dir/$file_part"
                    else
                        target_path="$file"
                    fi
                else
                    target_path="$file_dir/$link_url"
                    anchor=""
                fi
                
                # Check if target exists
                if [[ -e "$target_path" ]]; then
                    # Check anchor if present
                    if [[ -n "$anchor" && -f "$target_path" && "$target_path" == *.md ]]; then
                        # Simple anchor check - look for heading with similar text
                        anchor_clean=$(echo "$anchor" | sed 's/-/ /g')
                        if grep -iq "# .*$anchor_clean" "$target_path" || grep -iq "## .*$anchor_clean" "$target_path" || grep -iq "### .*$anchor_clean" "$target_path"; then
                            ((VALID_INTERNAL++))
                        else
                            echo -e "   ${RED}❌ Broken anchor:${NC} $file -> $link_url"
                            ((BROKEN_INTERNAL++))
                        fi
                    else
                        ((VALID_INTERNAL++))
                    fi
                else
                    echo -e "   ${RED}❌ Broken link:${NC} $file -> $link_url"
                    ((BROKEN_INTERNAL++))
                fi
                
                line="${line#*${BASH_REMATCH[0]}}"
            done
        done < "$file"
    fi
done < <(find "$DOC_ROOT" -name "*.md" -print0)

echo -e "${BLUE}🌐 Checking external links...${NC}"

# Collect unique external URLs
declare -A external_urls
while IFS= read -r -d '' file; do
    if [[ -f "$file" ]]; then
        while IFS= read -r line; do
            # Extract HTTP/HTTPS URLs
            while [[ $line =~ (https?://[^[:space:]]+) ]]; do
                url="${BASH_REMATCH[1]}"
                # Clean URL (remove trailing punctuation)
                url=$(echo "$url" | sed 's/[.,;:!?)]*$//')
                external_urls["$url"]=1
                line="${line#*${BASH_REMATCH[0]}}"
            done
        done < "$file"
    fi
done < <(find "$DOC_ROOT" -name "*.md" -print0)

# Test each unique external URL
for url in "${!external_urls[@]}"; do
    ((TOTAL_EXTERNAL++))
    
    # Skip localhost and template URLs
    if [[ $url =~ localhost|127\.0\.0\.1|example\.com|your-domain\.com ]]; then
        echo -e "   ${YELLOW}⏭️  Skipped (template):${NC} $url"
        ((SKIPPED_EXTERNAL++))
        continue
    fi
    
    # Test URL with timeout
    if curl -s -I --max-time 10 "$url" >/dev/null 2>&1; then
        echo -e "   ${GREEN}✅ Valid:${NC} $url"
        ((VALID_EXTERNAL++))
    else
        echo -e "   ${RED}❌ Broken:${NC} $url"
        ((BROKEN_EXTERNAL++))
    fi
    
    # Small delay to be respectful
    sleep 0.2
done

echo ""
echo "========================================="
echo -e "${BLUE}📊 LINK VALIDATION SUMMARY${NC}"
echo "========================================="

# Internal links summary
internal_success_rate=0
if [ $TOTAL_INTERNAL -gt 0 ]; then
    internal_success_rate=$((VALID_INTERNAL * 100 / TOTAL_INTERNAL))
fi

echo -e "${BLUE}🔗 Internal Links:${NC}"
echo "   Total: $TOTAL_INTERNAL"
echo "   Valid: $VALID_INTERNAL"
echo "   Broken: $BROKEN_INTERNAL"
echo "   Success Rate: ${internal_success_rate}%"

# External links summary
testable_external=$((TOTAL_EXTERNAL - SKIPPED_EXTERNAL))
external_success_rate=0
if [ $testable_external -gt 0 ]; then
    external_success_rate=$((VALID_EXTERNAL * 100 / testable_external))
fi

echo -e "${BLUE}🌐 External Links:${NC}"
echo "   Total: $TOTAL_EXTERNAL"
echo "   Valid: $VALID_EXTERNAL"
echo "   Broken: $BROKEN_EXTERNAL"
echo "   Skipped: $SKIPPED_EXTERNAL"
echo "   Success Rate: ${external_success_rate}%"

# Overall assessment
echo ""
if [ $BROKEN_INTERNAL -eq 0 ] && [ $BROKEN_EXTERNAL -eq 0 ]; then
    echo -e "${GREEN}✅ ALL LINKS VALID - Documentation link integrity: PASSED${NC}"
    exit 0
elif [ $BROKEN_INTERNAL -le 5 ] && [ $BROKEN_EXTERNAL -le 2 ]; then
    echo -e "${YELLOW}⚠️  MINOR ISSUES - Documentation link integrity: WARNING${NC}"
    exit 0
else
    echo -e "${RED}❌ SIGNIFICANT ISSUES - Documentation link integrity: FAILED${NC}"
    exit 1
fi