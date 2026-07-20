"""
cocotb testbench for gpio — Tier B
"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wb_helper import *

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_reset(dut):
    """Verify reset state."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.rst_i.value = 1
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)
    assert si(dut.ack_o) == 0, "ack should be 0 after reset"


@cocotb.test()
async def test_register_rw(dut):
    """Write/read registers."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    ack = await wb_write_sig(dut, 0x0000, 0x00000000)
    v, ack2 = await wb_read_sig(dut, 0x0000)
    assert ack2 == 1, f"R ack fail 0x0000"
    ack = await wb_write_sig(dut, 0x0004, 0x00000001)
    v, ack2 = await wb_read_sig(dut, 0x0004)
    assert ack2 == 1, f"R ack fail 0x0004"
    ack = await wb_write_sig(dut, 0x0008, 0x00000002)
    v, ack2 = await wb_read_sig(dut, 0x0008)
    assert ack2 == 1, f"R ack fail 0x0008"
    ack = await wb_write_sig(dut, 0xFF00, 0x00000003)
    v, ack2 = await wb_read_sig(dut, 0xFF00)
    assert ack2 == 1, f"R ack fail 0xFF00"
    ack = await wb_write_sig(dut, 0xFF04, 0x00000004)
    v, ack2 = await wb_read_sig(dut, 0xFF04)
    assert ack2 == 1, f"R ack fail 0xFF04"
    ack = await wb_write_sig(dut, 0xFF08, 0x00000005)
    v, ack2 = await wb_read_sig(dut, 0xFF08)
    assert ack2 == 1, f"R ack fail 0xFF08"
    ack = await wb_write_sig(dut, 0xFF0C, 0x00000006)
    v, ack2 = await wb_read_sig(dut, 0xFF0C)
    assert ack2 == 1, f"R ack fail 0xFF0C"


@cocotb.test()
async def test_wb_ack(dut):
    """Verify ack."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    ack = await wb_write_sig(dut, 0x0000, 0xDEADBEEF)
    assert ack == 1, "WB write ack fail"


@cocotb.test()
async def test_consecutive_writes(dut):
    """Multiple writes."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    ack = await wb_write_sig(dut, 0x0000, 0xAAAAAAAA)
    assert ack == 1, "cwrite 0 failed"
    ack = await wb_write_sig(dut, 0x0000, 0x55555555)
    assert ack == 1, "cwrite 1 failed"
    ack = await wb_write_sig(dut, 0x0000, 0x12345678)
    assert ack == 1, "cwrite 2 failed"
    ack = await wb_write_sig(dut, 0x0000, 0xDEADBEEF)
    assert ack == 1, "cwrite 3 failed"


@cocotb.test()
async def test_idle_read(dut):
    """Idle read."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, "idle read ack"


@cocotb.test()
async def test_stress_00(dut):
    """Stress 0: 0x0000."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x00000000)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s0 ack"


@cocotb.test()
async def test_stress_01(dut):
    """Stress 1: 0x0004."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x00000001)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s1 ack"


@cocotb.test()
async def test_stress_02(dut):
    """Stress 2: 0x0008."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000002)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s2 ack"


@cocotb.test()
async def test_stress_03(dut):
    """Stress 3: 0xFF00."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF00, 0x00000003)
    v, ack = await wb_read_sig(dut, 0xFF00)
    assert ack == 1, f"s3 ack"


@cocotb.test()
async def test_stress_04(dut):
    """Stress 4: 0xFF04."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF04, 0x00000004)
    v, ack = await wb_read_sig(dut, 0xFF04)
    assert ack == 1, f"s4 ack"


@cocotb.test()
async def test_stress_05(dut):
    """Stress 5: 0xFF08."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF08, 0x00000005)
    v, ack = await wb_read_sig(dut, 0xFF08)
    assert ack == 1, f"s5 ack"


@cocotb.test()
async def test_stress_06(dut):
    """Stress 6: 0xFF0C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF0C, 0x00000006)
    v, ack = await wb_read_sig(dut, 0xFF0C)
    assert ack == 1, f"s6 ack"


@cocotb.test()
async def test_stress_07(dut):
    """Stress 7: 0x0000."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x00000007)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s7 ack"


@cocotb.test()
async def test_stress_08(dut):
    """Stress 8: 0x0004."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x00000008)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s8 ack"


@cocotb.test()
async def test_stress_09(dut):
    """Stress 9: 0x0008."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.io_in.value = 0
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000009)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s9 ack"



# ── Signal-aware WB helpers for gpio ──
CLK = "clk_i"
RST = "rst_i"
CYCS = "cyc_i"
STBS = "stb_i"
WES  = "we_i"
ADRS = "adr_i"
DINS = "dat_i"
DOUTS = "dat_o"
SELS = "sel_i"
ACKS = "ack_o"

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
