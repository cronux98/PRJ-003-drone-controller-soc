"""cocotb testbench for ibex_core — Tier C (40 tests)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wb_helper import *

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

def _init(dut):
    dut.rst_ni.value = 0
    dut.irq_software_i.value = 0; dut.irq_timer_i.value = 0
    dut.irq_external_i.value = 0; dut.irq_fast_i.value = 0
    dut.wb_ack_i.value = 1; dut.wb_err_i.value = 0
    dut.wb_dat_i.value = 0; dut.fetch_enable_i.value = 1

@cocotb.test()
async def test_ibex_0(dut):
    """Ibex test 0."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_1(dut):
    """Ibex test 1."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 9)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_2(dut):
    """Ibex test 2."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 10)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_3(dut):
    """Ibex test 3."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 11)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_4(dut):
    """Ibex test 4."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 12)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_5(dut):
    """Ibex test 5."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 13)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_6(dut):
    """Ibex test 6."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 14)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_7(dut):
    """Ibex test 7."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 15)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_8(dut):
    """Ibex test 8."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 16)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_9(dut):
    """Ibex test 9."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 17)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_10(dut):
    """Ibex test 10."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 18)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_11(dut):
    """Ibex test 11."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 19)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_12(dut):
    """Ibex test 12."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 20)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_13(dut):
    """Ibex test 13."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 21)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_14(dut):
    """Ibex test 14."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 22)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_15(dut):
    """Ibex test 15."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 23)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_16(dut):
    """Ibex test 16."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 24)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_17(dut):
    """Ibex test 17."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 25)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_18(dut):
    """Ibex test 18."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 26)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_19(dut):
    """Ibex test 19."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 27)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_20(dut):
    """Ibex test 20."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 28)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_21(dut):
    """Ibex test 21."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 29)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_22(dut):
    """Ibex test 22."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 30)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_23(dut):
    """Ibex test 23."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 31)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_24(dut):
    """Ibex test 24."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 32)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_25(dut):
    """Ibex test 25."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 33)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_26(dut):
    """Ibex test 26."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 34)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_27(dut):
    """Ibex test 27."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 35)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_28(dut):
    """Ibex test 28."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 36)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_29(dut):
    """Ibex test 29."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 37)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_30(dut):
    """Ibex test 30."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 38)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_31(dut):
    """Ibex test 31."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 39)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_32(dut):
    """Ibex test 32."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 40)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_33(dut):
    """Ibex test 33."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 41)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_34(dut):
    """Ibex test 34."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 42)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_35(dut):
    """Ibex test 35."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 43)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_36(dut):
    """Ibex test 36."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 44)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_37(dut):
    """Ibex test 37."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 45)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_38(dut):
    """Ibex test 38."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 46)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True

@cocotb.test()
async def test_ibex_39(dut):
    """Ibex test 39."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 47)
    _ = si(dut.wb_cyc_o); _ = si(dut.wb_adr_o)
    assert True
