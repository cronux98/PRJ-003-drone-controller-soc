#!/usr/bin/env bash
# run_all_tbs.sh — Run all 18 module cocotb testbenches sequentially
# Output: results.xml per module, summary log

set -euo pipefail

export PATH="~/oss-cad-suite/bin:$HOME/bin:$HOME/.local/bin:$PATH"

BASE="~/hermes_workspace/projects/IP-010/v4"
VS="${BASE}/06_verification_stage"
LOG="${VS}/batch_run.log"

MODULES=(
    clk_rst_mgr irq_ctrl caravel_wrapper sram_8kb wishbone_interconnect
    spi_flash_ctrl dshot_pwm custom_timer
    timer watchdog
    uart_0 uart_1 uart_2 gpio
    spi_0 i2c_0
    ibex_core drone_soc
)

echo "=== Batch run started $(date) ===" | tee "$LOG"
PASS_COUNT=0
FAIL_COUNT=0
TOTAL_TESTS=0
TOTAL_PASS=0
TOTAL_FAIL=0

for mod in "${MODULES[@]}"; do
    TB_DIR="${VS}/tb-${mod}"
    if [ ! -d "$TB_DIR" ]; then
        echo "SKIP ${mod}: no tb directory" | tee -a "$LOG"
        continue
    fi

    echo "" | tee -a "$LOG"
    echo "--- ${mod} ---" | tee -a "$LOG"
    cd "$TB_DIR"

    if make sim > /tmp/sim_${mod}.log 2>&1; then
        echo "  PASS" | tee -a "$LOG"
        PASS_COUNT=$((PASS_COUNT + 1))
    else
        echo "  FAIL (see /tmp/sim_${mod}.log)" | tee -a "$LOG"
        FAIL_COUNT=$((FAIL_COUNT + 1))
    fi

    # Extract test counts from results.xml if it exists
    if [ -f results.xml ]; then
        TESTS=$(grep -c 'testsuite.*tests=' results.xml || echo "0")
        echo "  results.xml: $(wc -c < results.xml)B" | tee -a "$LOG"
    fi
done

echo "" | tee -a "$LOG"
echo "=== Batch run complete $(date) ===" | tee -a "$LOG"
echo "Modules PASS: ${PASS_COUNT}  FAIL: ${FAIL_COUNT}" | tee -a "$LOG"
