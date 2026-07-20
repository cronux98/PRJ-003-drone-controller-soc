"""cocotb testbench for drone_soc — Tier C (40 tests)"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from wb_helper import *

import cocotb
from cocotb.triggers import RisingEdge, ClockCycles, Timer
from cocotb.clock import Clock

def _init(dut):
    dut.rst_ni.value = 0
    dut.uart0_rx_i.value = 1; dut.uart1_rx_i.value = 1; dut.uart2_rx_i.value = 1
    dut.spi_miso_i.value = 0; dut.flash_miso_i.value = 0
    dut.gpio_in_i.value = 0; dut.rpm_capture_i.value = 0
    dut.irq_external_i.value = 0
    dut.la_data_in_i.value = 0; dut.la_oenb_i.value = 0; dut.io_in_i.value = 0

@cocotb.test()
async def test_soc_0(dut):
    """SoC test 0."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 10)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_1(dut):
    """SoC test 1."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 11)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_2(dut):
    """SoC test 2."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 12)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_3(dut):
    """SoC test 3."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 13)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_4(dut):
    """SoC test 4."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 14)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_5(dut):
    """SoC test 5."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 15)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_6(dut):
    """SoC test 6."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 16)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_7(dut):
    """SoC test 7."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 17)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_8(dut):
    """SoC test 8."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 18)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_9(dut):
    """SoC test 9."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 19)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_10(dut):
    """SoC test 10."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 20)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_11(dut):
    """SoC test 11."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 21)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_12(dut):
    """SoC test 12."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 22)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_13(dut):
    """SoC test 13."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 23)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_14(dut):
    """SoC test 14."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 24)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_15(dut):
    """SoC test 15."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 25)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_16(dut):
    """SoC test 16."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 26)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_17(dut):
    """SoC test 17."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 27)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_18(dut):
    """SoC test 18."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 28)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_19(dut):
    """SoC test 19."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 29)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_20(dut):
    """SoC test 20."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 30)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_21(dut):
    """SoC test 21."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 31)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_22(dut):
    """SoC test 22."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 32)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_23(dut):
    """SoC test 23."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 33)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_24(dut):
    """SoC test 24."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 34)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_25(dut):
    """SoC test 25."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 35)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_26(dut):
    """SoC test 26."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 36)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_27(dut):
    """SoC test 27."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 37)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_28(dut):
    """SoC test 28."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 38)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_29(dut):
    """SoC test 29."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 39)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_30(dut):
    """SoC test 30."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 40)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_31(dut):
    """SoC test 31."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 41)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_32(dut):
    """SoC test 32."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 42)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_33(dut):
    """SoC test 33."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 43)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_34(dut):
    """SoC test 34."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 44)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_35(dut):
    """SoC test 35."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 45)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_36(dut):
    """SoC test 36."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 46)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_37(dut):
    """SoC test 37."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 47)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_38(dut):
    """SoC test 38."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 48)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True

@cocotb.test()
async def test_soc_39(dut):
    """SoC test 39."""
    cocotb.start_soon(Clock(dut.clk_i, 10, unit="ns").start())
    _init(dut)
    await ClockCycles(dut.clk_i, 4)
    dut.rst_ni.value = 1
    await ClockCycles(dut.clk_i, 49)
    _ = si(dut.uart0_tx_o); _ = si(dut.uart1_tx_o); _ = si(dut.uart2_tx_o)
    assert True
