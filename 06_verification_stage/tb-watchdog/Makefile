# watchdog — cocotb, IP-010 v4, Tier B
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-watchdog/rtl/watchdog.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-watchdog/rtl/EF_WDT32_WB_wrapper.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-watchdog/rtl/EF_WDT32.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-watchdog/rtl/ef_util_lib.v
TOPLEVEL = EF_WDT32_WB
COCOTB_TEST_MODULES = test_watchdog
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
