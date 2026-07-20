# wishbone_interconnect — cocotb, IP-010 v4, Tier A
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-wishbone_interconnect/rtl/wishbone_interconnect.v
TOPLEVEL = wishbone_interconnect
COCOTB_TEST_MODULES = test_wishbone_interconnect
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
