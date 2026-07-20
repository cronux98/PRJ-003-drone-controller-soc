---
cost:
  stage: "02_specification_stage"
  agent: "spec-product-engineer"
  model: "mimo-v2.5-pro"
  token:
    input: 0
    output: 0
    total: 0
  cost_usd:
    input: 0.0
    output: 0.0
    total: 0.0
  wall_clock: ""
  iterations: 1
  api_calls: 0
  model_pricing_ref: "~/hermes_workspace/config/model_pricing.yaml"
---

# Project Specification — IP-010 v4: Drone Controller SoC

**STATUS: COMPLETE — derived from v3 spec + v4 BA reports (01_business_stage/)**

## 1. Project Identity

| Field | Value | Required |
|---|---|---|
| Project Name | Drone Controller SoC | Yes |
| Project ID | IP-010 | Auto |
| Version | v4 | Auto |
| Description | Open-source RISC-V flight controller ASIC for drone stabilization and motor control, fabricated on sky130A via Efabless Caravel MPW. v4 carries forward frequency to 16.67 MHz (measured STA), uses real sky130 SRAM macro, and fixes pad mapping. | Yes |
| Target Application | Nano/micro racing drone flight controller — rate-mode stabilization, motor PWM (DShot + standard), IMU sensor fusion, GPS/telemetry UART connectivity | Yes |
| **Project Type** | **soc** | **Yes** |

**Source documents:**
- `01_business_stage/market_validation.md` — PASS
- `01_business_stage/market_requirements.md` — MoSCoW feature classification
- `01_business_stage/competitive_analysis.md` — 5 comparables, gap analysis
- `01_business_stage/domain_report.md` — domain overview, standards, metrics
- `01_business_stage/baseline_metrics.json` — PPA baselines, feature baselines
- `../v3/02_specification_stage/spec_plan.md` — v2 baseline specification

**v4 Changes from v3:**
1. Frequency re-baselined to 16.67 MHz (measured STA closure from v2 synthesis) — eliminates timing risk
2. SRAM uses real sky130 macro (sram_8kb, not dummy) — proven silicon
3. Pad mapping fixed: I2C [10:11], DShot [15:12] — no I/O overlap
4. Power budget relaxed: ≤100 mW active (conservative for 16.67 MHz)
5. All timing calculations updated for 16.67 MHz clock

---

## 2. Instruction Set Architecture (ISA)

| Field | Value | Required | Default |
|---|---|---|---|
| ISA | RV32IMC | Yes | RV32I |
| Privilege Modes | Machine only | No | Machine only |
| CSRs | Standard RV32IMC CSRs (mstatus, mie, mip, mtvec, mcause, mepc, mtval) | No | Standard RV32I CSRs |
| Custom Instructions | None | No | None |

**Rationale:** Ibex "maxperf" configuration supports RV32IMC with 1-cycle multiply (3.13 CoreMark/MHz). The M-extension (hardware multiply/divide) is essential for fixed-point PID control math and sensor fusion. C-extension reduces code size — beneficial for 8KB SRAM to maximize firmware density.

---

## 3. Process & Technology

| Field | Value | Required | Default |
|---|---|---|---|
| PDK | sky130A (SKY130A, 130nm) | No | sky130hd |
| Target Frequency | 16.67 MHz (measured STA closure from v2) | No | 50 MHz |
| Target Area | ≤10 mm² (Caravel user area: 2.92 × 3.52 mm) | No | Unconstrained |
| Supply Voltage | 1.8V core / 3.3V I/O (sky130A PDK nominal) | No | PDK nominal |

**Source:** `baseline_metrics.json` PPA baselines. v3 uses 16.67 MHz — the measured STA closure frequency from v2 synthesis. This is conservative and guarantees timing closure. OpenTitan EarlGrey demonstrated 100 MHz Ibex on sky130A (same process, 6x frequency target). Ibex alone: ~0.15-0.25 mm² per lowRISC benchmarks.

---

## 4. Peripherals & Interfaces

### MUST (from market_requirements.md)

| Peripheral | Required | Config | Notes |
|---|---|---|---|
| UART x3 | Yes | 115200 baud min, 8N1, TX+RX, full-duplex. Port 1: SBUS-capable (inverted, 100k baud). Port 2: CRSF 420k baud capable. | FOSSi EF_UART (REUSE). 3 instances: GPS, RX, telemetry/debug. At 16.67 MHz: 144 ticks/bit @ 115200 baud. |
| SPI controller x1 | Yes | Master mode, 8+ MHz capable, continuous IMU reads | FOSSi EF_SPI (REUSE). ICM-42688-P IMU. At 16.67 MHz: SPI clock = sysclk/2 = 8.335 MHz. |
| I2C controller x1 | Yes | Master mode, 100 kHz standard, 400 kHz fast mode preferred | FOSSi EF_I2C (REUSE). Barometer (BMP280) + magnetometer (QMC5883L). At 16.67 MHz: fast mode divider = 42. |
| PWM (DShot + standard) x6 | Yes | 4× DShot 300 capable (300 kbps single-wire, ±2% timing accuracy). 2× standard 50-400Hz PWM. Glitch-free duty cycle updates. | **CREATE — custom DShot PWM timer.** At 16.67 MHz: 55.5 cycles/bit for DShot 300 — adequate with hardware timer. |
| GPIO x8 | Yes | 8 interrupt-capable pins, <10 µs edge-to-ISR latency | FOSSi EF_GPIO (REUSE). Buzzer, LED, arming switch, failsafe. Pad mapping: GPIO [0:7]. |
| SPI Flash controller | Yes | Standard SPI flash commands (read, fast read), XIP or cached execution | FOSSi EF_SPI (REUSE) — extended for flash command set. External flash: W25Q32JV 4MB. |
| Interrupt controller | Yes | Simple pending/enable, priority-based routing | FOSSi EF_IRQ (REUSE). |
| Timer | Yes | 32-bit, auto-reload, input capture for RPM telemetry | FOSSi EF_TIMER (REUSE). |
| Watchdog timer | Yes | 32-bit, interrupt + reset | FOSSi EF_WATCHDOG (REUSE). Safety requirement — resets FC if control loop hangs. |
| System SRAM | Yes | 8KB (2048×32-bit), zero wait states, single-cycle reads, Wishbone B4 slave | REUSE sram_8kb (real sky130 macro). Behavioral model for RTL sim, BLACKBOX for synth/PD. |

### SHOULD (market_requirements.md)

| Peripheral | Required | Config | Notes |
|---|---|---|---|
| UART x4 (add VTX control) | No | SmartAudio/Tramp protocol compatible | Additional EF_UART instance |
| SPI x2 (blackbox logging) | No | Dedicated SPI flash for data logging | Additional EF_SPI instance |
| PWM channels: 8 total | No | 6 DShot + 2 PWM | Extend DShot PWM timer channel count |
| GPIO expandability to 12+ | No | Additional aux functions | Extend EF_GPIO |

### COULD (market_requirements.md)

| Peripheral | Required | Config | Notes |
|---|---|---|---|
| PWM input capture (SBUS) | No | Eliminate external inverter for SBUS | EF_TIMER input capture |
| I2C x2 (separate buses) | No | Avoid speed contention baro/mag | Additional EF_I2C instance |
| ADC input 2-4 channels | No | Battery V/I monitoring for OSD | Custom — sky130A has no embedded ADC in open PDK; external ADC via I2C |
| Hardware CRC for DShot | No | Verify DShot frames in hardware | Extend DShot PWM timer |
| Debug module | No | JTAG via Caravel debug infrastructure | Caravel-provided |

### WON'T (explicitly excluded, from baseline_metrics.json + market_requirements.md)

| Feature | Rationale |
|---|---|
| FPU (hardware floating-point) | Ibex does not include FPU. Fixed-point PID sufficient. |
| On-chip flash memory | sky130A open PDK has no embedded flash. External SPI flash standard. |
| WiFi / BLE radio | RF IP not available. External module via UART. |
| USB PHY (full-speed) | Caravel provides USB-UART bridge. |
| Hardware crypto accelerator | Not needed for hobbyist drone FC. |
| Camera interface (DCMI) | Outside scope. |
| CAN bus controller | Not required for hobbyist drone ecosystem. v4 candidate. |
| Full Betaflight support | 16.67 MHz + 8KB SRAM insufficient for full Betaflight. Target: minimal flight firmware stack. |

---

## 5. Memory Architecture

| Field | Value | Required | Default |
|---|---|---|---|
| Instruction Memory | 8KB shared with data (Von Neumann) | No | 64 KB |
| Data Memory | 8KB shared with instruction | No | 64 KB |
| Memory Type | SRAM (sram_8kb — real sky130 macro, 2048×32-bit, behavioral for RTL sim, BLACKBOX for synth/PD) | No | SRAM |
| Boot Address | 0x0000_0000 (Caravel management SoC handles initial boot) | No | 0x0000_0000 |
| Memory Map | Auto-generated, see system_plan.md | No | Auto-generated |
| Harvard / Von Neumann | Von Neumann (unified 8KB SRAM) | No | Harvard |
| External Storage | SPI flash (W25Q32JV 4MB) for firmware + data logging | Yes | — |

**Rationale:** 8KB SRAM (real sky130 macro) is proven silicon. Von Neumann maximizes flexibility for dynamic allocation between code and data. With 8KB, the firmware can support multi-mode flight profiles, cached PID loops, larger IMU data buffers, and more complex sensor fusion. Execute-in-place from SPI flash with hot loops cached in SRAM. The C-extension (RV32IMC) further maximizes code density within 8KB.

**v4 improvement:** SRAM uses real sky130 macro (not dummy). Proven silicon eliminates SRAM integration risk.

---

## 6. Bus Architecture

| Field | Value | Required | Default |
|---|---|---|---|
| Bus Protocol | Wishbone B4 (shared bus) | No | APB |
| Bus Width | 32-bit | No | 32-bit |
| Address Width | 32-bit | No | 32 |
| Endianness | Little | No | Little |

**Rationale:** Wishbone B4 is FOSSi ecosystem standard. Compatible with all EF_* IP blocks (EF_UART, EF_SPI, EF_I2C, EF_GPIO, EF_TIMER, EF_WATCHDOG). Ibex supports Wishbone via its LSU interface. Shared bus topology (<4 bus masters expected).

---

## 7. Clock & Reset

| Field | Value | Required | Default |
|---|---|---|---|
| Clock Domains | Single | No | Single |
| Clock Source | External crystal (via Caravel clock input) | No | External |
| Target Frequency | 16.67 MHz (measured STA closure from v2) | No | 50 MHz |
| Reset Type | Async assert, sync deassert | No | Async assert, sync deassert |
| Reset Vector | 0x0000_0000 | No | 0x0000_0000 |

**Rationale:** Single clock domain simplifies timing closure on sky130A. 16.67 MHz is the measured STA closure frequency from v2 — conservative and guaranteed. If DShot PWM requires a separate high-speed timer clock, a clock divider from the main domain is used — no CDC needed. Caravel provides clock and reset management.

**Timing at 16.67 MHz:**
- Clock period: 60 ns
- DShot 300: 55.5 cycles/bit (3.33 µs / 60 ns) — adequate
- UART 115200: 144 ticks/bit
- SPI: sysclk/2 = 8.335 MHz
- I2C fast mode: divider = 42

---

## 8. Power

| Field | Value | Required | Default |
|---|---|---|---|
| Power Budget | ≤100 mW active (SoC only) | No | Unconstrained |
| Power Domains | Single | No | Single |
| Clock Gating | Yes (on idle peripherals) | No | No |
| Power States | Active / Idle (clock-gated) | No | Active only |

**Source:** `baseline_metrics.json` — conservative = 100 mW. At 16.67 MHz on sky130A, power is ~10-20 mW for core logic, ~50-75 mW total with SRAM and peripherals. ≤100 mW is conservative. Clock gating reduces power when peripherals are idle.

---

## 9. Verification Requirements

| Field | Value | Required | Default |
|---|---|---|---|
| Verification Method | Simulation + Formal | No | Both |
| Coverage Target | 95% functional coverage | No | 95% |
| Directed Tests | All ISA instructions (RV32IMC), all peripheral register R/W, DShot frame generation, PWM timing, SPI flash read, UART loopback | No | All ISA instructions |
| Random Tests | 1000 random sequences | No | 1000 |
| Golden Model | Python behavioral models for all peripherals + Ibex instruction-accurate model | No | Yes |
| Formal Properties | SymbiYosys BMC + Induction for custom DShot state machine | No | Yes |
| Integration Gate | Caravel mpw-precheck PASS | Yes | — |

**Source:** `market_validation.md` Conditions. Verification staged: (1) Ibex + UART + GPIO in user_project_wrapper → mpw-precheck. (2) Incrementally add SPI, I2C, PWM. (3) Full peripheral set final integration.

---

## 10. Physical Design Targets

| Field | Value | Required | Default |
|---|---|---|---|
| Utilization Target | 60% | No | 60% |
| DRC Clean | Zero violations required | No | Yes |
| LVS Clean | Netlist match required | No | Yes |
| Max Wire Length | PDK default | No | PDK default |
| Toolchain | OpenLANE (RTL→GDS) | Yes | — |
| Fabrication Target | Efabless chipIgnite MPW shuttle (sky130A) | Yes | — |

**Physical Design Feasibility (per asic-planning skill §3 requirement):**

| Metric | Value | Source |
|---|---|---|
| Reference ORFS examples | OpenTitan EarlGrey (100 MHz Ibex on sky130A) | OpenTitan synthesis reports |
| Estimated cell count | ~15K cells (Ibex) + ~5K cells (peripherals + Wishbone) + real SRAM macro ≈ 22K cells | Ibex benchmarks, FOSSi peripheral estimates |
| Interface complexity | Low — Wishbone B4 shared bus, single clock domain. External bus interfaces wrap the core, not synthesized into it. | Compatible with stock ORFS flows |
| Memory approach | sram_8kb real sky130 macro (proven silicon). External SPI flash (off-chip). No hardcoded boot ROM — firmware loaded via Caravel management SoC. | Follows ORFS best practices |
| Risk flags | DShot custom RTL is the only non-standard block. SRAM is real macro — no DFF array risk. | Per Condition 1 validation |

**Risk assessment:** Ibex (15K cells) + peripherals (5K) + real SRAM macro = ~22K cells estimated. The real SRAM macro eliminates the 107K DFF cell risk from v2. The custom DShot timer is the primary RTL unknown.

---

## 11. Constraints & Special Requirements

| Field | Value |
|---|---|
| Timing Constraints | DShot 300: 3.33 µs per bit (±2% accuracy). At 16.67 MHz (60 ns tick): ~55 ticks per bit — adequate resolution. PWM glitch-free during duty cycle update (atomic register write). |
| Area Constraints | Caravel user_area: 2.92 × 3.52 mm (10.28 mm²). Utilization ≤60%. |
| Test Constraints | JTAG access via Caravel debug infrastructure. Scan chain for production test (Caravel-provided). |
| Compliance | Caravel mpw-precheck (DRC, LVS, timing). Wishbone B4 spec compliance. DShot protocol specification compliance. |
| 8KB SRAM Budget | 8KB (2048×32-bit) unified SRAM — adequate for multi-mode flight, cached PID loops, and larger IMU buffers. |
| DShot Timer Spec | Condition 5 — DShot timer specification required before RTL begins (see §11.1 below). |
| Frequency Gate | v3: 16.67 MHz is measured STA closure — no further validation needed. |
| Integration Gate | Caravel mpw-precheck with incremental peripheral integration. |
| Pad Mapping | I2C [10:11], DShot [15:12] — no I/O overlap (v4 baseline (inherited from v3)). |

### 11.1 DShot Timer Specification (Condition 5 — PRELIMINARY)

**Protocol:** DShot 300 (300 kbps digital ESC protocol)
**Bit timing:** 3.33 µs per bit. At 16.67 MHz: ~55.5 cycles/bit (60 ns resolution).
**T0H = 1250 ns (~21 cycles), T0L = 2083 ns (~35 cycles). T1H = 2500 ns (~42 cycles), T1L = 833 ns (~14 cycles).**
**Frame format:** 16 bits per frame: 11-bit throttle (0-2047) + 1-bit telemetry request + 4-bit CRC
**CRC polynomial:** CRC-4 = x⁴ + x³ + x² + 1 (polynomial 0x1D)
**Telemetry:** Bidirectional mode: ESC responds with telemetry data on same wire after DShot frame
**Hardware requirements:**
- Timer resolution: 60 ns (16.67 MHz) → ~55 ticks per DShot bit — adequate
- State machine: idle → bit0 → bit1 → ... → bit15 → idle
- Atomic PWM duty cycle update (no glitch during update)
- 4 independent DShot channels + 2 standard PWM channels
- Pad mapping: DShot outputs on GPIO [15:12]

**Reference:** Betaflight DShot implementation (GPLv3), DShot protocol specification (flyduino/DSHOT).

---

## 12. Module Inventory

Based on Sections 4-6, the system comprises the following modules:

| # | Module | Description | Source | Classification |
|---|---|---|---|---|
| 1 | ibex_core | lowRISC Ibex RV32IMC "maxperf" processor core | REUSE: lowRISC/Ibex GitHub | REUSE_INTERNAL |
| 2 | wishbone_interconnect | Wishbone B4 shared bus fabric, 1 master, N slaves | REUSE: FOSSi wishbone-intercon | REUSE_INTERNAL |
| 3 | sram_8kb | 8KB SRAM (2048×32-bit), real sky130 macro, zero-wait-state | REUSE: real sky130 SRAM macro | REUSE_INTERNAL |
| 4 | uart_0 | UART controller — GPS (115200 baud) | REUSE: FOSSi EF_UART | REUSE_INTERNAL |
| 5 | uart_1 | UART controller — RC receiver, CRSF 420k baud, SBUS inverted | REUSE: FOSSi EF_UART | REUSE_INTERNAL |
| 6 | uart_2 | UART controller — telemetry/debug (115200 baud) | REUSE: FOSSi EF_UART | REUSE_INTERNAL |
| 7 | spi_0 | SPI master controller — IMU sensor (8.335 MHz at 16.67 MHz sysclk/2) | REUSE: FOSSi EF_SPI | REUSE_INTERNAL |
| 8 | i2c_0 | I2C master controller — barometer + magnetometer (100/400 kHz) | REUSE: FOSSi EF_I2C | REUSE_INTERNAL |
| 9 | dshot_pwm | DShot 300 PWM timer — 4 DShot channels + 2 standard PWM | **CREATE** (extend FOSSi EF_TIMER) | CREATE |
| 10 | gpio | 8 interrupt-capable GPIO pins, <10 µs ISR latency | REUSE: FOSSi EF_GPIO | REUSE_INTERNAL |
| 11 | spi_flash_ctrl | SPI flash controller — external W25Q32JV firmware storage, XIP | REUSE: FOSSi EF_SPI (flash-extended) | REUSE_INTERNAL |
| 12 | irq_ctrl | Interrupt controller — pending/enable/priority, 16 source lines | REUSE: FOSSi EF_IRQ | REUSE_INTERNAL |
| 13 | timer | 32-bit auto-reload timer with input capture (RPM telemetry) | REUSE: FOSSi EF_TIMER | REUSE_INTERNAL |
| 14 | watchdog | 32-bit watchdog timer — interrupt + reset on timeout | REUSE: FOSSi EF_WATCHDOG | REUSE_INTERNAL |
| 15 | caravel_wrapper | Caravel user_project_wrapper with Wishbone-to-Wishbone bridge | REUSE: Efabless Caravel template | REUSE_GITHUB |
| 16 | clk_rst_mgr | Clock divider + reset synchronizer | REUSE: FOSSi clock-reset-gen | REUSE_INTERNAL |
| 17 | custom_timer | Custom timer extensions for DShot + RPM telemetry | **CREATE** (extend EF_TIMER) | CREATE |

**Classification summary:**
- REUSE_INTERNAL: 13 modules (existing FOSSi IP or prior project reuse)
- REUSE_GITHUB: 1 module (Caravel template)
- CREATE: 2 modules (dshot_pwm, custom_timer)
- **Total: 17 modules | REUSE: 15 | CREATE: 2 | Reuse ratio: 15/17 = 0.882**

**REUSE/CREATE classification rule:** A module is REUSE if a pre-qualified IP block exists with matching functionality and bus interface. A module is CREATE if no matching IP exists or if significant extension is required (e.g., DShot protocol hardware not in FOSSi library).

---

## REQ-ID Index (autogenerated — Requirements Traceability)

Every normative requirement in this specification is tagged with a unique REQ-IP010-NNN identifier. See `traceability_matrix.md` for the full traceability matrix with owning modules and verification methods.

| REQ-ID | Summary | § | Module |
|---|---|---|---|
| REQ-IP010-001 | Project shall be named Drone Controller SoC and assigned IP-010 | §1 | top |
| REQ-IP010-002 | SoC shall target nano/micro racing drone flight controller application | §1 | top |
| REQ-IP010-003 | Project type shall be SoC (System-on-Chip) | §1 | top |
| REQ-IP010-004 | Core shall implement RV32IMC ISA with M-extension + C-extension | §2 | ibex_core |
| REQ-IP010-005 | Core shall operate in Machine-only privilege mode | §2 | ibex_core |
| REQ-IP010-006 | Core shall implement standard RV32IMC CSRs | §2 | ibex_core |
| REQ-IP010-007 | Core shall use Ibex "maxperf" configuration (1-cycle multiply) | §2 | ibex_core |
| REQ-IP010-008 | Design shall target sky130A (SKY130A, 130nm) PDK | §3 | top |
| REQ-IP010-009 | Target operating frequency shall be 16.67 MHz (measured STA closure) | §3 | top |
| REQ-IP010-010 | Design area shall not exceed 10 mm² | §3 | top |
| REQ-IP010-011 | Supply voltage shall be 1.8V core / 3.3V I/O | §3 | top |
| REQ-IP010-012 | SoC shall include 3 UART controllers (GPS, RC receiver, telemetry) | §4 | uart_0, uart_1, uart_2 |
| REQ-IP010-013 | SoC shall include 1 SPI master controller (8+ MHz at 16.67 MHz sysclk/2) | §4 | spi_0 |
| REQ-IP010-014 | SoC shall include 1 I2C master controller (100/400 kHz) | §4 | i2c_0 |
| REQ-IP010-015 | SoC shall include DShot PWM controller (4× DShot 300 + 2× PWM) | §4 | dshot_pwm |
| REQ-IP010-016 | SoC shall include 8 interrupt-capable GPIO pins (<10 µs ISR latency) | §4 | gpio |
| REQ-IP010-017 | SoC shall include SPI flash controller (W25Q32JV 4MB, XIP) | §4 | spi_flash_ctrl |
| REQ-IP010-018 | SoC shall include interrupt controller (16 sources, priority routing) | §4 | irq_ctrl |
| REQ-IP010-019 | SoC shall include 32-bit auto-reload timer with input capture | §4 | timer |
| REQ-IP010-020 | SoC shall include 32-bit watchdog timer (pre-warning + reset) | §4 | watchdog |
| REQ-IP010-021 | Memory architecture shall be Von Neumann (unified 8KB SRAM) | §5 | sram_8kb |
| REQ-IP010-022 | Boot address shall be 0x0000_0000 with Caravel firmware loading | §5 | caravel_bridge, ibex_core |
| REQ-IP010-023 | External storage shall be SPI flash (W25Q32JV 4MB) | §5 | spi_flash_ctrl |
| REQ-IP010-024 | Bus protocol shall be Wishbone B4 (32-bit, little-endian) | §6 | wishbone_interconnect |
| REQ-IP010-025 | Bus topology shall be shared bus (1 master, ≤14 slaves) | §6 | wishbone_interconnect |
| REQ-IP010-026 | SoC shall use single clock domain at 16.67 MHz (Caravel user_clock) | §7 | clk_rst_mgr |
| REQ-IP010-027 | Reset shall be async assert, sync deassert (2-stage synchronizer) | §7 | clk_rst_mgr |
| REQ-IP010-028 | Active power budget shall not exceed 100 mW (SoC only) | §8 | top |
| REQ-IP010-029 | Clock gating shall be implemented on idle peripherals | §8 | clk_rst_mgr, all peripherals |
| REQ-IP010-030 | Verification shall use simulation + formal (95% coverage target) | §9 | all modules |
| REQ-IP010-031 | Directed tests shall cover all ISA instructions + peripheral R/W | §9 | all modules |
| REQ-IP010-032 | Random tests shall include 1000 random sequences minimum | §9 | all modules |
| REQ-IP010-033 | Golden model shall provide Python behavioral models for all peripherals | §9 | all modules |
| REQ-IP010-034 | Formal properties for DShot state machine (SymbiYosys BMC+Induction) | §9 | dshot_pwm |
| REQ-IP010-035 | Integration gate: Caravel mpw-precheck PASS | §9 | caravel_wrapper |
| REQ-IP010-036 | Physical design: 60% utilization, zero DRC/LVS violations | §10 | top |
| REQ-IP010-037 | RTL-to-GDS flow shall use OpenLANE toolchain | §10 | top |
| REQ-IP010-038 | Fabrication target: Efabless chipIgnite MPW shuttle (sky130A) | §10 | top |
| REQ-IP010-039 | Estimated cell count: ~22K cells (Ibex 15K + peripherals 5K + SRAM macro) | §10 | top |
| REQ-IP010-040 | DShot 300 timing: 3.33 µs/bit, ±2% accuracy, 55.5 cycles/bit at 16.67 MHz | §11 | dshot_pwm |
| REQ-IP010-041 | PWM duty cycle updates shall be atomic (double-buffered registers) | §11 | dshot_pwm |
| REQ-IP010-042 | DShot CRC: CRC-4 polynomial x⁴+x³+x²+1 (0x1D) | §11 | dshot_pwm |
| REQ-IP010-043 | Firmware shall fit in 8KB SRAM (validated with C model before RTL) | §11 | ibex_core, sram_8kb |
| REQ-IP010-044 | Frequency target: 16.67 MHz measured STA closure (v4 — no further validation needed) | §11 | top |
| REQ-IP010-045 | Design shall comply with Wishbone B4 specification | §11 | wishbone_interconnect |
| REQ-IP010-046 | Design shall pass Caravel mpw-precheck (DRC, LVS, timing) | §11 | caravel_wrapper |
| REQ-IP010-047 | SoC shall instantiate ibex_core (lowRISC Ibex RV32IMC "maxperf") | §12 | ibex_core |
| REQ-IP010-048 | SoC shall instantiate wishbone_interconnect (shared bus fabric) | §12 | wishbone_interconnect |
| REQ-IP010-049 | SoC shall instantiate sram_8kb (8KB SRAM, real sky130 macro) | §12 | sram_8kb |
| REQ-IP010-050 | SoC shall instantiate dshot_pwm (custom DShot 300 + PWM timer) | §12 | dshot_pwm |
| REQ-IP010-051 | SoC shall instantiate caravel_wrapper (user_project_wrapper + bridge) | §12 | caravel_wrapper |
| REQ-IP010-052 | SoC shall instantiate clk_rst_mgr (clock divider + reset sync) | §12 | clk_rst_mgr |
| REQ-IP010-053 | Pad mapping: I2C [10:11], DShot [15:12] — no I/O overlap | §12 | caravel_wrapper |

**Total: 53 requirements tagged.**

## Notes

- Fields marked `Required` in the template were answered from BA reports — none are left blank.
- Fields marked `Default` were filled with documented defaults from `spec-template.md` or overridden per BA report evidence.
- The DShot PWM timer (CREATE) is the only novel RTL block. Condition 5 requires a full DShot timer spec before RTL begins.
- This spec is COMPLETE, derived from v3 spec + v4 BA reports.
- **v4 key changes:** Frequency re-baselined to 16.67 MHz (measured STA), real sky130 SRAM macro, clean pad mapping.
- **Anti-fabrication:** sram_8kb uses behavioral model for RTL sim, BLACKBOX for synth/PD (integrity verification).