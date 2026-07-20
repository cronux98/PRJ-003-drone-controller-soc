# Architecture — IP-010 v4: Drone Controller SoC

> **Tier:** Easy (v4 — rate-mode flight controller, 8KB SRAM)
> **PDK:** sky130_fd_sc_hd (sky130A)
> **Frequency:** 16.67 MHz (sys_clk, single domain — measured STA closure from v2)
> **Created:** 2026-07-19
> **Processor:** Ibex RV32IMC "maxperf" (2-stage, 3.13 CoreMark/MHz)
> **Bus:** Wishbone B4 shared (1 master, 14 slaves)
> **Memory:** 8KB unified Von Neumann SRAM (real sky130 macro)
> **Reuse Ratio:** 15/17 modules REUSE, 2 CREATE

**v4 Changes from v3:**
- Renamed caravel_wrapper → caravel_wrapper (consistent with spec)
- Added custom_timer module (CREATE) for DShot RPM telemetry extensions
- Updated all references from v3 → v4
- No architectural changes — v4 is a version bump from v3

---

## 1. Overview

IP-010 v4 is a drone flight controller SoC for the Caravel harness (sky130A). It runs a rate-mode PID control loop at ~4 kHz from 8KB of unified SRAM on an Ibex RV32IMC core. Sensor data arrives via SPI (IMU), I2C (barometer/magnetometer), and UART (GPS). Actuator commands go out over DShot 300 PWM (4 ESCs + 2 standard PWM). An RC receiver on a second UART provides pilot stick inputs. Telemetry streams out on a third UART. Firmware is stored off-chip in a 4 MB SPI NOR flash and loaded into SRAM by the Caravel management SoC at boot.

**Top-Level Block Diagram:** `block_diagrams/top_level.html`

**Key Specifications:**

| Spec | Value | Source |
|------|-------|--------|
| ISA | RV32IMC (I + M + C) | spec_plan.md §2 |
| Pipeline | 2-stage (IF → ID/EX) | spec_plan.md §2 |
| Bus | Wishbone B4 shared, 32-bit addr, 32-bit data | spec_plan.md §6 |
| Memory | 8KB unified SRAM (real sky130 macro), single-cycle | spec_plan.md §5 |
| Frequency | 16.67 MHz (sys_clk, single domain — measured STA) | spec_plan.md §3 |
| PDK | sky130_fd_sc_hd (sky130A) | spec_plan.md §3 |
| Peripherals | 3×UART, SPI, I2C, DShot PWM, GPIO, SPI flash, IRQ ctrl, timer, watchdog | spec_plan.md §4 |
| Interrupts | 13 sources, 4 priority levels, 16-line controller | spec_plan.md §4 |
| Boot | Caravel mgmt SoC loads firmware into SRAM, then releases Ibex reset | spec_plan.md §5 |
| SRAM | 8KB (2048×32-bit), real sky130 macro (~2K cells) | spec_plan.md §5 |
| Power | ≤100 mW active | spec_plan.md §8 |

---

## 2. Memory Map

### 2.1 Address Regions

| Region | Base Address | Size | Type | Module | Description |
|--------|-------------|------|------|--------|-------------|
| SRAM | 0x0000_0000 | 8KB (0x2000) | RAM | sram_8kb | Unified Von Neumann SRAM. Boot vector. 2048×32-bit. |
| UART 0 | 0x8000_0000 | 4KB (0x1000) | Peripheral | uart_0 | GPS — 115200 baud, 8N1 |
| UART 1 | 0x8000_1000 | 4KB (0x1000) | Peripheral | uart_1 | RC receiver — CRSF 420k / SBUS 100k baud |
| UART 2 | 0x8000_2000 | 4KB (0x1000) | Peripheral | uart_2 | Telemetry/debug — 115200 baud |
| SPI 0 | 0x8000_3000 | 4KB (0x1000) | Peripheral | spi_0 | IMU sensor SPI master (ICM-42688-P) |
| I2C 0 | 0x8000_4000 | 4KB (0x1000) | Peripheral | i2c_0 | Barometer + magnetometer |
| DShot PWM | 0x8000_5000 | 4KB (0x1000) | Peripheral | dshot_pwm | 4×DShot 300 + 2×standard PWM |
| GPIO | 0x8000_6000 | 4KB (0x1000) | Peripheral | gpio | 8 interrupt-capable GPIO pins |
| SPI Flash Ctrl | 0x8000_7000 | 4KB (0x1000) | Peripheral | spi_flash_ctrl | External W25Q32JV 4MB NOR flash |
| IRQ Ctrl | 0x8000_8000 | 4KB (0x1000) | Peripheral | irq_ctrl | 16-source interrupt controller |
| Timer | 0x8000_9000 | 4KB (0x1000) | Peripheral | timer | 32-bit auto-reload + input capture |
| Watchdog | 0x8000_A000 | 4KB (0x1000) | Peripheral | watchdog | 32-bit watchdog timer |
| Caravel Bridge | 0x8000_B000 | 4KB (0x1000) | Peripheral | caravel_wrapper | Caravel management SoC bridge |
| CLK/RST Manager | 0x8000_C000 | 4KB (0x1000) | Peripheral | clk_rst_mgr | Clock divider + reset synchronizer |
| Custom Timer | 0x8000_D000 | 4KB (0x1000) | Peripheral | custom_timer | DShot RPM telemetry timer extensions |

### 2.2 Memory Map Rules

- **Peripheral alignment:** 4KB (0x1000) — consistent with Wishbone B4 12-bit address decode.
- **No overlaps:** All 16 regions verified non-overlapping. SRAM: 0x0000_0000–0x0000_1FFF (8KB). Peripherals: 0x8000_0000–0x8000_DFFF.
- **Boot vector:** 0x0000_0000. Caravel management SoC loads firmware via `caravel_wrapper` before releasing Ibex reset.
- **Reserved gaps:** 0x0000_2000–0x7FFF_FFFF (future SRAM expansion). 0x8000_E000–0xFFFF_FFFF (future peripherals).
- **Address decode:** `wb_addr[31:12]` selects slave. Bits [11:0] are the peripheral register offset. For SRAM: `wb_addr[31:13]` = 0 selects the 8KB region.

### 2.3 Structured Memory Map

See `memory_map.json` for machine-readable address map. Generated from this section.

---

## 3. Bus Architecture

### 3.1 Bus Protocol

| Property | Value |
|----------|-------|
| Protocol | Wishbone B4 Classic (single master, single-cycle) |
| Data width | 32-bit |
| Address width | 32-bit |
| Granularity | Byte-select via `wb_sel_i[3:0]` |
| Handshake | STB + CYC → ACK/ERR (classic cycle) |
| Cycle types | Single read/write only (no burst/block transfers) |

### 3.2 Bus Topology

```
ibex_core (Wishbone LSU — native, no bridge)
  │  wb_adr_o, wb_dat_o, wb_sel_o, wb_we_o, wb_stb_o, wb_cyc_o
  ▼
wishbone_interconnect (15-slave one-hot address decoder + registered read-data mux)
  │
  ├── slave[0]:  sram_8kb          @ 0x0000_0000 (8KB)
  ├── slave[1]:  uart_0            @ 0x8000_0000
  ├── slave[2]:  uart_1            @ 0x8000_1000
  ├── slave[3]:  uart_2            @ 0x8000_2000
  ├── slave[4]:  spi_0             @ 0x8000_3000
  ├── slave[5]:  i2c_0             @ 0x8000_4000
  ├── slave[6]:  dshot_pwm         @ 0x8000_5000
  ├── slave[7]:  gpio              @ 0x8000_6000
  ├── slave[8]:  spi_flash_ctrl    @ 0x8000_7000
  ├── slave[9]:  irq_ctrl          @ 0x8000_8000
  ├── slave[10]: timer             @ 0x8000_9000
  ├── slave[11]: watchdog          @ 0x8000_A000
  ├── slave[12]: caravel_wrapper    @ 0x8000_B000
  ├── slave[13]: clk_rst_mgr       @ 0x8000_C000
  └── slave[14]: custom_timer      @ 0x8000_D000
```

**Address decoding:** `wishbone_interconnect` decodes `wb_addr[31:12]` to one-hot `slave_sel_o[14:0]`. For SRAM (8KB), `wb_addr[31:13]` = 0 selects slave[0]. All other slaves use `wb_addr[31:12]` match. The read-data path is a 15:1 combinational mux on `slave[N].wb_dat_o`, registered on ACK (`rd_data_q`).

### 3.3 Wishbone Master Interface (ibex_core → wishbone_interconnect)

| Signal | Direction | Width | Description |
|--------|-----------|-------|-------------|
| wb_clk_i | Input | 1 | Bus clock (16.67 MHz) |
| wb_rst_ni | Input | 1 | Bus reset (active low, sync deassert) |
| wb_adr_o | Output | 32 | Address |
| wb_dat_o | Output | 32 | Write data |
| wb_dat_i | Input | 32 | Read data (from registered mux) |
| wb_sel_o | Output | 4 | Byte select |
| wb_we_o | Output | 1 | Write enable (1=write, 0=read) |
| wb_stb_o | Output | 1 | Strobe |
| wb_cyc_o | Output | 1 | Cycle |
| wb_ack_i | Input | 1 | Acknowledge (OR of all slave ACKs) |
| wb_err_i | Input | 1 | Error (OR of all slave ERRs) |

### 3.4 Wishbone Slave Interface (all peripherals + SRAM)

| Signal | Direction | Width | Description |
|--------|-----------|-------|-------------|
| wb_adr_i | Input | 32 | Address (from interconnect) |
| wb_dat_i | Input | 32 | Write data |
| wb_dat_o | Output | 32 | Read data (to mux) |
| wb_sel_i | Input | 4 | Byte select |
| wb_we_i | Input | 1 | Write enable |
| wb_stb_i | Input | 1 | Chip select (decoded, one-hot) |
| wb_cyc_i | Input | 1 | Cycle |
| wb_ack_o | Output | 1 | Acknowledge |
| wb_err_o | Output | 1 | Error |

### 3.5 SRAM Slave Interface (sram_8kb — 13-bit address)

| Signal | Direction | Width | Description |
|--------|-----------|-------|-------------|
| clk_i | Input | 1 | System clock (16.67 MHz) |
| rst_ni | Input | 1 | Async reset, active low |
| wb_adr_i | Input | 13 | Word address (2048 entries, bits [12:0]) |
| wb_dat_i | Input | 32 | Write data |
| wb_dat_o | Output | 32 | Read data (registered) |
| wb_sel_i | Input | 4 | Byte select |
| wb_we_i | Input | 1 | Write enable |
| wb_stb_i | Input | 1 | Strobe (chip select) |
| wb_cyc_i | Input | 1 | Cycle |
| wb_ack_o | Output | 1 | Acknowledge (single-cycle) |

**Note:** SRAM uses 13-bit word address (2048×32-bit). The interconnect extracts `wb_addr[14:2]` for the 13-bit SRAM address. Byte address bits [1:0] are handled by `wb_sel_i`.

---

## 4. Modules

### 4.1 ibex_core (CPU)

**Purpose:** lowRISC Ibex RV32IMC processor in "maxperf" configuration. Executes the flight control firmware from SRAM.

**Interface:**
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| clk_i | Input | 1 | Core clock (16.67 MHz) |
| rst_ni | Input | 1 | Async reset, active low |
| wb_adr_o | Output | 32 | Wishbone address |
| wb_dat_o | Output | 32 | Wishbone write data |
| wb_dat_i | Input | 32 | Wishbone read data |
| wb_sel_o | Output | 4 | Byte select |
| wb_we_o | Output | 1 | Write enable |
| wb_stb_o | Output | 1 | Strobe |
| wb_cyc_o | Output | 1 | Cycle |
| wb_ack_i | Input | 1 | Acknowledge |
| wb_err_i | Input | 1 | Error |
| irq_software_i | Input | 1 | Software interrupt |
| irq_timer_i | Input | 1 | Timer interrupt |
| irq_external_i | Input | 1 | External interrupt (from irq_ctrl) |
| irq_fast_i | Input | 15 | Fast interrupt lines (unused, tied low) |
| fetch_enable_i | Input | 1 | Fetch enable (deassert during reset) |

**Functional Description:**
- 2-stage pipeline: IF (instruction fetch) → ID/EX (decode + execute + memory access).
- Native Wishbone LSU — no bridge needed. Ibex directly drives Wishbone master signals.
- I-side and D-side share the same Wishbone bus (Von Neumann architecture).
- RV32IMC: base integer (I), multiply/divide (M), compressed (C).
- 1-cycle fast multiplier (not iterative). 3.13 CoreMark/MHz.
- Machine mode only. Reset vector: 0x0000_0000.

**Timing:** 2-stage pipeline. Fetch takes 1-2 cycles (Wishbone ACK latency). Most ALU ops complete in 1 cycle. Loads: 2-3 cycles. Stores: 1-2 cycles. Multiplies: 1 cycle. Divides: up to 35 cycles. At 16.67 MHz: 60 ns per cycle.

**Edge Cases:**
- **Reset state:** All GPRs = 0x0000_0000. PC = 0x0000_0000. All CSRs = reset value per RISC-V spec.
- **W1C behavior:** N/A — CPU core CSRs follow RISC-V privileged spec. mip bits are W1C where applicable.
- **Fetch enable:** Must be held low during reset and until firmware is loaded. Deasserting `fetch_enable_i` prevents speculative fetches to uninitialized SRAM.
- **D-side stall:** Ibex will stall indefinitely if `wb_ack_i` is never asserted. watchdog timeout catches this.
- **M-mode only:** No U/S mode. No PMP. No MMU. Trap vector at `mtvec`.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~14,500 (RV32IMC maxperf) |
| DFFs | ~3,800 |
| Critical path | ~25 ns (multiply datapath — generous at 60 ns period) |
| Source | lowRISC Ibex, 15/15 STRONG qualification |

---

### 4.2 wishbone_interconnect (Shared Bus)

**Purpose:** 15-slave Wishbone B4 one-hot address decoder with registered read-data mux. Single master (Ibex), 15 slaves (SRAM + 12 peripherals + caravel_wrapper + clk_rst_mgr).

**Interface (Master side — from Ibex LSU):**
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| wb_clk_i | Input | 1 | Bus clock (16.67 MHz) |
| wb_rst_ni | Input | 1 | Bus reset (active low, sync deassert) |
| wb_adr_i | Input | 32 | Address |
| wb_dat_i | Input | 32 | Write data |
| wb_sel_i | Input | 4 | Byte select |
| wb_we_i | Input | 1 | Write enable |
| wb_stb_i | Input | 1 | Strobe |
| wb_cyc_i | Input | 1 | Cycle |
| wb_dat_o | Output | 32 | Read data (registered) |
| wb_ack_o | Output | 1 | Acknowledge |
| wb_err_o | Output | 1 | Error |

**Interface (Slave side):**
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| slave_adr_o[N] | Output | 32 | Address to slave N |
| slave_dat_o[N] | Output | 32 | Write data to slave N |
| slave_sel_o[N] | Output | 4 | Byte select to slave N |
| slave_we_o[N] | Output | 1 | Write enable to slave N |
| slave_stb_o[N] | Output | 1 | Strobe (one-hot, decoded) |
| slave_cyc_o[N] | Output | 1 | Cycle |
| slave_dat_i[N] | Input | 32 | Read data from slave N |
| slave_ack_i[N] | Input | 1 | Acknowledge from slave N |
| slave_err_i[N] | Input | 1 | Error from slave N |

**Functional Description:**
- **Address decoder:** Combinational. Decodes `wb_addr[31:12]` to one-hot `slave_sel_o[14:0]`. For SRAM: `wb_addr[31:13]` = 0 selects slave[0].

| Slave ID | Base Address | wb_addr[31:12] match |
|----------|-------------|----------------------|
| 0 | 0x0000_0000 | 0x00000 (SRAM, 8KB) |
| 1 | 0x8000_0000 | 0x80000 |
| 2 | 0x8000_1000 | 0x80001 |
| 3 | 0x8000_2000 | 0x80002 |
| 4 | 0x8000_3000 | 0x80003 |
| 5 | 0x8000_4000 | 0x80004 |
| 6 | 0x8000_5000 | 0x80005 |
| 7 | 0x8000_6000 | 0x80006 |
| 8 | 0x8000_7000 | 0x80007 |
| 9 | 0x8000_8000 | 0x80008 |
| 10 | 0x8000_9000 | 0x80009 |
| 11 | 0x8000_A000 | 0x8000A |
| 12 | 0x8000_B000 | 0x8000B |
| 13 | 0x8000_C000 | 0x8000C |
| 14 | 0x8000_D000 | 0x8000D |

- **Read-data mux:** 15:1 combinational mux on `slave_dat_i[N]`, output registered on ACK (`rd_data_q <= mux_out` when `any_ack`). Default mux output = 0x0000_0000.

**Timing:** Slave response: 0-1 cycles (combinational ACK for peripherals, registered for SRAM). Total read latency: 1-2 cycles. Write latency: 1 cycle.

**Edge Cases:**
- **Unmapped address:** If no slave matches, no `slave_stb_o` asserted. Ibex stalls until watchdog timeout. **Fix:** Add timeout counter or default error slave. Deferred — watchdog catches this.
- **Simultaneous ACK:** Only one slave is selected per transaction → only one ACK possible. No arbitration needed.
- **Registered read-data hold time:** `rd_data_q` holds stable until next ACK. Returns stale data if master reads without new transaction. **Expected behavior** — master ignores `wb_dat_o` when `wb_ack_o` is low.
- **Reset state:** All slave_select = 0. rd_data_q = 0x0000_0000.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~220 (decoder 50 + mux 170) |
| DFFs | ~32 (rd_data_q) |
| Critical path | ~12 ns (15:1 mux + register setup — generous at 60 ns) |
| Source | IP-005 Wishbone interconnect, extended to 14 slaves |

---

### 4.3 sram_8kb (System SRAM) ★ v4 — Real sky130 Macro (inherited from v3)

**Purpose:** 8KB unified Von Neumann SRAM. Holds firmware instructions and data. Boot vector at 0x0000_0000.

**Interface:** SRAM-specific Wishbone B4 slave (§3.5):

| Signal | Direction | Width | Clock Domain | Description |
|--------|-----------|-------|-------------|-------------|
| clk_i | Input | 1 | sys_clk | System clock (16.67 MHz) |
| rst_ni | Input | 1 | sys_clk | Async reset, active low |
| wb_adr_i | Input | 13 | sys_clk | Word address (2048 entries) |
| wb_dat_i | Input | 32 | sys_clk | Wishbone write data |
| wb_dat_o | Output | 32 | sys_clk | Wishbone read data (registered) |
| wb_sel_i | Input | 4 | sys_clk | Byte select |
| wb_we_i | Input | 1 | sys_clk | Write enable |
| wb_stb_i | Input | 1 | sys_clk | Strobe (chip select, one-hot decoded) |
| wb_cyc_i | Input | 1 | sys_clk | Bus cycle |
| wb_ack_o | Output | 1 | sys_clk | Acknowledge (single-cycle) |

**Functional Description:**
- 2048 × 32-bit words (8KB).
- Single-cycle read and write. Zero wait states.
- Byte-select support via `wb_sel_i[3:0]`. Unaligned byte/halfword writes are supported.
- **v3: Real sky130 SRAM macro.** Proven silicon — eliminates the 107K-cell DFF array risk from v2.
- Behavioral Verilog model for RTL sim. Real macro for synthesis/PD (same port interface).
- Anti-fabrication: Behavioral model for RTL sim only. Real macro used for synthesis/PD.

**Timing:** Single-cycle read (combinational), single-cycle write (registered on `wb_clk_i` posedge). Zero wait states. At 16.67 MHz: 60 ns access time (well within SRAM macro spec).

**Edge Cases:**
- **Simultaneous read/write:** Not possible — Wishbone is half-duplex (WE determines direction).
- **Byte-enable writes:** Writing with partial `wb_sel_i` updates only the selected bytes. Unselected bytes retain their value.
- **Reset state:** All SRAM contents = undefined after power-on. Firmware is loaded by Caravel management SoC after reset release.
- **Read during write cycle:** Write takes effect at next posedge. Read in same cycle returns old value.
- **Address wrap:** Addresses beyond 0x1FFF wrap modulo 8KB. `wb_adr_i[12:0]` masked to 2048 entries.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~2,000 (real sky130 SRAM macro — hard macro, not synthesized) |
| DFFs | 0 (SRAM macro, not DFF array) |
| Critical path | ~5 ns (macro access time) |
| Source | Real sky130 SRAM macro — proven silicon, v3 upgrade from behavioral DFF |

---

### 4.4 uart_0/1/2 (UART Controllers)

**Purpose:** Three identical UART instances, Wishbone B4 native. UART 0 = GPS (115200 baud), UART 1 = RC receiver (CRSF 420k / SBUS 100k baud), UART 2 = telemetry (115200 baud).

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| uart_tx_o | Output | 1 | UART TX output |
| uart_rx_i | Input | 1 | UART RX input |
| irq_rx_o | Output | 1 | RX FIFO not-empty interrupt |
| irq_tx_o | Output | 1 | TX FIFO empty interrupt |

**Functional Description:**
- TX FIFO: 16 bytes deep. Write `TXDATA` register to queue byte.
- RX FIFO: 16 bytes deep. Read `RXDATA` register to dequeue byte.
- Configurable baud rate: divider = clk_hz / baud_rate. For 16.67 MHz: 115200 → div 144, 420000 → div 40, 100000 → div 167.
- Frame format: 8N1 (8 data bits, no parity, 1 stop bit). SBUS inversion handled by firmware (read inverted bit).
- Interrupts: `irq_rx_o` when RX FIFO non-empty. `irq_tx_o` when TX FIFO empty.

**Register Map (per instance, offsets relative to base):**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | TXDATA | W | 0x00 | TX data write (pushes to TX FIFO) |
| 0x04 | RXDATA | R | 0x00 | RX data read (pops from RX FIFO) |
| 0x08 | STATUS | R | 0x00 | bit[0]=RX ready, bit[1]=TX full, bit[2]=TX empty |
| 0x0C | CTRL | R/W | 0x00 | bit[0]=TX enable, bit[1]=RX enable |
| 0x10 | DIVIDER | R/W | 0x0000 | Baud rate divider (clk_hz / baud) |

**Timing:** Write: 1 cycle (FIFO push). Read: 1 cycle (FIFO pop). TX bit period: `DIVIDER` cycles. RX sampling: 8× oversampling. At 16.67 MHz: 115200 baud → 144 ticks/bit, 420k baud → 40 ticks/bit.

**v4 Baud Rate Dividers:**

| Baud Rate | Divider (16.67 MHz) | Actual Baud | Error |
|-----------|---------------------|-------------|-------|
| 115200 | 144 | 115,764 | 0.49% |
| 420000 | 40 | 416,750 | 0.77% |
| 100000 | 167 | 99,820 | 0.18% |

**Edge Cases:**
- **TX FIFO full write:** Data is lost if TX FIFO is full (16 bytes). STATUS bit[1] warns firmware. **Firmware must check before writing.**
- **RX FIFO overflow:** If RX FIFO is full and a new byte arrives, the oldest byte is dropped. **Firmware must drain RX promptly.**
- **Baud rate divider resolution:** At 16.67 MHz, 420k baud → div=40 (416.75k actual). Error = 0.77% — acceptable for CRSF.
- **SBUS inversion:** UART hardware expects NRZ (idle high, start=low). SBUS is inverted (idle low, start=high). Firmware reads inverted bits. No hardware inverter needed.
- **Reset state:** All registers = 0x00. FIFOs empty. TX line idle (high). RX line ignored until enabled.

**Area/Timing Budget (per instance):**
| Metric | Value |
|--------|-------|
| Cells | ~500 |
| DFFs | ~200 |
| Critical path | ~12 ns (baud rate counter — generous at 60 ns) |
| Source | IP-005 Wishbone UART, lint/formal/synth/equiv PASS |

---

### 4.5 spi_0 (SPI Master)

**Purpose:** Wishbone B4 SPI master for IMU sensor (ICM-42688-P). Operates at 8.335 MHz (16.67 MHz / 2) for reliable IMU reads.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| spi_sck_o | Output | 1 | SPI clock |
| spi_mosi_o | Output | 1 | Master Out Slave In |
| spi_miso_i | Input | 1 | Master In Slave Out |
| spi_cs_o | Output | 1 | Chip select (active low) |
| irq_done_o | Output | 1 | Transfer complete interrupt |

**Functional Description:**
- SPI mode 0 (CPOL=0, CPHA=0). 8-bit word size.
- Configurable prescaler: /2 (8.335 MHz) or /4 (4.167 MHz). /2 recommended for IMU.
- Single-word transfers: write `TXDATA`, poll STATUS for completion, read `RXDATA`.
- IMU reads: SPI sends register address + R/W bit, receives 14-byte IMU frame.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | TXDATA | R/W | 0x00 | TX/RX data (write to start transfer) |
| 0x04 | STATUS | R | 0x00 | bit[0]=done, bit[1]=busy |
| 0x08 | CTRL | R/W | 0x00 | bit[1:0]=prescaler (00=/2, 01=/4, 10=/8, 11=/16) |

**Timing:** 8 SCLK cycles per byte transfer. At 8.335 MHz SCLK: 960 ns per byte. 14-byte IMU read: ~13.4 µs (vs 9 µs at v2 12.5 MHz).

**Edge Cases:**
- **Busy-write:** Writing TXDATA while STATUS[busy]=1 → new transfer queued, clobbers in-flight data. **Firmware must poll STATUS[busy]==0 before writing.**
- **CS deassertion:** CS remains asserted between back-to-back writes if firmware writes TXDATA quickly. To deassert CS, write CTRL with CS=1.
- **SPI mode:** CPOL=0, CPHA=0 fixed for ICM-42688-P. Not configurable.
- **Reset state:** All registers = 0x00. SCK = 0. MOSI = 0. CS = 1 (deasserted).

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~400 |
| DFFs | ~100 |
| Critical path | ~8 ns |
| Source | IP-005 Wishbone SPI, lint/formal/synth/equiv PASS |

---

### 4.6 i2c_0 (I2C Master)

**Purpose:** Wishbone B4 I2C master for barometer (BMP280) and magnetometer (QMC5883L). Standard-mode (100 kHz) and fast-mode (400 kHz).

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| i2c_scl_o | Output | 1 | I2C clock (open-drain via pad) |
| i2c_sda_o | Output | 1 | I2C data out (open-drain via pad) |
| i2c_sda_i | Input | 1 | I2C data in |
| irq_done_o | Output | 1 | Transaction complete interrupt |

**Functional Description:**
- 7-bit addressing. START/STOP generation. ACK/NACK detection.
- Single-byte and multi-byte read/write transactions.
- Firmware writes command register to initiate transaction. Polls STATUS for completion.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | CMD | R/W | 0x00 | Command: START, STOP, WRITE, READ, ACK, NACK |
| 0x04 | DATA | R/W | 0x00 | TX/RX data byte |
| 0x08 | STATUS | R | 0x00 | bit[0]=done, bit[1]=busy, bit[2]=ACK received |
| 0x0C | PRESCALE | R/W | 0x00 | Clock prescaler (16.67 MHz / (4 × PRESCALE) = SCL freq) |

**v4 I2C Prescaler Values:**

| Mode | SCL Freq | PRESCALE | Actual SCL | Error |
|------|----------|----------|------------|-------|
| Standard | 100 kHz | 42 | 99.2 kHz | 0.8% |
| Fast | 400 kHz | 10 | 416.75 kHz | 4.2% |

**Timing:** 1 SCL cycle per bit, 9 bits per byte (8 data + ACK). At 400 kHz SCL: ~22.5 µs per byte.

**Edge Cases:**
- **Bus arbitration:** Not implemented. Single-master I2C bus (only IP-010 SoC initiates transactions).
- **Clock stretching:** Slave can hold SCL low. Master must wait. **Implemented** — STATUS[busy] stays high while SCL held low.
- **NACK handling:** If slave NACKs, STATUS[2]=0. Firmware must check and retry or abort.
- **Reset state:** All registers = 0x00. SCL = 1, SDA = 1 (idle). PRESCALE = 0 → SCL = 0 until configured.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~285 |
| DFFs | ~80 |
| Critical path | ~8 ns |
| Source | IP_003_I2C (IP-005/v4), lint/formal/synth/equiv PASS |

---

### 4.7 dshot_pwm (DShot PWM Timer) ★ CREATE — v4 (inherited from v3)

**Purpose:** Hardware DShot 300 frame generator for 4 ESC channels + 2 standard PWM channels. Replaces firmware bit-banging — frees CPU for PID math.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| dshot_out_o[3:0] | Output | 4 | DShot 300 output per channel |
| pwm_out_o[1:0] | Output | 2 | Standard 50-400 Hz PWM output |
| irq_update_o | Output | 1 | Frame update complete interrupt |

**Functional Description:**

**DShot 300 Mode (channels 0-3):**
- 60 ns timer tick (16.67 MHz). DShot 300 bit period = 3,333 ns = 55 ticks.
- Bit encoding: Bit 0 → T0H=1250 ns (21 ticks) high + T0L=2083 ns (34 ticks) low. Bit 1 → T1H=2500 ns (42 ticks) high + T1L=833 ns (13 ticks) low.
- **v3 timing precision:** 55 ticks/bit (vs 167 at 50 MHz). Still adequate — 60 ns resolution vs DShot spec ±2% tolerance (67 ns).
- 16-bit frame: 11-bit throttle (0-2047) + 1-bit telemetry request + 4-bit CRC-4.
- Double-buffered throttle registers: write `THROTTLE_NEXT[ch]`, then write `COMMIT` to atomically transfer all 4 channels to active registers.
- Frame generation FSM: IDLE → BIT0 → BIT1 → ... → BIT15 → IDLE. 16 bits × 55 ticks = 880 ticks = 52.8 µs per frame. 4 channels sequential = ~211 µs total. Update rate: ~4.73 kHz (supports 4 kHz PID loop).
- Throttle=0 → disarmed (output remains low, no frame generated).

**Standard PWM Mode (channels 4-5):**
- 16-bit period register (default 6,667 ticks = 400 ms at 16.67 MHz → wait, recalculate).
- **v3 PWM:** Default period = 6,667 ticks × 60 ns = 400 µs? No: 20 ms = 333,333 ticks at 16.67 MHz. That exceeds 16-bit (65535). **Solution:** Use prescaler /16 → period = 20,833 ticks for 20 ms.
- 16-bit duty register with prescaler. Glitch-free update: new duty loaded at period rollover.

**v4 DShot 300 Timing Table:**

| Parameter | v2 (50 MHz) | v3 (16.67 MHz) | DShot Spec |
|-----------|-------------|-----------------|------------|
| Ticks/bit | 167 | 55 | — |
| Tick resolution | 20 ns | 60 ns | — |
| T0H ticks | 63 | 21 | 1250 ns ±2% |
| T0L ticks | 104 | 34 | 2083 ns ±2% |
| T1H ticks | 125 | 42 | 2500 ns ±2% |
| T1L ticks | 42 | 13 | 833 ns ±2% |
| Frame time | 53.4 µs | 52.8 µs | — |
| 4-ch update | 214 µs | 211 µs | — |
| Max rate | 4.68 kHz | 4.73 kHz | — |

**CRC-4:** Polynomial 0x1D (x⁴+x³+x²+1). Computed over 12-bit payload (throttle[10:0] + telemetry bit). Hardware CRC generator, combinational (1 cycle).

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | THROTTLE0_NEXT | R/W | 0x000 | DShot ch0 next throttle (bits [10:0] valid) |
| 0x04 | THROTTLE1_NEXT | R/W | 0x000 | DShot ch1 next throttle |
| 0x08 | THROTTLE2_NEXT | R/W | 0x000 | DShot ch2 next throttle |
| 0x0C | THROTTLE3_NEXT | R/W | 0x000 | DShot ch3 next throttle |
| 0x10 | TELEMETRY | R/W | 0x0 | bit[3:0] = telemetry request per channel |
| 0x14 | COMMIT | W | — | Write (any value) → atomically copies NEXT→active |
| 0x18 | PWM0_DUTY | R/W | 0x0000 | PWM ch4 duty (ticks, prescaled) |
| 0x1C | PWM0_PERIOD | R/W | 0x5161 | PWM ch4 period (20,833 ticks = 20 ms @ /16) |
| 0x20 | PWM1_DUTY | R/W | 0x0000 | PWM ch5 duty |
| 0x24 | PWM1_PERIOD | R/W | 0x5161 | PWM ch5 period |
| 0x28 | STATUS | R | 0x00 | bit[0]=update pending, bit[1]=frame active |
| 0x2C | CTRL | R/W | 0x00 | bit[0]=DShot enable, bit[1]=PWM enable, bit[2]=auto-commit, bit[4:3]=PWM prescaler |

**Timing:** DShot frame: 52.8 µs per channel. PWM period: configurable (default 20 ms with /16 prescaler). Critical path: CRC-4 generator (~2 ns).

**Edge Cases:**
- **Throttle=0 (disarmed):** Output stays low indefinitely. No DShot frame generated. Motor stops.
- **Throttle=48 (min armed):** Minimum valid DShot throttle per spec. 48-2047 = valid range.
- **Throttle>2047:** Clamped to 0x7FF (11-bit). Upper bits ignored.
- **Double-buffered commit:** Writing THROTTLE_NEXT without COMMIT → old value continues. Writing COMMIT mid-frame → update deferred to next frame start.
- **Telemetry mode:** Telemetry bit is transmitted but ESC telemetry response capture is NOT implemented.
- **Auto-commit mode:** CTRL[2]=1 → COMMIT happens automatically at end of each 4-channel frame sequence.
- **PWM update glitch protection:** New PWM duty takes effect at period counter rollover, not mid-cycle.
- **PWM prescaler:** At 16.67 MHz, 20 ms period needs prescaler /16 (20,833 ticks). Without prescaler, 16-bit counter max = 3.93 ms.
- **Reset state:** All THROTTLE = 0x000 (disarmed). PWM duty = 0x0000. PWM period = 0x5161. All outputs = low. Frame FSM = IDLE.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~800-1,200 (FSM + 4×16-bit timer + CRC-4 + 6×output registers) |
| DFFs | ~300-400 |
| Critical path | ~12 ns (CRC-4 combinational + DShot timing FSM) |
| Source | CREATE — custom RTL. No pre-qualified IP. |

**Design Decisions:**
- DShot 300 chosen over DShot 600: 55 ticks/bit at 16.67 MHz is adequate. DShot 600 needs 27 ticks/bit — marginal timing.
- Transmit-only (no telemetry capture): Reduces FSM complexity.
- Sequential channel output: 4 channels sent one after another on the same timer FSM.
- PWM prescaler required at 16.67 MHz (vs no prescaler at 50 MHz).

---

### 4.8 gpio (GPIO Controller)

**Purpose:** 8-bit bidirectional GPIO with per-pin interrupt edge detection. Used for buzzer, LED, arming switch, failsafe, and auxiliary signals.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| gpio_in_i[7:0] | Input | 8 | GPIO input values |
| gpio_out_o[7:0] | Output | 8 | GPIO output values |
| gpio_oe_o[7:0] | Output | 8 | Output enable (1=output, 0=input) |
| irq_gpio_o[3:0] | Output | 4 | Per-pin interrupt (pins [3:0] only) |

**Functional Description:**
- 8 pins, individually configurable as input or output via `OE` register.
- Per-pin interrupt on rising edge, falling edge, or both (configurable via `IEV` register).
- 4 interrupt outputs (pins [3:0] only). Pins [7:4] are output-only (buzzer, LED).

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | DATA_IN | R | — | Current GPIO input values |
| 0x04 | DATA_OUT | R/W | 0x00 | GPIO output values |
| 0x08 | OE | R/W | 0x00 | Output enable (1=output, 0=input) |
| 0x0C | IEV | R/W | 0x00 | Interrupt edge: bit[N]=0 → falling, bit[N]=1 → rising |
| 0x10 | IPEND | R/W1C | 0x00 | Interrupt pending (write 1 to clear) |

**Timing:** Input read: 2 cycles (synchronizer). Output write: 1 cycle. Interrupt latency: 2 cycles (sync + edge detect). At 16.67 MHz: <10 µs ISR latency requirement met (120 ns actual).

**Edge Cases:**
- **W1C behavior (IPEND):** Write 1 to bit N → clears IRQ pending for pin N. Write 0 → no effect. W1C priority: clear overrides set.
- **Input synchronizer:** All inputs pass through 2-stage synchronizer (2 FFs) to prevent metastability. Adds 2-cycle latency.
- **Simultaneous set/clear:** If external pin toggles while firmware writes W1C to IPEND, the new edge is captured AFTER the W1C.
- **Reset state:** DATA_OUT = 0x00. OE = 0x00 (all inputs). IEV = 0x00 (all falling edge). IPEND = 0x00. gpio_out_o = 0x00.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~300 |
| DFFs | ~80 |
| Critical path | ~8 ns |
| Source | IP_008_GPIO_WB4, lint/formal/synth/equiv PASS |

---

### 4.9 spi_flash_ctrl (SPI Flash Controller)

**Purpose:** SPI flash controller for external W25Q32JV 4 MB NOR flash. Hardware acceleration for read commands. Firmware stored in flash, loaded into SRAM at boot by Caravel management SoC.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| flash_sck_o | Output | 1 | SPI flash clock |
| flash_mosi_o | Output | 1 | Master Out Slave In (flash SI) |
| flash_miso_i | Input | 1 | Master In Slave Out (flash SO) |
| flash_cs_o | Output | 1 | Chip select (active low) |
| flash_wp_o | Output | 1 | Write protect (active low) |
| flash_hold_o | Output | 1 | Hold (active low) |

**Functional Description:**
- Extends IP-005 SPI master with flash command FSM.
- Supported flash commands:

| Command | Code | Description |
|---------|------|-------------|
| Read JEDEC ID | 0x9F | Returns manufacturer + device ID (3 bytes) |
| Read Status | 0x05 | Returns flash status register |
| Write Enable | 0x06 | Set WEL bit before program/erase |
| Read Data | 0x03 | Standard read (8.335 MHz max) |
| Fast Read | 0x0B | Fast read with dummy byte (16.67 MHz) |
| Page Program | 0x02 | Program up to 256 bytes |
| Sector Erase | 0x20 | Erase 4 KB sector |

- SPI mode 0 (CPOL=0, CPHA=0). 8-bit command + 24-bit address + data.
- Flash clock: sys_clk/2 = 8.335 MHz for standard read, sys_clk = 16.67 MHz for fast read.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | CMD | R/W | 0x00 | Flash command byte |
| 0x04 | ADDR | R/W | 0x000000 | 24-bit flash address |
| 0x08 | TXDATA | W | — | Write data (for Page Program) |
| 0x0C | RDDATA | R | — | Read data (from Read/Read JEDEC ID) |
| 0x10 | STATUS | R | 0x00 | bit[0]=done, bit[1]=busy, bit[2]=WEL |
| 0x14 | CTRL | R/W | 0x00 | bit[0]=go, bit[1]=fast_mode |

**FSM States:** IDLE → CMD_SEND → ADDR_SEND(×3) → DATA_PHASE → DONE

**Timing:** Read JEDEC ID: 32 SCLK cycles = 3.84 µs at 8.335 MHz. Page Program: 8+24+2048 bits = 249.6 µs at 8.335 MHz (plus flash internal ~3 ms program time).

**Edge Cases:**
- **Write enable requirement:** Page Program and Sector Erase require prior Write Enable (0x06). Controller does NOT automatically issue 0x06 — firmware must send it explicitly.
- **Busy polling:** After Page Program or Sector Erase, flash is busy internally (~3 ms program, ~45 ms sector erase). STATUS[busy] reflects flash busy via Read Status polling.
- **Address wrap:** 24-bit address wraps at 16 MB. W25Q32JV is 4 MB (0x000000-0x3FFFFF).
- **CS hold between commands:** CS is deasserted between commands automatically.
- **WP and HOLD pins:** Tied high (inactive) via external pull-ups.
- **Reset state:** All registers = 0x00. CS = 1 (deasserted). SCK = 0. MOSI = 0. FSM = IDLE.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~600-900 (SPI master base ~400 + flash FSM ~200-500) |
| DFFs | ~150-250 |
| Critical path | ~12 ns |
| Source | CREATE — extends IP-005 SPI master with flash command FSM |

---

### 4.10 irq_ctrl (Interrupt Controller)

**Purpose:** 16-source interrupt controller with priority-based arbitration. Aggregates 13 peripheral interrupts into a single `m_irq` line to Ibex.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| irq_src_i[15:0] | Input | 16 | Interrupt source lines (level or edge, from peripherals) |
| m_irq_o | Output | 1 | Machine external interrupt to Ibex |

**Functional Description:**
- 16 interrupt source lines. Sources 0-12 assigned (see §6). Sources 13-15 reserved.
- Priority-arbitration: per-source 2-bit priority (0=highest, 3=lowest). Within same priority, lowest source ID wins.
- Threshold register: only sources with priority ≤ threshold can trigger CPU IRQ.
- Claim mechanism: Ibex reads CLAIM register → returns ID of highest pending enabled source, clears pending bit.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | PENDING | R | 0x0000 | Pending interrupt flags (read-only) |
| 0x04 | ENABLE | R/W | 0x0000 | Interrupt enable mask (per source) |
| 0x08 | PRIORITY0_7 | R/W | 0x0000 | Priority for sources 0-7 (2 bits each, packed) |
| 0x0C | PRIORITY8_15 | R/W | 0x0000 | Priority for sources 8-15 |
| 0x10 | THRESHOLD | R/W | 0x0 | Minimum priority to trigger CPU IRQ |
| 0x14 | CLAIM | R | 0x00 | Returns highest-priority pending enabled source ID (also clears pending) |

**Timing:** Combinational pending → priority → threshold → m_irq_o path: ~8 ns. CLAIM read: 1 cycle.

**Edge Cases:**
- **W1C behavior (PENDING):** PENDING is read-only. Bits are cleared by hardware when CLAIM is read.
- **CLAIM with nothing pending:** Returns 0 (source 0). Firmware must check PENDING register first.
- **Priority tie-breaking:** Same priority → lowest source ID wins.
- **Threshold = 3:** All sources can trigger CPU IRQ. Threshold = 0: only priority 0 sources trigger.
- **Reset state:** All registers = 0x0000. m_irq_o = 0. No interrupts enabled.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~350-500 |
| DFFs | ~100 |
| Critical path | ~8 ns (priority encoder) |
| Source | IP-008/IP-009 internal IRQ controller, lint/formal/synth PASS |

---

### 4.11 timer (32-bit Auto-Reload Timer)

**Purpose:** 32-bit auto-reload down-counter with input capture. Used for PID loop scheduling (4 kHz interval) and ESC RPM telemetry capture.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| capture_i | Input | 1 | Input capture trigger (ESC RPM pulse) |
| irq_overflow_o | Output | 1 | Timer overflow interrupt |
| irq_capture_o | Output | 1 | Input capture interrupt |

**Functional Description:**
- 32-bit down-counter with auto-reload. Counter decrements on each `clk_i` tick. At 0: reloads from `RELOAD` register, asserts `irq_overflow_o`.
- Input capture: on rising edge of `capture_i`, latches current counter value into `CAPTURE` register, asserts `irq_capture_o`.
- Prescaler: 1, 2, 4, 8, 16, 32, 64, 128.

**v4 PID Loop Timer:** At 16.67 MHz, 4 kHz interval = 4,167 ticks (with prescaler=1). Reload value = 4,167.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | COUNTER | R/W | 0x00000000 | Current counter value |
| 0x04 | RELOAD | R/W | 0x00000000 | Auto-reload value |
| 0x08 | CAPTURE | R | 0x00000000 | Captured counter value |
| 0x0C | CTRL | R/W | 0x00 | bit[0]=enable, bits[3:1]=prescaler |
| 0x10 | INTC | R/W1C | 0x00 | bit[0]=overflow IRQ clear, bit[1]=capture IRQ clear |

**Timing:** Counter decrement: 1 cycle. Capture: 2-cycle sync + latch. Overflow: reload + IRQ in same cycle.

**Edge Cases:**
- **W1C behavior (INTC):** Write 1 to INTC[0] → clears overflow IRQ. Write 1 to INTC[1] → clears capture IRQ. W1C suppress re-trigger for 1 cycle.
- **Counter freeze:** When disabled (CTRL[0]=0), counter holds value. Re-enabling resumes from held value (NOT from RELOAD).
- **Capture during overflow:** If capture edge arrives in the same cycle as counter overflow, capture latches the reloaded value (post-reload).
- **Prescaler change:** Changing prescaler mid-count → counter resets to RELOAD on next tick.
- **Reset state:** COUNTER = 0. RELOAD = 0. CAPTURE = 0. CTRL = 0x00 (disabled). INTC = 0x00. irq_overflow_o = 0. irq_capture_o = 0.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~400-600 |
| DFFs | ~100 |
| Critical path | ~8 ns (32-bit counter) |
| Source | IP_009_TIMER_WB4, lint/formal/synth/equiv PASS |

---

### 4.12 watchdog (Watchdog Timer)

**Purpose:** 32-bit watchdog timer. Firmware periodically "kicks" the watchdog. If kick doesn't arrive before timeout, watchdog asserts interrupt (pre-warning), then system reset.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| irq_warn_o | Output | 1 | Pre-warning interrupt (timeout approaching) |
| rst_req_o | Output | 1 | System reset request (to clk_rst_mgr) |

**Functional Description:**
- 32-bit down-counter. On timeout (counter reaches 0): if `WARN` > 0, assert `irq_warn_o` for `WARN` cycles, then assert `rst_req_o`.
- Kick sequence: write 0x5A to `KICK0`, then 0xA5 to `KICK1` within 16 cycles. Reloads counter from `TIMEOUT`.
- Grace period: firmware can ack `irq_warn_o` by writing `WARN_ACK` to extend before hard reset.
- One-time enable: write 1 to `CTRL[0]` to enable. Once enabled, cannot be disabled (write ignored).

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | CTRL | R/W* | 0x00 | bit[0]=enable (one-time), bit[1]=locked |
| 0x04 | TIMEOUT | R/W | 0xFFFFFFFF | Timeout period (ticks). 16.67M ticks = 1s at 16.67 MHz. |
| 0x08 | WARN | R/W | 0x0000 | Pre-warning period (ticks before hard reset) |
| 0x0C | KICK0 | W | — | Kick sequence byte 0 (write 0x5A) |
| 0x10 | KICK1 | W | — | Kick sequence byte 1 (write 0xA5) |
| 0x14 | WARN_ACK | W | — | Write (any value) → acknowledge warning, extend |
| 0x18 | STATUS | R | 0x00 | bit[0]=enabled, bit[1]=warn active, bit[2]=reset asserted |

**FSM States:** DISABLED → ARMED → WARNING → RESET

**Timing:** Counter decrements every clock cycle. At 16.67 MHz: max timeout = 2³² / 16.67 MHz ≈ 257 seconds (vs 85.9s at 50 MHz). Kick window: 16 cycles = 960 ns.

**Edge Cases:**
- **Wrong kick sequence:** KICK0=0x5A followed by anything other than KICK1=0xA5 → no reload. Counter continues counting.
- **Double-kick:** Writing multiple kicks before timeout → counter reloads each time. No penalty for early kicking.
- **Disable after enable:** Not possible. CTRL[0] write is ignored after first enable.
- **WARN_ACK abuse:** Firmware can ack warning repeatedly, but each ack only extends by WARN cycles.
- **Reset pulse width:** `rst_req_o` stays high for 16 cycles, then auto-deasserts.
- **Reset state:** DISABLED. CTRL = 0x00. TIMEOUT = 0xFFFFFFFF. WARN = 0x0000. Counter = TIMEOUT. All IRQ/RST outputs = 0.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~200-400 |
| DFFs | ~100-150 |
| Critical path | ~8 ns (32-bit counter) |
| Source | CREATE — extends existing timer IP with watchdog mode |

---

### 4.13 caravel_wrapper (Caravel Management SoC Bridge)

**Purpose:** Wishbone B4 slave that bridges the Caravel management SoC to the user project. Used for firmware loading, debug, and USB-UART passthrough.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional Caravel harness:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| la_data_in_i[127:0] | Input | 128 | Logic analyzer data from Caravel mgmt SoC |
| la_data_out_o[127:0] | Output | 128 | Logic analyzer data to Caravel mgmt SoC |
| la_oenb_i[127:0] | Input | 128 | Logic analyzer output enable |
| io_in_i[37:0] | Input | 38 | GPIO input from Caravel pads |
| io_out_o[37:0] | Output | 38 | GPIO output to Caravel pads |
| io_oeb_o[37:0] | Output | 38 | GPIO output enable |
| irq_caravel_o | Output | 1 | Caravel bridge interrupt |

**Functional Description:**
- Standard Caravel `user_project_wrapper` interface. Management SoC accesses user SRAM and peripherals via this bridge during boot.
- Firmware loading: Caravel mgmt SoC writes firmware image to SRAM via this bridge before releasing Ibex reset.
- USB-UART passthrough: Caravel routes UART 2 (telemetry) through the bridge for PC-side monitoring.
- Pin mux: Routes internal peripheral I/Os to Caravel GPIO pads (see §7).

**Timing:** Standard Wishbone slave latency. Bridge does not add extra cycles.

**Edge Cases:**
- **Caravel reset hold-off:** Bridge must ignore Wishbone transactions until Caravel management SoC releases `user_reset_n`.
- **LA bus width mismatch:** Only lower 32 bits of `la_data_in/out` are used for Wishbone bridging. Upper bits tied to 0.
- **Reset state:** All outputs = 0. Bridge disabled until Caravel releases reset.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~200 (pin mux + LA bridge logic) |
| DFFs | ~50 |
| Critical path | ~3 ns |
| Source | REUSE_GITHUB — Caravel template, 40+ MPW proven |

---

### 4.14 clk_rst_mgr (Clock & Reset Manager)

**Purpose:** Reset synchronizer, reset sequencer, and optional clock divider. Generates clean, synchronized resets for all modules.

**Interface:** Standard Wishbone B4 slave (§3.4). Additional:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| user_clock_i | Input | 1 | Caravel user clock (16.67 MHz) |
| user_reset_n_i | Input | 1 | Caravel user reset (active low, async) |
| wb_rst_n_o | Output | 1 | Bus reset (sync deassert, active low) |
| cpu_rst_n_o | Output | 1 | CPU reset (held until firmware loaded) |
| wdg_rst_req_i | Input | 1 | Watchdog reset request |
| sys_clk_o | Output | 1 | System clock (buffered user_clock) |

**Functional Description:**
- **Reset synchronizer:** 2-stage FF chain on `user_reset_n_i`. Async assert, sync deassert.
- **CPU reset hold-off:** `cpu_rst_n_o` is held low for 16 cycles after `user_reset_n_i` deassertion. This allows SRAM to stabilize before Ibex starts fetching.
- **Watchdog reset:** On `wdg_rst_req_i`, asserts all resets for 16 cycles, then releases.
- **Clock divider:** Optional ÷N divider for peripheral domains. Not used in v3 (single 16.67 MHz domain). Bypass mode: `sys_clk_o = user_clock_i`.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | STATUS | R | 0x00 | bit[0]=reset active, bit[1]=cpu held, bit[2]=wdg reset occurred |
| 0x04 | CTRL | R/W | 0x00 | bit[0]=cpu release, bit[3:1]=clock divider (000=bypass) |

**Timing:** Reset sync adds 2 cycles. CPU hold-off: 16 cycles after reset deassert. Watchdog reset pulse: 16 cycles. At 16.67 MHz: hold-off = 960 ns.

**Edge Cases:**
- **Reset glitch filtering:** 2-stage synchronizer rejects pulses shorter than 1 clock cycle (60 ns).
- **Double reset:** If watchdog reset occurs during Caravel reset, the longer reset wins.
- **Clock divider glitches:** Changing clock divider while running → clock output may glitch. **Firmware must gate output before changing.**
- **Reset state:** All resets asserted (active). STATUS = 0x07 (reset active, cpu held, no wdg event). CTRL = 0x00.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | ~50-100 |
| DFFs | ~20-40 |
| Critical path | ~2 ns |
| Source | REUSE_INTERNAL — trivial module |

---



---

### 4.15 custom_timer (DShot RPM Telemetry Timer Extensions) ★ CREATE

**Purpose:** Custom timer extensions for DShot RPM telemetry capture. Extends the 32-bit timer (Section 4.11) with dedicated RPM pulse measurement hardware for up to 4 ESC channels.

**Interface:** Standard Wishbone B4 slave (Section 3.4). Additional external I/O:
| Port | Direction | Width | Description |
|------|-----------|-------|-------------|
| rpm_capture_i[3:0] | Input | 4 | ESC RPM pulse inputs (one per DShot channel) |
| irq_rpm_o | Output | 1 | RPM measurement complete interrupt |

**Functional Description:**
- Extends the 32-bit timer input capture with 4-channel RPM measurement.
- Each channel captures rising-edge timestamps on `rpm_capture_i[N]`.
- Frequency measurement: RPM = 60 times sys_clk_hz / (capture_delta_ticks times pole_pairs).
- At 16.67 MHz: minimum measurable RPM approx 15 RPM (1 pulse/s). Maximum approx 250,000 RPM (4,167 ticks between pulses).
- RPM values stored in read-only capture registers, updated on each valid pulse.
- Anti-glitch filter: pulses shorter than 3 clock cycles (180 ns) are rejected.
- Interrupt: `irq_rpm_o` asserts when any channel completes a valid RPM measurement.

**Register Map:**
| Offset | Name | Access | Reset | Description |
|--------|------|--------|-------|-------------|
| 0x00 | RPM_CH0 | R | 0x0000 | Channel 0 RPM value (16-bit) |
| 0x04 | RPM_CH1 | R | 0x0000 | Channel 1 RPM value |
| 0x08 | RPM_CH2 | R | 0x0000 | Channel 2 RPM value |
| 0x0C | RPM_CH3 | R | 0x0000 | Channel 3 RPM value |
| 0x10 | POLE_PAIRS | R/W | 0x0007 | Motor pole pairs (default: 7 for typical brushless) |
| 0x14 | CTRL | R/W | 0x00 | bit[0]=enable, bit[3:1]=filter depth |
| 0x18 | STATUS | R | 0x00 | bit[3:0]=ch_valid, bit[4]=measurement active |

**Timing:** RPM measurement: continuous (updates on each valid pulse edge). Anti-glitch filter adds 3-cycle latency. At 16.67 MHz: RPM resolution = 60 times 16,666,667 / (N times POLE_PAIRS) for N ticks between pulses.

**Edge Cases:**
- **No pulse detected:** RPM registers hold last valid value (not 0). STATUS[ch_valid]=0 indicates stale data.
- **Pulse too fast:** If time between pulses is less than 3 cycles, measurement is skipped (anti-glitch).
- **Pulse too slow:** RPM = 0 reported if no pulse detected within 1 second (counter timeout).
- **Pole pairs = 0:** Treated as 1 internally (no divide-by-zero).
- **Reset state:** All RPM registers = 0x0000. POLE_PAIRS = 0x0007. CTRL = 0x00 (disabled). STATUS = 0x00. irq_rpm_o = 0.

**Area/Timing Budget:**
| Metric | Value |
|--------|-------|
| Cells | 200-350 |
| DFFs | 80-120 |
| Critical path | 8 ns (frequency divider + capture logic) |
| Source | CREATE — new module for v4, extends timer (Section 4.11) RPM capture capability |

## 5. Reset & Clock Strategy

### 5.1 Clock Architecture

| Property | Value |
|----------|-------|
| Clock domains | 1 (sys_clk, 16.67 MHz) |
| Clock source | Caravel `user_clock` input (external crystal) |
| Clock distribution | `clk_rst_mgr` buffers `user_clock` to all modules |
| Target frequency | 16.67 MHz (measured STA closure from v2 synthesis) |
| Clock period | 60 ns |
| Clock uncertainty | ±5% (PDK variation), 0.2 ns jitter |

**Single clock domain — no CDC required.** All modules operate from the same 16.67 MHz `sys_clk`. DShot timing resolution at 16.67 MHz (60 ns tick) is adequate (55 ticks per DShot 300 bit).

### 5.2 Reset Architecture

| Signal | Type | Assertion | Deassertion | Modules |
|--------|------|-----------|-------------|---------|
| user_reset_n_i | Global | Async | Sync (2-stage in clk_rst_mgr) | clk_rst_mgr input |
| wb_rst_n_o | Bus | Async assert | Sync deassert | All Wishbone slaves |
| cpu_rst_n_o | CPU | Async assert | Sync deassert (held 16 cycles extra) | ibex_core |
| wdg_rst_req_i | Watchdog | Async | — | clk_rst_mgr input (from watchdog) |

**Reset polarity:** Active low (`_n` suffix). All resets are asynchronous-assert, synchronous-deassert.

### 5.3 Boot Sequence

1. Power-on → Caravel management SoC holds `user_reset_n_i` low.
2. Caravel management SoC loads firmware image into SRAM via `caravel_wrapper`.
3. Caravel management SoC releases `user_reset_n_i` → `clk_rst_mgr` sync-deasserts `wb_rst_n_o` (immediate).
4. After 16 clock cycles (960 ns), `clk_rst_mgr` deasserts `cpu_rst_n_o`.
5. Ibex begins execution at 0x0000_0000.
6. Watchdog reset (if occurs): `wdg_rst_req_i` → all resets asserted for 16 cycles → reboot from step 4.

### 5.4 Reset Register Initialization

| Module | Register | Reset Value |
|--------|----------|-------------|
| All | All CSRs | 0x0000_0000 (unless otherwise specified) |
| ibex_core | PC | 0x0000_0000 |
| ibex_core | GPRs x0-x31 | 0x0000_0000 |
| sram_8kb | All 2048 words | Undefined (loaded by Caravel at boot) |
| dshot_pwm | THROTTLE[3:0] | 0x000 (disarmed) |
| dshot_pwm | PWM_PERIOD[1:0] | 0x5161 (20 ms @ /16 prescaler) |
| watchdog | TIMEOUT | 0xFFFF_FFFF (~257 s at 16.67 MHz) |

---

## 6. Interrupt Architecture

### 6.1 Interrupt Sources

| Source ID | Name | Module | Type | Priority | Description |
|-----------|------|--------|------|----------|-------------|
| 0 | IRQ_CARAVEL | caravel_wrapper | Level | 0 (highest) | Caravel management SoC |
| 1 | IRQ_WATCHDOG | watchdog | Level | 1 | Watchdog pre-warning |
| 2 | IRQ_TIMER0 | timer | Edge | 2 | PID loop timer overflow |
| 3 | IRQ_SPI0_DONE | spi_0 | Edge | 3 | SPI transfer complete |
| 4 | IRQ_UART1_RX | uart_1 | Level | 4 | RC receiver data ready |
| 5 | IRQ_UART0_RX | uart_0 | Level | 5 | GPS data ready |
| 6 | IRQ_UART2_RX | uart_2 | Level | 6 | Telemetry RX |
| 7 | IRQ_I2C0_DONE | i2c_0 | Edge | 7 | I2C transaction complete |
| 8 | IRQ_GPIO0 | gpio | Edge | 8 | GPIO pin 0 (arming switch) |
| 9 | IRQ_GPIO1 | gpio | Edge | 9 | GPIO pin 1 (failsafe) |
| 10 | IRQ_GPIO2 | gpio | Edge | 10 | GPIO pin 2 (aux) |
| 11 | IRQ_GPIO3 | gpio | Edge | 11 | GPIO pin 3 (aux) |
| 12 | IRQ_TIMER1_CAPTURE | timer | Edge | 12 | RPM input capture |
| 13-15 | (reserved) | — | — | — | Future expansion |

### 6.2 IRQ Routing

```
irq_ctrl
  ├── irq_src[0]  ← caravel_wrapper.irq_caravel_o
  ├── irq_src[1]  ← watchdog.irq_warn_o
  ├── irq_src[2]  ← timer.irq_overflow_o
  ├── irq_src[3]  ← spi_0.irq_done_o
  ├── irq_src[4]  ← uart_1.irq_rx_o
  ├── irq_src[5]  ← uart_0.irq_rx_o
  ├── irq_src[6]  ← uart_2.irq_rx_o
  ├── irq_src[7]  ← i2c_0.irq_done_o
  ├── irq_src[8:11] ← gpio.irq_gpio_o[3:0]
  └── irq_src[12] ← timer.irq_capture_o
  │
  └── m_irq_o → ibex_core.irq_external_i
```

### 6.3 Interrupt Priority Arbitration

- Priority 0 (highest): Caravel bridge. Must always be serviced.
- Priority 1: Watchdog warning. Firmware must kick watchdog or system reboots.
- Priority 2: PID timer. Affects flight stability — must meet 4 kHz deadline.
- Priority 3-7: Sensor data (SPI, I2C, UART). Important but not safety-critical.
- Priority 8-11: GPIO (arming, failsafe). Safety-critical in flight but low-frequency.
- Priority 12: RPM capture. Telemetry only — lowest priority.

**Within same priority:** Lower source ID wins (UP-counting).

---

## 7. External Pin Allocation (Caravel GPIO) ★ v4 PAD MAPPING (inherited from v3)

| GPIO Pins | Signal | Direction | Module | Description |
|-----------|--------|-----------|--------|-------------|
| io[3:0] | uart0_tx, uart0_rx, uart1_tx, uart1_rx | Out, In, Out, In | uart_0, uart_1 | GPS + RC UART |
| io[7:4] | uart2_tx, uart2_rx, —, — | Out, In, —, — | uart_2 | Telemetry/debug UART |
| io[9:8] | i2c_scl, i2c_sda | I/O | i2c_0 | **v3 FIX: I2C moved to [10:11]** |
| io[11:10] | i2c_scl, i2c_sda | I/O | i2c_0 | Sensor I2C (v3 corrected position) |
| io[15:12] | dshot[3:0] | Out | dshot_pwm | **v3 FIX: DShot moved to [15:12]** |
| io[17:16] | pwm[1:0] | Out | dshot_pwm | Standard PWM |
| io[25:18] | gpio[7:0] | I/O | gpio | Buzzer, LED, switches |
| io[33:26] | spi_sck, spi_mosi, spi_miso, spi_cs, flash_sck, flash_mosi, flash_miso, flash_cs | Various | spi_0, spi_flash_ctrl | SPI buses |
| io[37:34] | (reserved) | — | — | Future expansion |

**v4 Pad Mapping (inherited from v3):** I2C moved from io[17:16] to io[11:10]. DShot moved from io[25:22] to io[15:12]. This eliminates the I/O overlap that existed in v2.

**Total: 38/38 pins allocated.** No multiplexing needed.

---

## 8. CDC Plan

**CDC Paths: None.**

IP-010 v4 uses a single clock domain (16.67 MHz `sys_clk`). All modules clocked from the same source. No clock domain crossings exist. No synchronizers or CDC constraints are required.

See `cdc_plan.md` for the full CDC documentation.

---

## 9. Coding Constraints

### 9.1 Language
- Verilog 2005 (IEEE 1364-2005). No SystemVerilog in synthesizable RTL.
- SystemVerilog allowed in testbenches only.

### 9.2 Naming Conventions
| Element | Convention | Example |
|---------|-----------|---------|
| Clock input | `clk_i` | `wb_clk_i` |
| Reset input (active low) | `rst_ni` | `wb_rst_ni` |
| Module input | `signal_name_i` | `wb_adr_i` |
| Module output | `signal_name_o` | `wb_dat_o` |
| Internal wire/reg | `signal_name` | `rd_data_q` |
| Active low signal | `_n` suffix | `rst_n`, `cs_n` |
| Wishbone signals | `wb_` prefix | `wb_stb_i`, `wb_ack_o` |
| Interrupt signals | `irq_` prefix | `irq_rx_o` |
| Constant | ALL_CAPS | `NUM_SLAVES` |

### 9.3 Forbidden Patterns
- No `initial` blocks in synthesizable code.
- No latches: every `if` has an `else`, every `case` has a `default`.
- No partial bit-slice LHS assignment.
- No LHS concatenation in `assign` or `always` blocks.
- No implicit wires — all signals explicitly declared.
- No mixing blocking (`=`) and non-blocking (`<=`) in the same `always` block.
- No `#delay` in synthesizable code.
- No tri-state logic inside the SoC (bidirectional pads at Caravel wrapper only).

### 9.4 Required Patterns
- Active-low async reset: `always @(posedge clk_i or negedge rst_ni)`
- Registered outputs for all module boundary signals (1-cycle output latency) unless combinational.
- `default` in every `case` statement.
- 4-space indentation.
- Module header comment block: purpose, interface table, author, date.
- Separate `always @(*)` for combinational and `always @(posedge clk_i)` for sequential.

### 9.5 Module Boundaries
- Each module has exactly one clock domain.
- Module outputs are registered unless documented as combinational.
- Bus interfaces use Wishbone B4 classic (STB/CYC/ACK handshake).
- No module-to-module direct connections bypassing the Wishbone bus (except IRQ and reset).

---

## 10. SDC Constraints (Summary)

See `constraints/top.sdc` for the full SDC file. Key constraints:

| Constraint | Value |
|-----------|-------|
| Clock period | 60 ns (16.67 MHz) |
| Clock name | `sys_clk` |
| Clock source | `user_clock` input pad |
| Clock uncertainty | 1.5 ns (setup) / 0.9 ns (hold) |
| Input delay | 36.0 ns max / 1.5 ns min (external pins to first FF) |
| Output delay | 36.0 ns max / 1.5 ns min (last FF to external pins) |
| False paths | None (single clock domain) |
| Clock groups | None (single clock domain) |

---

## 11. ORFS Compatibility

### 11.1 Comparison Against Reference Designs

| Metric | IP-010 v3 | riscv32i (ORFS) | ibex (ORFS) |
|--------|-----------|-----------------|-------------|
| Cells (est.) | ~22,500 (excl. SRAM macro) | ~4,500 | ~15,000 |
| Core | Ibex RV32IMC | Stock RV32I | Ibex RV32IMC |
| Pipeline | 2-stage | Single-cycle | 2-stage |
| Peripherals | 12 slave modules | None | None |
| SRAM | 8KB real sky130 macro (~2K cells) | None | None |
| Bus | Wishbone B4 shared | Direct memory | TL-UL + Wishbone |
| Frequency | 16.67 MHz | 50 MHz | 50 MHz |

### 11.2 ORFS-Friendly Architecture Decisions

- **Bus interfaces are external wrappers, not synthesized into the core.** ✅
- **Memory interface is ORFS-friendly:** Real SRAM macro (not DFF array). No hardcoded boot ROM. ✅
- **Cell count sanity check:** ~22K cells for a 17-module SoC is within ORFS capability. ✅
- **Reference:** `/opt/OpenROAD/OpenROAD-flow-scripts/flow/designs/sky130hd/ibex/` is the closest comparison.

### 11.3 v3 ORFS Improvements Over v2

- **Real SRAM macro eliminates 107K-cell DFF array risk.** v2 behavioral model would synthesize to 106,902 cells. v3 real macro is ~2K cells.
- **16.67 MHz relaxes timing.** 60 ns period vs 20 ns at 50 MHz. Critical paths are no longer timing-critical.
- **Simpler synthesis.** No BLACKBOX complexity — real macro is placed as hard macro during P&R.

---

## 12. CSRs Not Covered by Per-Module Register Maps

The following are Ibex RISC-V standard CSRs (not Wishbone-mapped):

| CSR | Address | Access | Reset | Description |
|-----|---------|--------|-------|-------------|
| mstatus | 0x300 | RW | 0x0000_0000 | Machine status |
| misa | 0x301 | RO | — | ISA and extensions (RV32IMC) |
| mie | 0x304 | RW | 0x0000_0000 | Machine interrupt enable |
| mtvec | 0x305 | RW | 0x0000_0000 | Trap-handler base address |
| mscratch | 0x340 | RW | 0x0000_0000 | Scratch register |
| mepc | 0x341 | RW | 0x0000_0000 | Exception PC |
| mcause | 0x342 | RW | 0x0000_0000 | Trap cause |
| mtval | 0x343 | RW | 0x0000_0000 | Bad address or instruction |
| mip | 0x344 | RW | 0x0000_0000 | Interrupt pending |
| mhartid | 0xF14 | RO | 0x0000_0000 | Hardware thread ID |

---

## 13. Assumptions & Open Items

### 13.1 Simplifications
- Single clock domain (no CDC needed).
- M-mode only (no U/S mode, no PMP, no virtual memory).
- No DMA controller. All data movement is CPU-driven.
- No cache. Direct SRAM access.
- No debug interface (JTAG passthrough via Caravel bridge only).
- DShot transmit-only (no ESC telemetry capture).
- SPI flash: no XIP caching. Firmware loaded to SRAM by Caravel at boot.
- No performance counters.
- SRAM uses real sky130 macro (proven silicon).

### 13.2 v4 Improvements Over v3
- 16.67 MHz (measured STA closure) eliminates timing risk. 60 ns period is 3× more margin than needed for all critical paths.
- Real sky130 SRAM macro eliminates 107K-cell DFF array risk. ~2K cells vs 106K cells.
- Pad mapping fix: I2C [10:11], DShot [15:12] — no I/O overlap.
- Power budget: ≤100 mW active (conservative at 16.67 MHz).

### 13.3 Open Items

| # | Item | Owner | Status |
|---|------|-------|--------|
| 1 | DShot PWM RTL implementation + simulation | frontend-engineer | PENDING |
| 2 | Real SRAM macro integration (behavioral → macro) | backend-engineer | PENDING |
| 3 | Caravel mpw-precheck integration | backend-engineer | PENDING |
| 4 | 16.67 MHz synthesis validation | backend-engineer | PENDING |
| 5 | UART 420k baud divider verification (16.67 MHz / 420k = 39.7) | verification-engineer | PENDING |
| 6 | SPI flash controller: verify W25Q32JV command timing at 8.335 MHz | verification-engineer | PENDING |
| 7 | PWM prescaler verification (20 ms at 16.67 MHz needs /16) | verification-engineer | PENDING |
| 8 | SRAM macro timing characterization | backend-engineer | PENDING |

### 13.4 Known Limitations
- No ESC telemetry capture (DShot bidirectional mode). RPM data from timer input capture or UART.
- SPI flash is slow for XIP (~4.17 MB/s at 8.335 MHz). Critical loops must fit in SRAM.
- No hardware FPU. Attitude estimation uses fixed-point math.
- Single-issue, in-order execution. No branch prediction.
- 55 ticks/DShot bit (vs 167 at 50 MHz) — adequate but less timing margin.

---

## 14. References

1. spec_plan.md — 370 lines, 12 sections, 54 REQ-IDs (v4)
2. ../v2/03_architecture_stage/architecture_doc.md — v2 baseline architecture (1167 lines)
3. ../v2/02_specification_stage/golden_models/golden_model.py — 1014 lines, 9 modules
4. DShot protocol specification (flyduino/DSHOT)
5. Betaflight DShot implementation (GPLv3)
6. lowRISC Ibex RV32IMC documentation
7. Wishbone B4 specification (OpenCores)
8. FOSSi EF_UART, EF_SPI, EF_I2C, EF_GPIO, EF_TIMER, EF_WATCHDOG, EF_IRQ documentation
9. Caravel user_project_wrapper documentation (Efabless)
10. sky130A SRAM macro documentation
11. IP-010 v3 ARCHITECTURE_V3.md — baseline architecture (1198 lines)
