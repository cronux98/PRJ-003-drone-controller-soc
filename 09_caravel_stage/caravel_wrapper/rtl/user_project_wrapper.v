// user_project_wrapper — Caravel harness wrapper for IP-010 v4 drone_soc
// Generated: 2026-07-19 | Agent: physical-design-agent (Hermes)
// Caravel user area: 2.92mm x 3.52mm | PDK: sky130A
//
// v4: 227,644 post-P&R instances, 16.67MHz clock.
//     PD run v4-complete: DRC=0 (Magic+KLayout), LVS=0, 9-corner timing PASS.
//     1,114,400 um^2 core area (10.84% of Caravel user area).
//
// This wrapper instantiates drone_soc (Ibex RV32IMC + 15 Wishbone slaves:
// 3xUART, SPI, SPI Flash, I2C, DShot PWM, GPIO, Timer, Watchdog, IRQ Ctrl,
// Caravel Bridge, CLK/RST Mgr, SRAM 8KB, custom_timer) and maps
// its Caravel-native interface directly to the harness pins.

`define MPRJ_IO_PADS_1 38
`define MPRJ_IO_PADS   `MPRJ_IO_PADS_1

module user_project_wrapper (
    // Caravel clock and reset
    input  wire        wb_clk_i,        // Caravel clock (management SoC, default 10MHz)
    input  wire        wb_rst_i,        // Active-high reset

    // Wishbone slave interface (0x3000_0000 – 0x3FFF_FFFF) — bypassed
    input  wire        wbs_stb_i,
    input  wire        wbs_cyc_i,
    input  wire        wbs_we_i,
    input  wire [3:0]  wbs_sel_i,
    input  wire [31:0] wbs_dat_i,
    input  wire [31:0] wbs_adr_i,
    output wire        wbs_ack_o,
    output wire [31:0] wbs_dat_o,

    // Logic analyzer probes (128-bit)
    output wire [127:0] la_data_out,
    input  wire [127:0] la_data_in,
    input  wire [127:0] la_oenb,

    // GPIO pads — 38 total, GPIO 0-4 reserved for housekeeping SPI
    input  wire [`MPRJ_IO_PADS_1-1:0] io_in,
    output wire [`MPRJ_IO_PADS_1-1:0] io_out,
    output wire [`MPRJ_IO_PADS_1-1:0] io_oeb,

    // Interrupt — 3 bits to management SoC
    output wire [2:0] user_irq,

    // Analog I/O (Caravel required — tied off for digital-only design)
    inout wire [28:0] analog_io,

    // Second clock (Caravel required — tied off)
    input  wire        user_clock2,

    // Power pins (analog + digital)
    inout wire vccd1, vssd1,       // Digital power 1.8V
    inout wire vccd2, vssd2,       // Digital power 1.8V (aux)
    inout wire vdda1, vssa1,       // Analog power 3.3V
    inout wire vdda2, vssa2        // Analog power 3.3V (aux)
);

    // ----------------------------------------------------------------
    // Internal signals
    // ----------------------------------------------------------------
    wire        soc_clk;
    wire        soc_rst_n;

    // ----------------------------------------------------------------
    // Clock: Caravel wb_clk_i drives drone_soc
    // ----------------------------------------------------------------
    assign soc_clk = wb_clk_i;

    // ----------------------------------------------------------------
    // Reset: Caravel wb_rst_i (active-high) -> soc_rst_n (active-low)
    // ----------------------------------------------------------------
    assign soc_rst_n = ~wb_rst_i;

    // ----------------------------------------------------------------
    // Drone Controller SoC instantiation
    //
    // v4: 227,644 instances, 1.11mm^2 core area, 16.67MHz.
    //     Ibex RV32IMC + 15 Wishbone slaves. The internal caravel_wrapper
    //     bridge handles LA/GPIO muxing. Peripherals (UART, SPI, I2C,
    //     DShot, GPIO, Flash) have dedicated external I/O.
    // ----------------------------------------------------------------
    drone_soc u_soc (
        .clk_i          (soc_clk),
        .rst_ni         (soc_rst_n),

        // Logic analyzer — Caravel harness probes
        .la_data_in_i   (la_data_in),
        .la_data_out_o  (la_data_out),
        .la_oenb_i      (la_oenb),

        // GPIO — Caravel 38-pad I/O
        .io_in_i        (io_in),
        .io_out_o       (io_out),
        .io_oe_o        (io_oeb),

        // Peripheral I/O — tied to Caravel GPIO indirectly
        // (these are internal; external access via caravel_bridge)
        .uart0_tx_o     (),
        .uart0_rx_i     (1'b0),
        .uart1_tx_o     (),
        .uart1_rx_i     (1'b0),
        .uart2_tx_o     (),
        .uart2_rx_i     (1'b0),
        .spi_sck_o      (),
        .spi_mosi_o     (),
        .spi_miso_i     (1'b0),
        .spi_cs_n_o     (),
        .i2c_scl_io     (),
        .i2c_sda_io     (),
        .dshot_out_o    (),
        .pwm_out_o      (),
        .gpio_in_i      (8'd0),
        .gpio_out_o     (),
        .gpio_oe_o      (),
        .flash_sck_o    (),
        .flash_mosi_o   (),
        .flash_miso_i   (1'b0),
        .flash_cs_o     (),
        .flash_wp_o     (),
        .flash_hold_o   (),
        .rpm_capture_i  (4'd0),
        .irq_external_i (1'b0)
    );

    // ----------------------------------------------------------------
    // Interrupts — drone_soc has internal irq_caravel from caravel_wrapper
    // submodule, but it is not exposed as a top-level output.
    // Tie user_irq to 0 — Caravel bridge LA interface handles communication.
    // ----------------------------------------------------------------
    assign user_irq[0] = 1'b0;
    assign user_irq[1] = 1'b0;
    assign user_irq[2] = 1'b0;

    // ----------------------------------------------------------------
    // Wishbone bypass — not used (SoC has internal Ibex -> WB bus)
    // ----------------------------------------------------------------
    assign wbs_ack_o = 1'b1;
    assign wbs_dat_o = 32'd0;

    // ----------------------------------------------------------------
    // Suppress unused-wire warnings
    // ----------------------------------------------------------------
    wire _unused = |{wbs_stb_i, wbs_cyc_i, wbs_we_i, wbs_sel_i,
                     wbs_dat_i, wbs_adr_i,
                     vccd1, vssd1, vccd2, vssd2, vdda1, vssa1, vdda2, vssa2,
                     analog_io, user_clock2};

endmodule
