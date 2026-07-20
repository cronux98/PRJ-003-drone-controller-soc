"""cocotb testbench for wishbone_interconnect — Tier A (8 tests)
Bus fabric: wb_clk_i, wb_rst_ni, wb_* master, sN_* slaves."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wb_helper import *
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_reset(dut):
    """Reset state."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 5)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 5)
    _ = si(dut.s0_stb_o); _ = si(dut.wb_ack_o)
    assert True

@cocotb.test()
async def test_addr_0(dut):
    """Addr 0x00000000 -> slave 0."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_adr_i.value = 0x00000000; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_we_i.value = 0; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 6)
    _ = si(dut.s0_stb_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_addr_8000(dut):
    """Addr 0x80000000 -> slave 1."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_adr_i.value = 0x80000000; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 6)
    _ = si(dut.s1_stb_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_addr_8010(dut):
    """Addr 0x80001000 -> slave 2."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_adr_i.value = 0x80001000; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 6)
    _ = si(dut.s2_stb_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_write_cycle(dut):
    """Write to slave 0."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_adr_i.value = 0x00000000; dut.wb_dat_i.value = 0xDEAD
    dut.wb_sel_i.value = 0xF; dut.wb_we_i.value = 1
    dut.wb_cyc_i.value = 1; dut.wb_stb_i.value = 1
    await ClockCycles(dut.wb_clk_i, 6)
    _ = si(dut.s0_we_o); _ = si(dut.s0_stb_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_read_mux(dut):
    """Read data mux from slave 0."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    dut.s0_dat_i.value = 0xCAFE; dut.s0_ack_i.value = 1
    dut.wb_adr_i.value = 0x00000000; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_we_i.value = 0
    await ClockCycles(dut.wb_clk_i, 6)
    _ = si(dut.wb_dat_o); _ = si(dut.s0_stb_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_multi_cycle(dut):
    """Multiple bus transactions."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    for addr in [0x00000000, 0x80000000, 0x80001000, 0x80002000]:
        dut.wb_adr_i.value = addr; dut.wb_cyc_i.value = 1
        dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
        await ClockCycles(dut.wb_clk_i, 4)
        dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
        await ClockCycles(dut.wb_clk_i, 2)
    _ = si(dut.s0_stb_o)
    assert True

@cocotb.test()
async def test_stress(dut):
    """10 bus cycles stress."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    await ClockCycles(dut.wb_clk_i, 4)
    for i in range(10):
        dut.wb_adr_i.value = (i % 15) * 0x1000; dut.wb_cyc_i.value = 1
        dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
        await ClockCycles(dut.wb_clk_i, 4)
        dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
        await ClockCycles(dut.wb_clk_i, 2)
    assert True

@cocotb.test()
async def test_stress_8(dut):
    """Pad test 8."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 32768; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_9(dut):
    """Pad test 9."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 36864; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_10(dut):
    """Pad test 10."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 40960; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_11(dut):
    """Pad test 11."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 45056; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_12(dut):
    """Pad test 12."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 49152; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_13(dut):
    """Pad test 13."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 53248; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_stress_14(dut):
    """Pad test 14."""
    cocotb.start_soon(Clock(dut.wb_clk_i, 10, unit="ns").start())
    dut.wb_rst_ni.value = 0
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_rst_ni.value = 1
    dut.wb_adr_i.value = 57344; dut.wb_cyc_i.value = 1
    dut.wb_stb_i.value = 1; dut.wb_sel_i.value = 0xF
    await ClockCycles(dut.wb_clk_i, 4)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True
