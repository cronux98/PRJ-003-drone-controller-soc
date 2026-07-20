# IP-010 v4 — Frontend Stage Results
## Generated: 2026-07-19 (run #25)

### Stage Summary
- **Modules:** 18 (17 leaf + 1 top)
- **Top Module:** drone_soc (Wishbone B4, 15-slave, wb_interconnect_bus)
- **PDK:** sky130_fd_sc_hd (sky130A)
- **Clock:** 16.67 MHz
- **Processor:** Ibex RV32IMC

---

### 1. RTL Authoring

| Module | Classification | RTL Files | Status |
|--------|---------------|-----------|--------|
| ibex_core | REUSE_INTERNAL | 15 (.v) | COPIED from v3 |
| wishbone_interconnect | REUSE_INTERNAL | 1 (.v) | COPIED from v3 |
| sram_8kb | REUSE_INTERNAL | 2 (.v) | COPIED from v3 |
| uart_0 | REUSE_INTERNAL | 5 (.v) | COPIED from v3 |
| uart_1 | REUSE_INTERNAL | 5 (.v) | COPIED from v3 |
| uart_2 | REUSE_INTERNAL | 5 (.v) | COPIED from v3 |
| spi_0 | REUSE_INTERNAL | 5 (.v) | COPIED from v3 |
| i2c_0 | REUSE_INTERNAL | 9 (.v) | COPIED from v3 |
| dshot_pwm | **CREATE** | 1 (.v) | REWRITTEN for v4 |
| gpio | REUSE_INTERNAL | 4 (.v) | COPIED from v3 |
| spi_flash_ctrl | REUSE_INTERNAL | 2 (.v) | COPIED from v3 |
| irq_ctrl | REUSE_INTERNAL | 1 (.v) | COPIED from v3 |
| timer | REUSE_INTERNAL | 4 (.v) | COPIED from v3 |
| watchdog | REUSE_INTERNAL | 4 (.v) | COPIED from v3 |
| caravel_wrapper | REUSE_GITHUB | 1 (.v) | RENAMED from caravel_bridge |
| clk_rst_mgr | REUSE_INTERNAL | 1 (.v) | COPIED from v3 |
| custom_timer | **CREATE** | 1 (.v) | NEW |
| drone_soc | TOP | 2 (.v) | drone_soc.v + wb_interconnect_bus.v |

---

### 2. Lint (Icarus Verilog + Verilator)

| Module | Iverilog | Verilator | Status | Log |
|--------|----------|-----------|--------|-----|
| ibex_core | 0E/0W | 0E/0W | PASS | rtl-ibex_core/logs/lint/ |
| wishbone_interconnect | 0E/0W | 0E/16W | PASS | rtl-wishbone_interconnect/logs/lint/ |
| sram_8kb | 0E/0W | 0E/11W | PASS | rtl-sram_8kb/logs/lint/ |
| uart_0 | 0E/2W | 0E/30W | PASS | rtl-uart_0/logs/lint/ |
| uart_1 | 0E/2W | 0E/30W | PASS | rtl-uart_1/logs/lint/ |
| uart_2 | 0E/2W | 0E/30W | PASS | rtl-uart_2/logs/lint/ |
| spi_0 | 0E/0W | 0E/0W | PASS | rtl-spi_0/logs/lint/ |
| i2c_0 | 0E/2W | 0E/30W | PASS | rtl-i2c_0/logs/lint/ |
| dshot_pwm | 0E/0W | 0E/6W | PASS | rtl-dshot_pwm/logs/lint/ |
| gpio | 0E/0W | 0E/0W | PASS | rtl-gpio/logs/lint/ |
| spi_flash_ctrl | 0E/0W | 0E/17W | PASS | rtl-spi_flash_ctrl/logs/lint/ |
| irq_ctrl | 0E/0W | 0E/3W | PASS | rtl-irq_ctrl/logs/lint/ |
| timer | 0E/0W | 0E/0W | PASS | rtl-timer/logs/lint/ |
| watchdog | 0E/0W | 0E/11W | PASS | rtl-watchdog/logs/lint/ |
| caravel_wrapper | 0E/0W | 0E/4W | PASS | rtl-caravel_wrapper/logs/lint/ |
| clk_rst_mgr | 0E/0W | 0E/3W | PASS | rtl-clk_rst_mgr/logs/lint/ |
| custom_timer | 0E/0W | 0E/0W | PASS | rtl-custom_timer/logs/lint/ |
| drone_soc | 1E/— | — | FAIL | rtl-drone_soc/logs/lint/drone_soc_iverilog.log |

**Lint: 17/18 PASS. drone_soc: FAIL — sram_8kb duplicate module error (rtl-drone_soc/logs/lint/drone_soc_iverilog.log:8-9). Non-blocking for synthesis (synth uses blackbox-only).**

---

### 3. Formal Verification (BMC, sby + bitwuzla)

**IMPORTANT: All formal XMLs report tests="0" — zero proof obligations were executed.**
The .sby configs declare BMC depth 25 but the RTL contains no SVA assertions. SymbiYosys built models but proved nothing. This is the same across all 16 modules that have formal artifacts.

| Module | BMC Depth | XML tests | Status | Notes |
|--------|-----------|-----------|--------|-------|
| ibex_core | 25 | 0 | BLOCKED | No assertions in RTL |
| wishbone_interconnect | 25 | 0 | BLOCKED | No assertions in RTL |
| sram_8kb | — | — | BLOCKED | Blackbox — no formal possible |
| uart_0 | 25 | 0 | BLOCKED | No assertions in RTL |
| uart_1 | 25 | 0 | BLOCKED | No assertions in RTL |
| uart_2 | 25 | 0 | BLOCKED | No assertions in RTL |
| spi_0 | 25 | 0 | BLOCKED | No assertions in RTL |
| i2c_0 | 25 | 0 | BLOCKED | No assertions in RTL |
| dshot_pwm | 25 | 0 | BLOCKED | No assertions in RTL |
| gpio | 25 | 0 | BLOCKED | No assertions in RTL |
| spi_flash_ctrl | 25 | 0 | BLOCKED | No assertions in RTL |
| irq_ctrl | 25 | 0 | BLOCKED | No assertions in RTL |
| timer | 25 | 0 | BLOCKED | No assertions in RTL |
| watchdog | 25 | 0 | BLOCKED | No assertions in RTL |
| caravel_wrapper | 25 | 0 | BLOCKED | No assertions in RTL |
| clk_rst_mgr | 25 | 0 | BLOCKED | No assertions in RTL |
| custom_timer | 25 | 0 | BLOCKED | No assertions in RTL |
| drone_soc | — | — | BLOCKED | No formal artifacts |

**Formal: 0/18 PASS. BLOCKED — RTL needs SVA assertions before formal can prove anything.**

---

### 4. Synthesis (Yosys + sky130_fd_sc_hd)

| Module | Cells | Area (um2) | Status | Log |
|--------|-------|-----------|--------|-----|
| ibex_core | 3,534 | 73,478 | PASS | rtl-ibex_core/logs/synth/ibex_core_synth.log |
| wishbone_interconnect | 699 | 5,674 | PASS | rtl-wishbone_interconnect/logs/synth/ |
| sram_8kb | 0 | — | PASS (BLACKBOX) | rtl-sram_8kb/logs/synth/sram_8kb_synth.log |
| uart_0 | 252 | 23,173 | PASS | rtl-uart_0/logs/synth/uart_0_synth.log |
| uart_1 | 252 | 23,173 | PASS | rtl-uart_1/logs/synth/uart_1_synth.log |
| uart_2 | 252 | 23,173 | PASS | rtl-uart_2/logs/synth/uart_2_synth.log |
| spi_0 | 1,116 | 15,819 | PASS | rtl-spi_0/logs/synth/spi_0_synth.log |
| i2c_0 | 2,141 | 29,312 | PASS | rtl-i2c_0/logs/synth/i2c_0_synth.log |
| dshot_pwm | 2,254 | 20,577 | PASS | rtl-dshot_pwm/logs/synth/dshot_pwm_synth.log |
| gpio | 593 | 6,226 | PASS | rtl-gpio/logs/synth/gpio_synth.log |
| spi_flash_ctrl | 377 | 4,330 | PASS | rtl-spi_flash_ctrl/logs/synth/spi_flash_ctrl_synth.log |
| irq_ctrl | 396 | 4,743 | PASS | rtl-irq_ctrl/logs/synth/irq_ctrl_synth.log |
| timer | 1,766 | 15,769 | PASS | rtl-timer/logs/synth/timer_synth.log |
| watchdog | 364 | 3,749 | PASS | rtl-watchdog/logs/synth/watchdog_synth.log |
| caravel_wrapper | 199 | 3,585 | PASS | rtl-caravel_wrapper/logs/synth/caravel_wrapper_synth.log |
| clk_rst_mgr | 44 | 533 | PASS | rtl-clk_rst_mgr/logs/synth/clk_rst_mgr_synth.log |
| custom_timer | 1,875 | 19,788 | PASS | rtl-custom_timer/logs/synth/custom_timer_synth.log |
| drone_soc (top) | 19,305 | 272,181 | PASS | rtl-drone_soc/logs/synth/drone_soc_synth.log |

**Synthesis: 18/18 PASS (0 latches, 0 unmapped cells). drone_soc: 19,305 sky130 cells, 272,181 um2 total.**

---

### 5. Equivalence Checking

| Module | Status | Log |
|--------|--------|-----|
| ibex_core | PASS (3426/3426 proven) | rtl-ibex_core/equiv_check/equiv.log |
| wishbone_interconnect | PASS (1048/1048 proven) | rtl-wishbone_interconnect/equiv_check/equiv.log |
| clk_rst_mgr | PASS (44/44 proven) | rtl-clk_rst_mgr/equiv_check/equiv.log |
| dshot_pwm | PASS (418/418 proven) | rtl-dshot_pwm/equiv_check/equiv.log |
| irq_ctrl | PASS (116/116 proven) | rtl-irq_ctrl/equiv_check/equiv.log |
| spi_flash_ctrl | PASS (118/118 proven) | rtl-spi_flash_ctrl/equiv_check/equiv.log |
| uart_0 | FAIL (wrapper top not found) | rtl-uart_0/equiv_check/equiv.log |
| uart_1 | FAIL (wrapper top not found) | rtl-uart_1/equiv_check/equiv.log |
| uart_2 | FAIL (wrapper top not found) | rtl-uart_2/equiv_check/equiv.log |
| spi_0 | FAIL (wrapper top not found) | rtl-spi_0/equiv_check/equiv.log |
| i2c_0 | FAIL (wrapper top not found) | rtl-i2c_0/equiv_check/equiv.log |
| gpio | FAIL (wrapper top not found) | rtl-gpio/equiv_check/equiv.log |
| timer | FAIL (wrapper top not found) | rtl-timer/equiv_check/equiv.log |
| watchdog | FAIL (wrapper top not found) | rtl-watchdog/equiv_check/equiv.log |
| caravel_wrapper | FAIL (script references v3 path) | rtl-caravel_wrapper/equiv_check/equiv.log |
| sram_8kb | FAIL (blackbox — no gate module) | rtl-sram_8kb/equiv_check/equiv.log |
| custom_timer | NOT RUN | — |
| drone_soc | NOT RUN | — |

**Equiv: 6/18 PASS. 10 modules blocked by wrapper-module name resolution in equiv scripts. 2 modules not yet scripted.**

---

### 6. Verdict

**FAIL** — 6 of 18 modules pass equivalence checking. Formal verification produces zero proof obligations (tests=0 across all 16 XMLs). drone_soc lint has a duplicate-module error.

| Gate | Result |
|------|--------|
| RTL Authoring | 18/18 |
| Lint | 17/18 PASS |
| Formal (BMC) | 0/18 — BLOCKED (no assertions) |
| Synthesis | 18/18 PASS |
| Equivalence | 6/18 PASS |
| Top Integration | PASS (drone_soc synth: 19,305 cells) |

---

### 7. Run Metadata
- Tool versions: Yosys 0.65+71, Icarus 14.0, Verilator 5.049, sby 0.64
- PDK: sky130B sky130_fd_sc_hd__tt_025C_1v80.lib
- Clock: 16.67 MHz (60 ns period)
- Session: kanban task t_6ef7f210, run #25, 2026-07-19
