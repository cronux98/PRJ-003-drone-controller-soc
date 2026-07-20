// user_defines.v — Caravel GPIO configuration for IP-010 v4 drone_soc
// Generated: 2026-07-19 | Agent: physical-design-agent (Hermes)
//
// GPIO 0-4: Reserved for Caravel housekeeping SPI (do NOT configure)
// GPIO 5-37: User GPIO — 33 pads available
//
// The drone_soc caravel_wrapper submodule bridges all I/O through
// the Caravel management SoC. Peripheral assignment is handled at
// firmware boot time via the caravel_bridge register interface.
//
// Default: all user GPIO configured as bidirectional with weak pull-up.

`ifndef USER_DEFINES_V
`define USER_DEFINES_V

// Number of I/O pads
`define MPRJ_IO_PADS_1 38
`define MPRJ_IO_PADS   `MPRJ_IO_PADS_1

// GPIO direction configuration (0 = input, 1 = output)
// GPIO 5-37 default to input (safe) until firmware configures them
`define MPRJ_IO_PADS_1_DIRECTION 38'h0000000000

// GPIO output enable (active-low: 0 = output enabled, 1 = input/hi-z)
// Default: all pads in input/hi-z mode (safe)
`define MPRJ_IO_PADS_1_OUTPUT_ENABLE 38'h3FFFFFFFFF

// GPIO output values (don't-care when pads are in input mode)
`define MPRJ_IO_PADS_1_OUTPUT_VALUE 38'h0000000000

`endif // USER_DEFINES_V
