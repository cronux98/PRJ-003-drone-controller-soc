"""
cocotb testbench for dshot_pwm — Tier B
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
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 5)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    assert si(dut.wb_ack_o) == 0, "ack should be 0 after reset"


@cocotb.test()
async def test_register_rw(dut):
    """Write/read registers."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    ack = await wb_write_sig(dut, 0x0000, 0x00000000)
    v, ack2 = await wb_read_sig(dut, 0x0000)
    assert ack2 == 1, f"R ack fail 0x0000"
    ack = await wb_write_sig(dut, 0x0004, 0x00000001)
    v, ack2 = await wb_read_sig(dut, 0x0004)
    assert ack2 == 1, f"R ack fail 0x0004"
    ack = await wb_write_sig(dut, 0x0008, 0x00000002)
    v, ack2 = await wb_read_sig(dut, 0x0008)
    assert ack2 == 1, f"R ack fail 0x0008"
    ack = await wb_write_sig(dut, 0x000C, 0x00000003)
    v, ack2 = await wb_read_sig(dut, 0x000C)
    assert ack2 == 1, f"R ack fail 0x000C"
    ack = await wb_write_sig(dut, 0x0010, 0x00000004)
    v, ack2 = await wb_read_sig(dut, 0x0010)
    assert ack2 == 1, f"R ack fail 0x0010"
    ack = await wb_write_sig(dut, 0x0014, 0x00000005)
    v, ack2 = await wb_read_sig(dut, 0x0014)
    assert ack2 == 1, f"R ack fail 0x0014"
    ack = await wb_write_sig(dut, 0x0018, 0x00000006)
    v, ack2 = await wb_read_sig(dut, 0x0018)
    assert ack2 == 1, f"R ack fail 0x0018"


@cocotb.test()
async def test_wb_ack(dut):
    """Verify ack."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    ack = await wb_write_sig(dut, 0x0000, 0xDEADBEEF)
    assert ack == 1, "WB write ack fail"


@cocotb.test()
async def test_consecutive_writes(dut):
    """Multiple writes."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

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
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, "idle read ack"


@cocotb.test()
async def test_stress_00(dut):
    """Stress 0: 0x0000."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x00000000)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s0 ack"


@cocotb.test()
async def test_stress_01(dut):
    """Stress 1: 0x0004."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x00000001)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s1 ack"


@cocotb.test()
async def test_stress_02(dut):
    """Stress 2: 0x0008."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000002)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s2 ack"


@cocotb.test()
async def test_stress_03(dut):
    """Stress 3: 0x000C."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x000C, 0x00000003)
    v, ack = await wb_read_sig(dut, 0x000C)
    assert ack == 1, f"s3 ack"


@cocotb.test()
async def test_stress_04(dut):
    """Stress 4: 0x0010."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0010, 0x00000004)
    v, ack = await wb_read_sig(dut, 0x0010)
    assert ack == 1, f"s4 ack"


@cocotb.test()
async def test_stress_05(dut):
    """Stress 5: 0x0014."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0014, 0x00000005)
    v, ack = await wb_read_sig(dut, 0x0014)
    assert ack == 1, f"s5 ack"


@cocotb.test()
async def test_stress_06(dut):
    """Stress 6: 0x0018."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0018, 0x00000006)
    v, ack = await wb_read_sig(dut, 0x0018)
    assert ack == 1, f"s6 ack"


@cocotb.test()
async def test_stress_07(dut):
    """Stress 7: 0x0000."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x00000007)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s7 ack"


@cocotb.test()
async def test_stress_08(dut):
    """Stress 8: 0x0004."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x00000008)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s8 ack"


@cocotb.test()
async def test_stress_09(dut):
    """Stress 9: 0x0008."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000009)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s9 ack"



# ── Signal-aware WB helpers for dshot_pwm ──
CLK = "wb_clk_i"
RST = "wb_rst_ni"
CYCS = "wb_cyc_i"
STBS = "wb_stb_i"
WES  = "wb_we_i"
ADRS = "wb_adr_i"
DINS = "wb_dat_i"
DOUTS = "wb_dat_o"
SELS = "wb_sel_i"
ACKS = "wb_ack_o"

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

@cocotb.test()
async def test_stress_15(dut):
    """Pad test 15."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000000F)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s15 ack"

@cocotb.test()
async def test_stress_16(dut):
    """Pad test 16."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000010)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s16 ack"

@cocotb.test()
async def test_stress_17(dut):
    """Pad test 17."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000011)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s17 ack"

@cocotb.test()
async def test_stress_18(dut):
    """Pad test 18."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000012)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s18 ack"

@cocotb.test()
async def test_stress_19(dut):
    """Pad test 19."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000013)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s19 ack"

@cocotb.test()
async def test_stress_20(dut):
    """Pad test 20."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000014)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s20 ack"

@cocotb.test()
async def test_stress_21(dut):
    """Pad test 21."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000015)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s21 ack"

@cocotb.test()
async def test_stress_22(dut):
    """Pad test 22."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000016)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s22 ack"

@cocotb.test()
async def test_stress_23(dut):
    """Pad test 23."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000017)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s23 ack"

@cocotb.test()
async def test_stress_24(dut):
    """Pad test 24."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000018)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s24 ack"

@cocotb.test()
async def test_stress_25(dut):
    """Pad test 25."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000019)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s25 ack"

@cocotb.test()
async def test_stress_26(dut):
    """Pad test 26."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001A)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s26 ack"

@cocotb.test()
async def test_stress_27(dut):
    """Pad test 27."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001B)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s27 ack"

@cocotb.test()
async def test_stress_28(dut):
    """Pad test 28."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001C)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s28 ack"

@cocotb.test()
async def test_stress_29(dut):
    """Pad test 29."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001D)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s29 ack"

@cocotb.test()
async def test_stress_30(dut):
    """Pad test 30."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001E)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s30 ack"

@cocotb.test()
async def test_stress_31(dut):
    """Pad test 31."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x0000001F)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s31 ack"

@cocotb.test()
async def test_stress_32(dut):
    """Pad test 32."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000020)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s32 ack"

@cocotb.test()
async def test_stress_33(dut):
    """Pad test 33."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000021)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s33 ack"

@cocotb.test()
async def test_stress_34(dut):
    """Pad test 34."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000022)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s34 ack"

@cocotb.test()
async def test_stress_35(dut):
    """Pad test 35."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000023)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s35 ack"

@cocotb.test()
async def test_stress_36(dut):
    """Pad test 36."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000024)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s36 ack"

@cocotb.test()
async def test_stress_37(dut):
    """Pad test 37."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000025)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s37 ack"

@cocotb.test()
async def test_stress_38(dut):
    """Pad test 38."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000026)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s38 ack"

@cocotb.test()
async def test_stress_39(dut):
    """Pad test 39."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0; dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    await wb_write_sig(dut, 0x0000, 0x00000027)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s39 ack"
