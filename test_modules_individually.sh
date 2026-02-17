#!/bin/bash

# Script to test each Ansible module individually with validate-modules sanity test
# This helps identify which specific modules have issues

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Counters
TOTAL_MODULES=0
PASSED_MODULES=0
FAILED_MODULES=0

# Arrays to store results
PASSED_LIST=()
FAILED_LIST=()

echo -e "${YELLOW}Starting individual module validation tests...${NC}"
echo "========================================================"

# Function to test a single module
test_module() {
    local module_path="$1"
    local module_name=$(basename "$module_path" .py)
    
    echo -n "Testing $module_name... "
    
    # Run ansible-test on the single module and capture output
    if ansible-test sanity --test validate-modules "$module_path" > /tmp/test_output_${module_name}.log 2>&1; then
        echo -e "${GREEN}PASSED${NC}"
        PASSED_LIST+=("$module_name")
        ((PASSED_MODULES++))
    else
        echo -e "${RED}FAILED${NC}"
        FAILED_LIST+=("$module_name")
        ((FAILED_MODULES++))
        
        # Show the error for failed modules
        echo -e "${RED}Error details:${NC}"
        cat /tmp/test_output_${module_name}.log | head -20
        echo "---"
    fi
    ((TOTAL_MODULES++))
}

# Test all SDS Block modules
echo -e "\n${YELLOW}Testing SDS Block modules:${NC}"
echo "----------------------------"
for module in plugins/modules/sds_block/*.py; do
    if [[ -f "$module" ]]; then
        test_module "$module"
    fi
done

# Test all VSP modules  
echo -e "\n${YELLOW}Testing VSP modules:${NC}"
echo "--------------------"
for module in plugins/modules/vsp/*.py; do
    if [[ -f "$module" ]]; then
        test_module "$module"
    fi
done

# Summary
echo ""
echo "========================================================"
echo -e "${YELLOW}SUMMARY:${NC}"
echo "Total modules tested: $TOTAL_MODULES"
echo -e "Passed: ${GREEN}$PASSED_MODULES${NC}"
echo -e "Failed: ${RED}$FAILED_MODULES${NC}"

if [[ $FAILED_MODULES -gt 0 ]]; then
    echo ""
    echo -e "${RED}FAILED MODULES:${NC}"
    for module in "${FAILED_LIST[@]}"; do
        echo "  - $module"
    done
    
    echo ""
    echo -e "${YELLOW}Detailed error logs saved in /tmp/test_output_<module_name>.log${NC}"
fi

if [[ $PASSED_MODULES -gt 0 ]]; then
    echo ""
    echo -e "${GREEN}PASSED MODULES:${NC}"
    for module in "${PASSED_LIST[@]}"; do
        echo "  - $module"
    done
fi

# Cleanup successful test logs
for module in "${PASSED_LIST[@]}"; do
    rm -f /tmp/test_output_${module}.log
done

echo ""
echo "========================================================"

# Exit with error code if any modules failed
if [[ $FAILED_MODULES -gt 0 ]]; then
    exit 1
else
    echo -e "${GREEN}All modules passed validation!${NC}"
    exit 0
fi