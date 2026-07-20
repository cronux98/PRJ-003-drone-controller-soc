"""
Shared Wishbone B4 helper functions for cocotb testbenches.
IP-010 v4 — Drone Controller SoC Verification.
Used by all module testbenches.

Efabless WB wrapper signal convention:
  clk_i, rst_i, adr_i, dat_i, dat_o, sel_i, cyc_i, stb_i, ack_o, we_i
"""

import cocotb
from cocotb.triggers import RisingEdge, FallingEdge, ClockCycles, Timer
from cocotb.clock import Clock

def si(signal):
    """Safe int: read cocotb signal, return 0 for X/Z."""
    try:
        return int(signal.value)
    except (ValueError, TypeError):
        return 0

def sv(signal):
    """Safe value: return signal value or 0 if unknown."""
    try:
        v = signal.value
        if hasattr(v, 'integer'):
            return v.integer
        return int(v)
    except (ValueError, TypeError):
        return 0

async def reset_dut_activelow(dut, clk_signal, rst_signal, cycles=4):
    """Assert (low) and deassert (high) active-low reset."""
    rst_signal.value = 0
    await ClockCycles(clk_signal, cycles)
    rst_signal.value = 1
    await ClockCycles(clk_signal, 2)
    await Timer(1, unit='ns')

async def reset_dut_activehigh(dut, clk_signal, rst_signal, cycles=4):
    """Assert (high) and deassert (low) active-high reset."""
    rst_signal.value = 1
    await ClockCycles(clk_signal, cycles)
    rst_signal.value = 0
    await ClockCycles(clk_signal, 2)
    await Timer(1, unit='ns')

async def wb_write(dut, addr, data, cyc_sig=None, stb_sig=None, we_sig=None,
                   adr_sig=None, dat_i_sig=None, sel_sig=None, ack_sig=None):
    """Write to WB slave. Uses Efabless naming by default."""
    cyc = getattr(dut, cyc_sig) if cyc_sig else getattr(dut, 'cyc_i')
    stb = getattr(dut, stb_sig) if stb_sig else getattr(dut, 'stb_i')
    we = getattr(dut, we_sig) if we_sig else getattr(dut, 'we_i')
    adr = getattr(dut, adr_sig) if adr_sig else getattr(dut, 'adr_i')
    dat = getattr(dut, dat_i_sig) if dat_i_sig else getattr(dut, 'dat_i')
    sel = getattr(dut, sel_sig) if sel_sig else getattr(dut, 'sel_i')
    ack = getattr(dut, ack_sig) if ack_sig else getattr(dut, 'ack_o')

    adr.value = addr
    dat.value = data
    sel.value = 0xF
    we.value = 1
    cyc.value = 1
    stb.value = 1

    ack_val = 0
    for _ in range(16):
        await RisingEdge(dut.clk_i)
        await Timer(1, unit='ns')
        ack_val = si(ack)
        if ack_val == 1:
            break

    cyc.value = 0
    stb.value = 0
    we.value = 0
    await RisingEdge(dut.clk_i)
    await Timer(1, unit='ns')
    return ack_val

async def wb_read(dut, addr, cyc_sig=None, stb_sig=None, we_sig=None,
                  adr_sig=None, dat_o_sig=None, sel_sig=None, ack_sig=None):
    """Read from WB slave."""
    cyc = getattr(dut, cyc_sig) if cyc_sig else getattr(dut, 'cyc_i')
    stb = getattr(dut, stb_sig) if stb_sig else getattr(dut, 'stb_i')
    we  = getattr(dut, we_sig) if we_sig else getattr(dut, 'we_i')
    adr = getattr(dut, adr_sig) if adr_sig else getattr(dut, 'adr_i')
    dout= getattr(dut, dat_o_sig) if dat_o_sig else getattr(dut, 'dat_o')
    sel = getattr(dut, sel_sig) if sel_sig else getattr(dut, 'sel_i')
    ack = getattr(dut, ack_sig) if ack_sig else getattr(dut, 'ack_o')

    adr.value = addr
    we.value = 0
    sel.value = 0xF
    cyc.value = 1
    stb.value = 1

    data = 0
    ack_val = 0
    for _ in range(16):
        await RisingEdge(dut.clk_i)
        await Timer(1, unit='ns')
        ack_val = si(ack)
        if ack_val == 1:
            data = si(dout)
            break

    cyc.value = 0
    stb.value = 0
    await RisingEdge(dut.clk_i)
    await Timer(1, unit='ns')
    return data, ack_val
