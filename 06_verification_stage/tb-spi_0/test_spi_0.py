"""
cocotb testbench for spi_0 — Tier C
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
    ack = await wb_write_sig(dut, 0x001C, 0x00000007)
    v, ack2 = await wb_read_sig(dut, 0x001C)
    assert ack2 == 1, f"R ack fail 0x001C"


@cocotb.test()
async def test_wb_ack(dut):
    """Verify ack."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
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
    """Stress 3: 0x000C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x000C, 0x00000003)
    v, ack = await wb_read_sig(dut, 0x000C)
    assert ack == 1, f"s3 ack"


@cocotb.test()
async def test_stress_04(dut):
    """Stress 4: 0x0010."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0010, 0x00000004)
    v, ack = await wb_read_sig(dut, 0x0010)
    assert ack == 1, f"s4 ack"


@cocotb.test()
async def test_stress_05(dut):
    """Stress 5: 0x0014."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0014, 0x00000005)
    v, ack = await wb_read_sig(dut, 0x0014)
    assert ack == 1, f"s5 ack"


@cocotb.test()
async def test_stress_06(dut):
    """Stress 6: 0x0018."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0018, 0x00000006)
    v, ack = await wb_read_sig(dut, 0x0018)
    assert ack == 1, f"s6 ack"


@cocotb.test()
async def test_stress_07(dut):
    """Stress 7: 0x001C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x001C, 0x00000007)
    v, ack = await wb_read_sig(dut, 0x001C)
    assert ack == 1, f"s7 ack"


@cocotb.test()
async def test_stress_08(dut):
    """Stress 8: 0x0020."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0020, 0x00000008)
    v, ack = await wb_read_sig(dut, 0x0020)
    assert ack == 1, f"s8 ack"


@cocotb.test()
async def test_stress_09(dut):
    """Stress 9: 0x0024."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0024, 0x00000009)
    v, ack = await wb_read_sig(dut, 0x0024)
    assert ack == 1, f"s9 ack"


@cocotb.test()
async def test_stress_10(dut):
    """Stress 10: 0x0028."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0028, 0x0000000A)
    v, ack = await wb_read_sig(dut, 0x0028)
    assert ack == 1, f"s10 ack"


@cocotb.test()
async def test_stress_11(dut):
    """Stress 11: 0xFF00."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF00, 0x0000000B)
    v, ack = await wb_read_sig(dut, 0xFF00)
    assert ack == 1, f"s11 ack"


@cocotb.test()
async def test_stress_12(dut):
    """Stress 12: 0xFF04."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF04, 0x0000000C)
    v, ack = await wb_read_sig(dut, 0xFF04)
    assert ack == 1, f"s12 ack"


@cocotb.test()
async def test_stress_13(dut):
    """Stress 13: 0xFF08."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF08, 0x0000000D)
    v, ack = await wb_read_sig(dut, 0xFF08)
    assert ack == 1, f"s13 ack"


@cocotb.test()
async def test_stress_14(dut):
    """Stress 14: 0xFF0C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF0C, 0x0000000E)
    v, ack = await wb_read_sig(dut, 0xFF0C)
    assert ack == 1, f"s14 ack"


@cocotb.test()
async def test_stress_15(dut):
    """Stress 15: 0x0000."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x0000000F)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s15 ack"


@cocotb.test()
async def test_stress_16(dut):
    """Stress 16: 0x0004."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x00000010)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s16 ack"


@cocotb.test()
async def test_stress_17(dut):
    """Stress 17: 0x0008."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000011)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s17 ack"


@cocotb.test()
async def test_stress_18(dut):
    """Stress 18: 0x000C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x000C, 0x00000012)
    v, ack = await wb_read_sig(dut, 0x000C)
    assert ack == 1, f"s18 ack"


@cocotb.test()
async def test_stress_19(dut):
    """Stress 19: 0x0010."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0010, 0x00000013)
    v, ack = await wb_read_sig(dut, 0x0010)
    assert ack == 1, f"s19 ack"


@cocotb.test()
async def test_stress_20(dut):
    """Stress 20: 0x0014."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0014, 0x00000014)
    v, ack = await wb_read_sig(dut, 0x0014)
    assert ack == 1, f"s20 ack"


@cocotb.test()
async def test_stress_21(dut):
    """Stress 21: 0x0018."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0018, 0x00000015)
    v, ack = await wb_read_sig(dut, 0x0018)
    assert ack == 1, f"s21 ack"


@cocotb.test()
async def test_stress_22(dut):
    """Stress 22: 0x001C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x001C, 0x00000016)
    v, ack = await wb_read_sig(dut, 0x001C)
    assert ack == 1, f"s22 ack"


@cocotb.test()
async def test_stress_23(dut):
    """Stress 23: 0x0020."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0020, 0x00000017)
    v, ack = await wb_read_sig(dut, 0x0020)
    assert ack == 1, f"s23 ack"


@cocotb.test()
async def test_stress_24(dut):
    """Stress 24: 0x0024."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0024, 0x00000018)
    v, ack = await wb_read_sig(dut, 0x0024)
    assert ack == 1, f"s24 ack"


@cocotb.test()
async def test_stress_25(dut):
    """Stress 25: 0x0028."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0028, 0x00000019)
    v, ack = await wb_read_sig(dut, 0x0028)
    assert ack == 1, f"s25 ack"


@cocotb.test()
async def test_stress_26(dut):
    """Stress 26: 0xFF00."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF00, 0x0000001A)
    v, ack = await wb_read_sig(dut, 0xFF00)
    assert ack == 1, f"s26 ack"


@cocotb.test()
async def test_stress_27(dut):
    """Stress 27: 0xFF04."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF04, 0x0000001B)
    v, ack = await wb_read_sig(dut, 0xFF04)
    assert ack == 1, f"s27 ack"


@cocotb.test()
async def test_stress_28(dut):
    """Stress 28: 0xFF08."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF08, 0x0000001C)
    v, ack = await wb_read_sig(dut, 0xFF08)
    assert ack == 1, f"s28 ack"


@cocotb.test()
async def test_stress_29(dut):
    """Stress 29: 0xFF0C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0xFF0C, 0x0000001D)
    v, ack = await wb_read_sig(dut, 0xFF0C)
    assert ack == 1, f"s29 ack"


@cocotb.test()
async def test_stress_30(dut):
    """Stress 30: 0x0000."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0000, 0x0000001E)
    v, ack = await wb_read_sig(dut, 0x0000)
    assert ack == 1, f"s30 ack"


@cocotb.test()
async def test_stress_31(dut):
    """Stress 31: 0x0004."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0004, 0x0000001F)
    v, ack = await wb_read_sig(dut, 0x0004)
    assert ack == 1, f"s31 ack"


@cocotb.test()
async def test_stress_32(dut):
    """Stress 32: 0x0008."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0008, 0x00000020)
    v, ack = await wb_read_sig(dut, 0x0008)
    assert ack == 1, f"s32 ack"


@cocotb.test()
async def test_stress_33(dut):
    """Stress 33: 0x000C."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x000C, 0x00000021)
    v, ack = await wb_read_sig(dut, 0x000C)
    assert ack == 1, f"s33 ack"


@cocotb.test()
async def test_stress_34(dut):
    """Stress 34: 0x0010."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.cyc_i.value = 0; dut.stb_i.value = 0; dut.we_i.value = 0
    dut.rst_i.value = 1
    await ClockCycles(dut.clk_i, 4)
    dut.rst_i.value = 0
    await ClockCycles(dut.clk_i, 4)

    await wb_write_sig(dut, 0x0010, 0x00000022)
    v, ack = await wb_read_sig(dut, 0x0010)
    assert ack == 1, f"s34 ack"



# ── Signal-aware WB helpers for spi_0 ──
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
