# spi_flash_ctrl — cocotb, IP-010 v4, Tier B
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-spi_flash_ctrl/rtl/spi_flash_ctrl.v
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-spi_flash_ctrl/rtl/spi_master.v
TOPLEVEL = spi_flash_ctrl
COCOTB_TEST_MODULES = test_spi_flash_ctrl
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
