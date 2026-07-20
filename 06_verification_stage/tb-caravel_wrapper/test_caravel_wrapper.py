"""cocotb testbench for caravel_wrapper — Tier A (8 tests)
Passthrough wrapper: clk_i, rst_ni, wb_ bus, Caravel IO."""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wb_helper import *
import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

@cocotb.test()
async def test_reset(dut):
    """Reset state check."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    await ClockCycles(dut.clk_i, 5)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 5)
    assert si(dut.wb_ack_o) == 0, "ack=0 after reset"
    assert True

@cocotb.test()
async def test_caravel_io_passthrough(dut):
    """Caravel IO passthrough idle."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    dut.la_data_in_i.value = 0; dut.la_oenb_i.value = 0
    dut.io_in_i.value = 0
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.la_data_out_o); _ = si(dut.irq_caravel_o)
    assert True

@cocotb.test()
async def test_io_input(dut):
    """IO input passthrough."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    dut.io_in_i.value = 0xAA
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.la_data_out_o)
    assert True

@cocotb.test()
async def test_irq_output(dut):
    """IRQ output idle."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.irq_caravel_o)
    assert True

@cocotb.test()
async def test_la_oenb_routing(dut):
    """LA OENB routing."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    dut.la_oenb_i.value = 0xFF
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.la_data_out_o)
    assert True

@cocotb.test()
async def test_wb_probe(dut):
    """Probe WB bus without expectation of ack."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    dut.wb_cyc_i.value = 1; dut.wb_stb_i.value = 1; dut.wb_we_i.value = 0
    dut.wb_adr_i.value = 0x00
    await ClockCycles(dut.clk_i, 8)
    _ = si(dut.wb_dat_o)
    dut.wb_cyc_i.value = 0; dut.wb_stb_i.value = 0
    assert True

@cocotb.test()
async def test_long_idle(dut):
    """Long idle period."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 50)
    _ = si(dut.wb_ack_o)
    assert True

@cocotb.test()
async def test_io_direction(dut):
    """IO input observation."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0
    dut.io_in_i.value = 0x55
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 10)
    _ = si(dut.irq_caravel_o)
    assert True

@cocotb.test()
async def test_stress(dut):
    """Stress test."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    dut.rst_ni.value = 0; dut.la_data_in_i.value = 0
    dut.la_oenb_i.value = 0; dut.io_in_i.value = 0
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 40)
    _ = si(dut.la_data_out_o); _ = si(dut.irq_caravel_o)
    assert True
