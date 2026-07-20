# Third-Party Components

This project integrates open-source hardware IP from multiple sources. Each component retains its original license. This file documents attribution as required by those licenses.

## RISC-V Core

**Component:** Ibex RISC-V Core (RV32IMC)
**Source:** lowRISC — https://github.com/lowRISC/ibex
**License:** Apache 2.0
**Copyright:** lowRISC contributors, ETH Zürich, University of Bologna
**Files:** `04_frontend_stage/rtl-ibex_core/rtl/*.v`

## SRAM Macro

**Component:** OpenRAM Sky130 SRAM (8 KB, sram_1rw1r_32_256_8_sky130)
**Source:** OpenRAM Project — https://github.com/VLSIDA/OpenRAM
**License:** BSD 3-Clause
**Files:** `08_backend_stage/macros/sram_8kb/`

## Caravel Harness

**Component:** Caravel SoC Harness (user_project_wrapper)
**Source:** Efabless — https://github.com/efabless/caravel_user_project
**License:** Apache 2.0
**Files:** `09_caravel_stage/caravel_wrapper/`

## Efabless IP Library

The following peripheral IP blocks are from the Efabless IP library:

| Block | Source File | License |
|-------|-------------|---------|
| EF_UART | `EF_UART.v`, `EF_UART_WB.v`, `EF_UART_WB_wrapper.v` | Apache 2.0 |
| EF_SPI | `EF_SPI.v`, `EF_SPI_WB_wrapper.v` | Apache 2.0 |
| EF_GPIO8 | `EF_GPIO8.v`, `EF_GPIO8_WB_wrapper.v` | Apache 2.0 |
| EF_TMR32 | `EF_TMR32.v`, `EF_TMR32_WB_wrapper.v` | Apache 2.0 |
| EF_WDT32 | `EF_WDT32.v`, `EF_WDT32_WB_wrapper.v` | Apache 2.0 |
| EF_I2C | `EF_I2C_WB_wrapper.v` | Apache 2.0 |

**Source:** Efabless IP — https://github.com/efabless/EF_IPs
**License:** Apache 2.0
**Copyright:** Efabless Corporation

## PDK

**Component:** SkyWater sky130_fd_sc_hd (130nm open-source PDK)
**Source:** SkyWater Technology / Google — https://github.com/google/skywater-pdk
**License:** Apache 2.0
**Files:** `04_frontend_stage/common/sky130_fd_sc_hd/`

## Toolchain

The following open-source EDA tools were used by the agentic framework (not distributed in this repository):

| Tool | Version | License |
|------|---------|---------|
| Yosys | 0.62 | ISC |
| OpenROAD | 2026-02-17 | BSD 3-Clause |
| Magic VLSI | 8.3.623 | MIT-style |
| Klayout | 0.30.7 | GPL |
| Netgen | 1.5.316 | GPL |
| Icarus Verilog | s20250103 | GPL |
| Verilator | 5.044 | LGPL |
| cocotb | 1.9.x | BSD 3-Clause |

## Framework

The agentic workflow that produced this chip uses the Hermes agent framework and the Vera ASIC orchestration system. No human wrote RTL, testbenches, SDC constraints, or invoked EDA tools — all design artifacts were produced autonomously by Claude Opus 4.8 subagents working from specification documents and project templates.

---

*If you believe any attribution is missing or incorrect, please open an issue.*
