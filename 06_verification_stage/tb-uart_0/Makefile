# uart_0 — cocotb, IP-010 v4, Tier B
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-uart_0/rtl/EF_UART_WB.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-uart_0/rtl/EF_UART_WB_wrapper.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-uart_0/rtl/EF_UART.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-uart_0/rtl/ef_util_lib.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-uart_0/rtl/axis_fifo.v
TOPLEVEL = EF_UART_WB
COCOTB_TEST_MODULES = test_uart_0
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
