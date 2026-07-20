#!/bin/bash
# Batch lint all modules with both iverilog and verilator
set -e
source "$(dirname "$0")/env_setup.sh"
V4="$(dirname "$0")/.."
RESULTS="$V4/results"
mkdir -p "$RESULTS"

echo "=== BATCH LINT REPORT ===" > "$RESULTS/lint_summary.txt"
echo "Generated: $(date)" >> "$RESULTS/lint_summary.txt"
echo "" >> "$RESULTS/lint_summary.txt"

for mod_dir in $V4/rtl-*/; do
    mod=$(basename "$mod_dir" | sed 's/^rtl-//')
    rtl_dir="$mod_dir/rtl"
    log_dir="$mod_dir/logs/lint"
    
    [ "$mod" = "drone_soc" ] && continue  # skip top for now
    
    rtl_files=$(ls "$rtl_dir"/*.v 2>/dev/null | tr '\n' ' ')
    [ -z "$rtl_files" ] && continue
    
    # Verilator
    verilator --lint-only -Wall -Wno-fatal $rtl_files 2>&1 | tee "$log_dir/${mod}_verilator.log"
    v_warn=$(grep -ci 'warning' "$log_dir/${mod}_verilator.log" 2>/dev/null || echo 0)
    v_err=$(grep -ci 'error' "$log_dir/${mod}_verilator.log" 2>/dev/null || echo 0)
    
    # Icarus
    iverilog -Wall -g2005 -o /dev/null $rtl_files 2>&1 | tee "$log_dir/${mod}_iverilog.log"
    i_warn=$(grep -ci 'warning' "$log_dir/${mod}_iverilog.log" 2>/dev/null || echo 0)
    i_err=$(grep -ci 'error' "$log_dir/${mod}_iverilog.log" 2>/dev/null || echo 0)
    
    if [ "$v_err" = "0" ] && [ "$i_err" = "0" ]; then
        echo "PASS: $mod (v:$v_warn/$v_err i:$i_warn/$i_err)" | tee -a "$RESULTS/lint_summary.txt"
    else
        echo "FAIL: $mod (v:$v_warn/$v_err i:$i_warn/$i_err)" | tee -a "$RESULTS/lint_summary.txt"
    fi
done
echo "=== DONE ===" >> "$RESULTS/lint_summary.txt"

