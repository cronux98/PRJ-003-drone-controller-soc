# irq_ctrl — cocotb, IP-010 v4, Tier A
SIM = icarus
TOPLEVEL_LANG = verilog
COMPILE_ARGS = -g2005
VERILOG_SOURCES += ~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/rtl-irq_ctrl/rtl/irq_ctrl.v
TOPLEVEL = irq_ctrl
COCOTB_TEST_MODULES = test_irq_ctrl
COMPILE_ARGS += -I~/hermes_workspace/projects/IP-010/v4/04_frontend_stage/common/rtl
include $(shell cocotb-config --makefiles)/Makefile.sim
