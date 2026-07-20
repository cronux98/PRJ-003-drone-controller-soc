# gpio — cocotb, IP-010 v4, Tier B
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-gpio/rtl/gpio.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8_WB_wrapper.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-gpio/rtl/EF_GPIO8.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-gpio/rtl/ef_util_lib.v
TOPLEVEL = EF_GPIO8_WB
COCOTB_TEST_MODULES = test_gpio
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
