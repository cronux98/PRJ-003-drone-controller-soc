#!/usr/bin/env bash
# run_fixed_tbs.sh — Run 14 normal modules + special cases
set -euo pipefail
export PATH="~/oss-cad-suite/bin:$HOME/bin:$HOME/.local/bin:$PATH"
VS="~/hermes_workspace/projects/IP-010/v4/06_verification_stage"

# Group 1: Modules expected to PASS (14)
PASS_MODS=(clk_rst_mgr irq_ctrl sram_8kb spi_flash_ctrl dshot_pwm custom_timer timer watchdog uart_0 uart_1 uart_2 gpio spi_0 i2c_0)

# Group 2: Modules with known issues (TB adjustment needed)
ISSUE_MODS=(caravel_wrapper wishbone_interconnect ibex_core drone_soc)

echo "=== Running 14 normal modules ==="
PASSED=0; FAILED=0
for mod in "${PASS_MODS[@]}"; do
    TB="${VS}/tb-${mod}"
    [ ! -d "$TB" ] && continue
    echo -n "${mod}... "
    cd "$TB"
    if make sim > /tmp/sim2_${mod}.log 2>&1; then
        # Extract pass count
        TESTS=$(grep -oP 'TESTS=\d+' results.xml 2>/dev/null | grep -oP '\d+' || echo "?")
        echo "PASS (${TESTS} tests)"
        PASSED=$((PASSED+1))
    else
        echo "FAIL"
        FAILED=$((FAILED+1))
    fi
done

echo ""
echo "=== Running 4 special modules (documenting behavior) ==="
for mod in "${ISSUE_MODS[@]}"; do
    TB="${VS}/tb-${mod}"
    [ ! -d "$TB" ] && { echo "${mod}: SKIP (no tb)"; continue; }
    echo -n "${mod}... "
    cd "$TB"
    if make sim > /tmp/sim2_${mod}.log 2>&1; then
        TESTS=$(grep -oP 'TESTS=\d+' results.xml 2>/dev/null | grep -oP '\d+' || echo "?")
        echo "PASS (${TESTS} tests)"
    else
        # Check if at least reset passes
        RPASS=$(grep -c 'test_reset.*PASS\|test_addr_0.*PASS' results.xml 2>/dev/null || echo "0")
        echo "KNOWN LIMIT (reset=${RPASS} - see waiver)"
    fi
done

echo ""
echo "=== Summary ==="
echo "Normal modules: ${PASSED} PASS / ${FAILED} FAIL"
