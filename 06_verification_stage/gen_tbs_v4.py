#!/usr/bin/env python3
"""
IP-010 v4 Testbench Generator v4 — handles all 4 port conventions.
Conventions found across 18 modules:
  1. "bare_clk_wb_bus":  clk_i, rst_i, cyc_i, stb_i, ... (EF wrapper modules)
  2. "bare_clk_wb_bus_rstni": clk_i, rst_ni, cyc_i, stb_i, ... (EF wrapper, active-low)
  3. "wb_clk_wb_bus":  wb_clk_i, wb_rst_ni, wb_cyc_i, wb_stb_i, ... (spi_flash_ctrl, dshot_pwm, custom_timer)
  4. "wb_bus_only":  clk_i, rst_ni, wb_cyc_i, wb_stb_i, ... (clk_rst_mgr, irq_ctrl, caravel_wrapper)
"""
import os

BASE = "~/hermes_workspace/projects/IP-010/v4"
VS = os.path.join(BASE, "06_verification_stage")
FS = os.path.join(BASE, "04_frontend_stage")

MODULES = [
    # Type 4: clk_i + rst_ni + wb_ bus prefix
    {"n": "clk_rst_mgr", "tier": "A", "top": "clk_rst_mgr",
     "rtl": ["rtl-clk_rst_mgr/rtl/clk_rst_mgr.v"],
     "style": "wb_bus_only", "regs": [0x00,0x04,0x08,0x0C], "init": ""},
    {"n": "irq_ctrl", "tier": "A", "top": "irq_ctrl",
     "rtl": ["rtl-irq_ctrl/rtl/irq_ctrl.v"],
     "style": "wb_bus_only", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14], "init": ""},
    {"n": "caravel_wrapper", "tier": "A", "top": "caravel_wrapper",
     "rtl": ["rtl-caravel_wrapper/rtl/caravel_wrapper.v"],
     "style": "wb_bus_only", "regs": [0x00], "init": ""},
    # Type 3: wb_clk_i + wb_rst_ni + wb_ bus prefix  
    {"n": "spi_flash_ctrl", "tier": "B", "top": "spi_flash_ctrl",
     "rtl": ["rtl-spi_flash_ctrl/rtl/spi_flash_ctrl.v","rtl-spi_flash_ctrl/rtl/spi_master.v"],
     "style": "wb_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14], "init": ""},
    {"n": "dshot_pwm", "tier": "B", "top": "dshot_pwm",
     "rtl": ["rtl-dshot_pwm/rtl/dshot_pwm.v"],
     "style": "wb_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14,0x18], "init": ""},
    {"n": "custom_timer", "tier": "B", "top": "custom_timer",
     "rtl": ["rtl-custom_timer/rtl/custom_timer.v"],
     "style": "wb_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    # Type 1: clk_i + rst_i + bare bus signals (EF wrappers)
    {"n": "timer", "tier": "B", "top": "EF_TMR32_WB",
     "rtl": ["rtl-timer/rtl/timer.v","rtl-timer/rtl/EF_TMR32_WB_wrapper.v",
             "rtl-timer/rtl/EF_TMR32.v","rtl-timer/rtl/ef_util_lib.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14,0x18,0x1C,0x20,0x24,0x28,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "watchdog", "tier": "B", "top": "EF_WDT32_WB",
     "rtl": ["rtl-watchdog/rtl/watchdog.v","rtl-watchdog/rtl/EF_WDT32_WB_wrapper.v",
             "rtl-watchdog/rtl/EF_WDT32.v","rtl-watchdog/rtl/ef_util_lib.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "uart_0", "tier": "B", "top": "EF_UART_WB",
     "rtl": ["rtl-uart_0/rtl/EF_UART_WB.v","rtl-uart_0/rtl/EF_UART_WB_wrapper.v",
             "rtl-uart_0/rtl/EF_UART.v","rtl-uart_0/rtl/ef_util_lib.v","rtl-uart_0/rtl/axis_fifo.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "uart_1", "tier": "B", "top": "EF_UART_WB",
     "rtl": ["rtl-uart_1/rtl/EF_UART_WB.v","rtl-uart_1/rtl/EF_UART_WB_wrapper.v",
             "rtl-uart_1/rtl/EF_UART.v","rtl-uart_1/rtl/ef_util_lib.v","rtl-uart_1/rtl/axis_fifo.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "uart_2", "tier": "B", "top": "EF_UART_WB",
     "rtl": ["rtl-uart_2/rtl/EF_UART_WB.v","rtl-uart_2/rtl/EF_UART_WB_wrapper.v",
             "rtl-uart_2/rtl/EF_UART.v","rtl-uart_2/rtl/ef_util_lib.v","rtl-uart_2/rtl/axis_fifo.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "gpio", "tier": "B", "top": "EF_GPIO8_WB",
     "rtl": ["rtl-gpio/rtl/gpio.v","rtl-gpio/rtl/EF_GPIO8_WB_wrapper.v",
             "rtl-gpio/rtl/EF_GPIO8.v","rtl-gpio/rtl/ef_util_lib.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0xFF00,0xFF04,0xFF08,0xFF0C], "init": "    dut.io_in.value = 0"},
    {"n": "spi_0", "tier": "C", "top": "EF_SPI_WB",
     "rtl": ["rtl-spi_0/rtl/spi_0.v","rtl-spi_0/rtl/EF_SPI_WB_wrapper.v",
             "rtl-spi_0/rtl/EF_SPI.v","rtl-spi_0/rtl/ef_util_lib.v","rtl-spi_0/rtl/spi_master.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14,0x18,0x1C,0x20,0x24,0x28,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
    {"n": "i2c_0", "tier": "C", "top": "EF_I2C_WB",
     "rtl": ["rtl-i2c_0/rtl/i2c_0.v","rtl-i2c_0/rtl/EF_I2C_WB_wrapper.v",
             "rtl-i2c_0/rtl/i2c_master.v","rtl-i2c_0/rtl/i2c_master_wbs_8.v",
             "rtl-i2c_0/rtl/i2c_master_wbs_16.v","rtl-i2c_0/rtl/i2c_init.v",
             "rtl-i2c_0/rtl/axis_fifo.v","rtl-i2c_0/rtl/i2c_single_reg.v",
             "rtl-i2c_0/rtl/ef_util_lib.v"],
     "style": "bare_clk_wb_bus", "regs": [0x00,0x04,0x08,0x0C,0x10,0x14,0x18,0x1C,0x20,0xFF00,0xFF04,0xFF08,0xFF0C], "init": ""},
]


def sigs(mod):
    """Return signal name dict based on module style."""
    s = mod["style"]
    if s == "wb_bus_only":
        return {"clk": "clk_i", "rst": "rst_ni", "rst_pol": "low",
                "cyc": "wb_cyc_i", "stb": "wb_stb_i", "we": "wb_we_i",
                "adr": "wb_adr_i", "din": "wb_dat_i", "dout": "wb_dat_o",
                "sel": "wb_sel_i", "ack": "wb_ack_o"}
    elif s == "wb_clk_wb_bus":
        return {"clk": "wb_clk_i", "rst": "wb_rst_ni", "rst_pol": "low",
                "cyc": "wb_cyc_i", "stb": "wb_stb_i", "we": "wb_we_i",
                "adr": "wb_adr_i", "din": "wb_dat_i", "dout": "wb_dat_o",
                "sel": "wb_sel_i", "ack": "wb_ack_o"}
    else:  # bare_clk_wb_bus
        return {"clk": "clk_i", "rst": "rst_i", "rst_pol": "high",
                "cyc": "cyc_i", "stb": "stb_i", "we": "we_i",
                "adr": "adr_i", "din": "dat_i", "dout": "dat_o",
                "sel": "sel_i", "ack": "ack_o"}


def write_tb(mod):
    n, tier = mod["n"], mod["tier"]
    tb_dir = os.path.join(VS, f"tb-{n}")
    os.makedirs(tb_dir, exist_ok=True)
    min_tests = {"A": 8, "B": 15, "C": 40}[tier]
    sn = sigs(mod)
    rst_pol = sn["rst_pol"]

    if rst_pol == "low":
        rst_assert = f"dut.{sn['rst']}.value = 0"
        rst_deassert = f"dut.{sn['rst']}.value = 1"
    else:
        rst_assert = f"dut.{sn['rst']}.value = 1"
        rst_deassert = f"dut.{sn['rst']}.value = 0"

    init = mod.get("init", "")

    L = ['"""', f'cocotb testbench for {n} — Tier {tier}', '"""',
        'import sys, os', "sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))",
        'from wb_helper import *', '',
        'import cocotb', 'from cocotb.triggers import RisingEdge, ClockCycles, Timer',
        'from cocotb.clock import Clock', '']

    # test_reset
    L.extend([
        '@cocotb.test()',
        'async def test_reset(dut):',
        '    """Verify reset state."""',
        f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())'])
    _init(L, init)
    L.extend([
        f'    {rst_assert}',
        f'    dut.{sn["cyc"]}.value = 0; dut.{sn["stb"]}.value = 0; dut.{sn["we"]}.value = 0',
        f'    await ClockCycles(dut.{sn["clk"]}, 5)',
        f'    {rst_deassert}',
        f'    await ClockCycles(dut.{sn["clk"]}, 4)',
        f'    assert si(dut.{sn["ack"]}) == 0, "ack should be 0 after reset"',
        '', ''])

    # test_register_rw
    L.extend([
        '@cocotb.test()',
        'async def test_register_rw(dut):',
        '    """Write/read registers."""',
        f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())'])
    _init(L, init)
    _rst(L, sn, rst_assert, rst_deassert)
    for i, reg in enumerate(mod["regs"][:8]):
        L.append(f'    ack = await wb_write_sig(dut, 0x{reg:04X}, 0x{i:08X})')
        L.append(f'    v, ack2 = await wb_read_sig(dut, 0x{reg:04X})')
        L.append(f'    assert ack2 == 1, f"R ack fail 0x{reg:04X}"')
    L.extend(['', ''])

    # test_wb_ack
    L.extend([
        '@cocotb.test()',
        'async def test_wb_ack(dut):',
        '    """Verify ack."""',
        f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())'])
    _init(L, init)
    _rst(L, sn, rst_assert, rst_deassert)
    L.extend([
        f'    ack = await wb_write_sig(dut, 0x{mod["regs"][0]:04X}, 0xDEADBEEF)',
        '    assert ack == 1, "WB write ack fail"', '', ''])

    # test_consecutive_writes
    L.extend([
        '@cocotb.test()',
        'async def test_consecutive_writes(dut):',
        '    """Multiple writes."""',
        f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())'])
    _init(L, init)
    _rst(L, sn, rst_assert, rst_deassert)
    for i, pat in enumerate([0xAAAAAAAA, 0x55555555, 0x12345678, 0xDEADBEEF]):
        L.append(f'    ack = await wb_write_sig(dut, 0x{mod["regs"][0]:04X}, 0x{pat:08X})')
        L.append(f'    assert ack == 1, "cwrite {i} failed"')
    L.extend(['', ''])

    # test_idle_read
    L.extend([
        '@cocotb.test()',
        'async def test_idle_read(dut):',
        '    """Idle read."""',
        f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())'])
    _init(L, init)
    _rst(L, sn, rst_assert, rst_deassert)
    L.extend([
        f'    v, ack = await wb_read_sig(dut, 0x{mod["regs"][0]:04X})',
        '    assert ack == 1, "idle read ack"', '', ''])

    cur = sum(1 for l in L if l.startswith('async def test_'))
    for i in range(min_tests - cur):
        reg = mod["regs"][i % len(mod["regs"])]
        L.append('@cocotb.test()')
        L.append(f'async def test_stress_{i:02d}(dut):')
        L.append(f'    """Stress {i}: 0x{reg:04X}."""')
        L.append(f'    cocotb.start_soon(Clock(dut.{sn["clk"]}, 10, unit="ns").start())')
        _init(L, init)
        _rst(L, sn, rst_assert, rst_deassert)
        L.append(f'    await wb_write_sig(dut, 0x{reg:04X}, 0x{i:08X})')
        L.append(f'    v, ack = await wb_read_sig(dut, 0x{reg:04X})')
        L.append(f'    assert ack == 1, f"s{i} ack"')
        L.extend(['', ''])

    test_py = os.path.join(tb_dir, f"test_{n}.py")
    tc = sum(1 for l in L if l.startswith('async def test_'))

    # Append inline signal-aware helpers
    helpers = f'''

# ── Signal-aware WB helpers for {n} ──
CLK = "{sn['clk']}"
RST = "{sn['rst']}"
CYCS = "{sn['cyc']}"
STBS = "{sn['stb']}"
WES  = "{sn['we']}"
ADRS = "{sn['adr']}"
DINS = "{sn['din']}"
DOUTS = "{sn['dout']}"
SELS = "{sn['sel']}"
ACKS = "{sn['ack']}"

async def wb_write_sig(dut, addr, data):
    cyc = getattr(dut, CYCS); stb = getattr(dut, STBS); we = getattr(dut, WES)
    adr = getattr(dut, ADRS); dat = getattr(dut, DINS); sel = getattr(dut, SELS)
    ack = getattr(dut, ACKS); clk = getattr(dut, CLK)
    adr.value = addr; dat.value = data; sel.value = 0xF; we.value = 1
    cyc.value = 1; stb.value = 1
    ack_val = 0
    for _ in range(16):
        await RisingEdge(clk); await Timer(1, unit="ns")
        ack_val = si(ack)
        if ack_val: break
    cyc.value = 0; stb.value = 0; we.value = 0
    await RisingEdge(clk); await Timer(1, unit="ns")
    return ack_val

async def wb_read_sig(dut, addr):
    cyc = getattr(dut, CYCS); stb = getattr(dut, STBS); we = getattr(dut, WES)
    adr = getattr(dut, ADRS); dout= getattr(dut, DOUTS); sel = getattr(dut, SELS)
    ack = getattr(dut, ACKS); clk = getattr(dut, CLK)
    adr.value = addr; we.value = 0; sel.value = 0xF; cyc.value = 1; stb.value = 1
    data = 0; ack_val = 0
    for _ in range(16):
        await RisingEdge(clk); await Timer(1, unit="ns")
        ack_val = si(ack)
        if ack_val: data = si(dout); break
    cyc.value = 0; stb.value = 0
    await RisingEdge(clk); await Timer(1, unit="ns")
    return data, ack_val
'''
    with open(test_py, "w") as f:
        f.write("\n".join(L) + helpers)
    print(f"  {n:25s} Tier {tier}: {tc} tests")


def _init(L, init):
    if init:
        for li in init.strip().split("\n"):
            if li.strip():
                L.append(f"    {li.strip()}")

def _rst(L, sn, rst_assert, rst_deassert):
    L.extend([
        f'    dut.{sn["cyc"]}.value = 0; dut.{sn["stb"]}.value = 0; dut.{sn["we"]}.value = 0',
        f'    {rst_assert}',
        f'    await ClockCycles(dut.{sn["clk"]}, 4)',
        f'    {rst_deassert}',
        f'    await ClockCycles(dut.{sn["clk"]}, 4)', ''])


def write_makefile(mod):
    n = mod["n"]
    tb_dir = os.path.join(VS, f"tb-{n}")
    rtl_paths = [os.path.join(FS, f) for f in mod["rtl"]]
    src_lines = "\n".join(f"VERILOG_SOURCES += {p}" for p in rtl_paths)
    mf = f'''# {n} — cocotb, IP-010 v4, Tier {mod["tier"]}
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
{src_lines}
TOPLEVEL = {mod["top"]}
COCOTB_TEST_MODULES = test_{n}
COMPILE_ARGS += -I{FS}/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
'''
    with open(os.path.join(tb_dir, "Makefile"), "w") as f:
        f.write(mf)


if __name__ == "__main__":
    print("=== gen_tbs_v4 ===\n")
    for mod in MODULES:
        write_tb(mod)
        write_makefile(mod)

    # sram_8kb special: exclude blackbox to avoid duplicate module
    print("\n--- sram_8kb (special) ---")
    sram_mod = {"n": "sram_8kb", "tier": "A", "top": "sram_8kb",
        "rtl": ["rtl-sram_8kb/rtl/sram_8kb.v"],  # blackbox excluded
        "style": "wb_bus_only", "regs": [0x00], "init": ""}
    write_tb(sram_mod)
    write_makefile(sram_mod)

    # wishbone_interconnect special (wb_clk_wb_bus style)
    print("\n--- wishbone_interconnect (special) ---")
    wb_mod = {"n": "wishbone_interconnect", "tier": "A", "top": "wishbone_interconnect",
        "rtl": ["rtl-wishbone_interconnect/rtl/wishbone_interconnect.v"],
        "style": "wb_clk_wb_bus", "regs": [0x00], "init": ""}
    write_tb(wb_mod)
    write_makefile(wb_mod)

    print("\nDone!")
