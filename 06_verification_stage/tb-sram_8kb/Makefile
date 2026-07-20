# sram_8kb — cocotb, IP-010 v4, Tier A
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-sram_8kb/rtl/sram_8kb.v
TOPLEVEL = sram_8kb
COCOTB_TEST_MODULES = test_sram_8kb
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
