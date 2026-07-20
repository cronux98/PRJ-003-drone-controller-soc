// =========================================================================
// Module: drone_soc
// Description: IP-010 v4 Drone Controller SoC Top-Level
//              Instantiates Ibex RV32IMC + Wishbone interconnect + 15 slaves
//
// Source: IP-010 v4 Architecture — Top-Level Integration
// Clock: 16.67 MHz (sys_clk, single domain)
// Bus: Wishbone B4 shared, 15-slave one-hot decoder
// Memory: 8KB unified SRAM (blackbox)
//
// Block Diagram:
//   ibex_core (Wishbone master)
//     → wishbone_interconnect (15-slave decoder)
//       ├── sram_8kb          @ 0x0000_0000
//       ├── uart_0            @ 0x8000_0000
//       ├── uart_1            @ 0x8000_1000
//       ├── uart_2            @ 0x8000_2000
//       ├── spi_0             @ 0x8000_3000
//       ├── i2c_0             @ 0x8000_4000
//       ├── dshot_pwm         @ 0x8000_5000
//       ├── gpio              @ 0x8000_6000
//       ├── spi_flash_ctrl    @ 0x8000_7000
//       ├── irq_ctrl          @ 0x8000_8000
//       ├── timer             @ 0x8000_9000
//       ├── watchdog          @ 0x8000_A000
//       ├── caravel_wrapper   @ 0x8000_B000
//       ├── clk_rst_mgr       @ 0x8000_C000
//       └── custom_timer      @ 0x8000_D000
// =========================================================================

module drone_soc (
    // Clock and reset
    input  wire        clk_i,
    input  wire        rst_ni,

    // UART 0 (GPS) — external pins
    output wire        uart0_tx_o,
    input  wire        uart0_rx_i,

    // UART 1 (RC receiver) — external pins
    output wire        uart1_tx_o,
    input  wire        uart1_rx_i,

    // UART 2 (Telemetry/debug) — external pins
    output wire        uart2_tx_o,
    input  wire        uart2_rx_i,

    // SPI 0 (IMU sensor)
    output wire        spi_sck_o,
    output wire        spi_mosi_o,
    input  wire        spi_miso_i,
    output wire [3:0]  spi_cs_n_o,

    // I2C 0 (Barometer + Magnetometer)
    inout  wire        i2c_scl_io,
    inout  wire        i2c_sda_io,

    // DShot PWM
    output wire [3:0]  dshot_out_o,
    output wire [1:0]  pwm_out_o,

    // GPIO
    input  wire [7:0]  gpio_in_i,
    output wire [7:0]  gpio_out_o,
    output wire [7:0]  gpio_oe_o,

    // SPI Flash
    output wire        flash_sck_o,
    output wire        flash_mosi_o,
    input  wire        flash_miso_i,
    output wire        flash_cs_o,
    output wire        flash_wp_o,
    output wire        flash_hold_o,

    // Caravel wrapper — external Caravel harness
    input  wire [127:0] la_data_in_i,
    output wire [127:0] la_data_out_o,
    input  wire [127:0] la_oenb_i,
    input  wire [37:0]  io_in_i,
    output wire [37:0]  io_out_o,
    output wire [37:0]  io_oe_o,

    // RPM capture (ESC telemetry)
    input  wire [3:0]  rpm_capture_i,

    // External interrupt input
    input  wire        irq_external_i
);

    // -----------------------------------------------------------------
    // Internal Wishbone bus — master to interconnect
    // -----------------------------------------------------------------
    wire [31:0] m_wb_adr;
    wire [31:0] m_wb_dat_o;
    wire [31:0] m_wb_dat_i;
    wire [ 3:0] m_wb_sel;
    wire        m_wb_we;
    wire        m_wb_stb;
    wire        m_wb_cyc;
    wire        m_wb_ack;
    wire        m_wb_err;

    // -----------------------------------------------------------------
    // Interconnect to slaves — one-hot select + per-slave buses
    // -----------------------------------------------------------------
    wire [14:0] slave_sel;
    wire [31:0] s_wb_dat [0:14];
    wire [14:0] s_wb_ack;
    wire [14:0] s_wb_err;

    // -----------------------------------------------------------------
    // Interrupt lines
    // -----------------------------------------------------------------
    wire        irq_caravel;
    wire        irq_watchdog;
    wire        irq_timer_overflow;
    wire        irq_spi_done;
    wire        irq_uart1_rx;
    wire        irq_uart0_rx;
    wire        irq_uart2_rx;
    wire        irq_i2c_done;
    wire [3:0]  irq_gpio;
    wire        irq_timer_capture;
    wire        irq_rpm;
    wire        irq_dshot_update;

    wire        m_irq;
    wire [15:0] irq_sources;

    // -----------------------------------------------------------------
    // Reset and clock distribution
    // -----------------------------------------------------------------
    wire        wb_rst_n;
    wire        cpu_rst_n;
    wire        wdg_rst_req;

    // clk_rst_mgr distributes reset
    assign wb_rst_n  = rst_ni;  // Simplified: single reset domain
    assign cpu_rst_n = rst_ni;

    // -----------------------------------------------------------------
    // Ibex RV32IMC Core (Wishbone master)
    // -----------------------------------------------------------------
    ibex_core u_ibex (
        .clk_i   (clk_i),
        .rst_ni  (cpu_rst_n),
        .wb_adr_o   (m_wb_adr),
        .wb_dat_o   (m_wb_dat_o),
        .wb_dat_i   (m_wb_dat_i),
        .wb_sel_o   (m_wb_sel),
        .wb_we_o    (m_wb_we),
        .wb_stb_o   (m_wb_stb),
        .wb_cyc_o   (m_wb_cyc),
        .wb_ack_i   (m_wb_ack),
        .wb_err_i   (m_wb_err),
        .irq_external_i (m_irq)
    );

    // -----------------------------------------------------------------
    // Wishbone Interconnect (15-slave decoder)
    // -----------------------------------------------------------------
    wb_interconnect_bus #(
        .NUM_SLAVES (15)
    ) u_interconnect (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        // Master side
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (m_wb_dat_i),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (m_wb_stb),
        .wb_cyc_i   (m_wb_cyc),
        .wb_ack_o   (m_wb_ack),
        .wb_err_o   (m_wb_err),
        // Slave side
        .slave_sel_o    (slave_sel),
        .s_wb_dat_i_0  (s_wb_dat[0]),
        .s_wb_dat_i_1  (s_wb_dat[1]),
        .s_wb_dat_i_2  (s_wb_dat[2]),
        .s_wb_dat_i_3  (s_wb_dat[3]),
        .s_wb_dat_i_4  (s_wb_dat[4]),
        .s_wb_dat_i_5  (s_wb_dat[5]),
        .s_wb_dat_i_6  (s_wb_dat[6]),
        .s_wb_dat_i_7  (s_wb_dat[7]),
        .s_wb_dat_i_8  (s_wb_dat[8]),
        .s_wb_dat_i_9  (s_wb_dat[9]),
        .s_wb_dat_i_10  (s_wb_dat[10]),
        .s_wb_dat_i_11  (s_wb_dat[11]),
        .s_wb_dat_i_12  (s_wb_dat[12]),
        .s_wb_dat_i_13  (s_wb_dat[13]),
        .s_wb_dat_i_14  (s_wb_dat[14]),
        .s_wb_ack_i_0  (s_wb_ack[0]),
        .s_wb_ack_i_1  (s_wb_ack[1]),
        .s_wb_ack_i_2  (s_wb_ack[2]),
        .s_wb_ack_i_3  (s_wb_ack[3]),
        .s_wb_ack_i_4  (s_wb_ack[4]),
        .s_wb_ack_i_5  (s_wb_ack[5]),
        .s_wb_ack_i_6  (s_wb_ack[6]),
        .s_wb_ack_i_7  (s_wb_ack[7]),
        .s_wb_ack_i_8  (s_wb_ack[8]),
        .s_wb_ack_i_9  (s_wb_ack[9]),
        .s_wb_ack_i_10  (s_wb_ack[10]),
        .s_wb_ack_i_11  (s_wb_ack[11]),
        .s_wb_ack_i_12  (s_wb_ack[12]),
        .s_wb_ack_i_13  (s_wb_ack[13]),
        .s_wb_ack_i_14  (s_wb_ack[14]),
        .s_wb_err_i_0  (s_wb_err[0]),
        .s_wb_err_i_1  (s_wb_err[1]),
        .s_wb_err_i_2  (s_wb_err[2]),
        .s_wb_err_i_3  (s_wb_err[3]),
        .s_wb_err_i_4  (s_wb_err[4]),
        .s_wb_err_i_5  (s_wb_err[5]),
        .s_wb_err_i_6  (s_wb_err[6]),
        .s_wb_err_i_7  (s_wb_err[7]),
        .s_wb_err_i_8  (s_wb_err[8]),
        .s_wb_err_i_9  (s_wb_err[9]),
        .s_wb_err_i_10  (s_wb_err[10]),
        .s_wb_err_i_11  (s_wb_err[11]),
        .s_wb_err_i_12  (s_wb_err[12]),
        .s_wb_err_i_13  (s_wb_err[13]),
        .s_wb_err_i_14  (s_wb_err[14])
    );

    // -----------------------------------------------------------------
    // Slave 0: SRAM 8KB @ 0x0000_0000
    // -----------------------------------------------------------------
    sram_8kb u_sram (
        .clk_i      (clk_i),
        .rst_ni     (wb_rst_n),
        .wb_adr_i   (m_wb_adr[12:0]),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[0]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[0] && m_wb_stb),
        .wb_cyc_i   (slave_sel[0] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[0])
    );

    // -----------------------------------------------------------------
    // Slave 1: UART 0 (GPS) @ 0x8000_0000
    // -----------------------------------------------------------------
    EF_UART_WB_wrapper u_uart0 (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[1]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[1] && m_wb_stb),
        .wb_cyc_i   (slave_sel[1] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[1]),
        .wb_err_o   (s_wb_err[1]),
        .uart_tx_o  (uart0_tx_o),
        .uart_rx_i  (uart0_rx_i),
        .irq_rx_o   (irq_uart0_rx)
    );

    // -----------------------------------------------------------------
    // Slave 2: UART 1 (RC Receiver) @ 0x8000_1000
    // -----------------------------------------------------------------
    EF_UART_WB_wrapper u_uart1 (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[2]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[2] && m_wb_stb),
        .wb_cyc_i   (slave_sel[2] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[2]),
        .wb_err_o   (s_wb_err[2]),
        .uart_tx_o  (uart1_tx_o),
        .uart_rx_i  (uart1_rx_i),
        .irq_rx_o   (irq_uart1_rx)
    );

    // -----------------------------------------------------------------
    // Slave 3: UART 2 (Telemetry) @ 0x8000_2000
    // -----------------------------------------------------------------
    EF_UART_WB_wrapper u_uart2 (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[3]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[3] && m_wb_stb),
        .wb_cyc_i   (slave_sel[3] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[3]),
        .wb_err_o   (s_wb_err[3]),
        .uart_tx_o  (uart2_tx_o),
        .uart_rx_i  (uart2_rx_i),
        .irq_rx_o   (irq_uart2_rx)
    );

    // -----------------------------------------------------------------
    // Slave 4: SPI 0 (IMU) @ 0x8000_3000
    // -----------------------------------------------------------------
    EF_SPI_WB_wrapper u_spi0 (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[4]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[4] && m_wb_stb),
        .wb_cyc_i   (slave_sel[4] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[4]),
        .wb_err_o   (s_wb_err[4]),
        .spi_sck_o  (spi_sck_o),
        .spi_mosi_o (spi_mosi_o),
        .spi_miso_i (spi_miso_i),
        .spi_cs_o (spi_cs_n_o[0]),
        .irq_done_o (irq_spi_done)
    );

    // Pad unused SPI CS bits to 1 (deasserted)
    assign spi_cs_n_o[3:1] = 3'b111;

    // -----------------------------------------------------------------
    // Slave 5: I2C 0 (Barometer + Magnetometer) @ 0x8000_4000
    // -----------------------------------------------------------------
    EF_I2C_WB_wrapper u_i2c0 (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[5]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[5] && m_wb_stb),
        .wb_cyc_i   (slave_sel[5] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[5]),
        .wb_err_o   (s_wb_err[5]),
        .i2c_scl_o (i2c_scl_io),
        .i2c_sda_o (i2c_sda_io),
        .i2c_sda_i (i2c_sda_io),
        .irq_done_o (irq_i2c_done)
    );

    // -----------------------------------------------------------------
    // Slave 6: DShot PWM @ 0x8000_5000
    // -----------------------------------------------------------------
    dshot_pwm u_dshot (
        .wb_clk_i       (clk_i),
        .wb_rst_ni      (wb_rst_n),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[6]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[6] && m_wb_stb),
        .wb_cyc_i       (slave_sel[6] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[6]),
        .wb_err_o       (s_wb_err[6]),
        .dshot_out_o    (dshot_out_o),
        .pwm_out_o      (pwm_out_o),
        .irq_update_o   (irq_dshot_update)
    );

    // -----------------------------------------------------------------
    // Slave 7: GPIO @ 0x8000_6000
    // -----------------------------------------------------------------
    EF_GPIO8_WB_wrapper u_gpio (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[7]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[7] && m_wb_stb),
        .wb_cyc_i   (slave_sel[7] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[7]),
        .wb_err_o   (s_wb_err[7]),
        .gpio_in_i  (gpio_in_i),
        .gpio_out_o (gpio_out_o),
        .gpio_oe_o  (gpio_oe_o),
        .irq_gpio_o (irq_gpio)
    );

    // -----------------------------------------------------------------
    // Slave 8: SPI Flash Controller @ 0x8000_7000
    // -----------------------------------------------------------------
    spi_flash_ctrl u_flash (
        .wb_clk_i       (clk_i),
        .wb_rst_ni      (wb_rst_n),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[8]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[8] && m_wb_stb),
        .wb_cyc_i       (slave_sel[8] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[8]),
        .wb_err_o       (s_wb_err[8]),
        .flash_sck_o    (flash_sck_o),
        .flash_mosi_o   (flash_mosi_o),
        .flash_miso_i   (flash_miso_i),
        .flash_cs_o     (flash_cs_o),
        .flash_wp_o     (flash_wp_o),
        .flash_hold_o   (flash_hold_o)
    );

    // -----------------------------------------------------------------
    // Slave 9: Interrupt Controller @ 0x8000_8000
    // -----------------------------------------------------------------
    assign irq_sources = {
        3'd0, irq_rpm, irq_timer_capture,
        irq_gpio[3], irq_gpio[2], irq_gpio[1], irq_gpio[0],
        irq_i2c_done, irq_uart2_rx, irq_uart0_rx, irq_uart1_rx,
        irq_spi_done, irq_timer_overflow, irq_watchdog, irq_caravel
    };

    irq_ctrl u_irq (
        .clk_i   (clk_i),
        .rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[9]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[9] && m_wb_stb),
        .wb_cyc_i   (slave_sel[9] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[9]),
        .irq_src_i  (irq_sources),
        .m_irq_o    (m_irq)
    );

    // -----------------------------------------------------------------
    // Slave 10: Timer @ 0x8000_9000
    // -----------------------------------------------------------------
    EF_TMR32_WB_wrapper u_timer (
        .wb_clk_i       (clk_i),
        .wb_rst_ni      (wb_rst_n),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[10]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[10] && m_wb_stb),
        .wb_cyc_i       (slave_sel[10] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[10]),
        .wb_err_o       (s_wb_err[10]),
        .irq_overflow_o (irq_timer_overflow),
        .irq_capture_o  (irq_timer_capture)
    );

    // -----------------------------------------------------------------
    // Slave 11: Watchdog @ 0x8000_A000
    // -----------------------------------------------------------------
    EF_WDT32_WB_wrapper u_watchdog (
        .wb_clk_i   (clk_i),
        .wb_rst_ni  (wb_rst_n),
        .wb_adr_i   (m_wb_adr),
        .wb_dat_i   (m_wb_dat_o),
        .wb_dat_o   (s_wb_dat[11]),
        .wb_sel_i   (m_wb_sel),
        .wb_we_i    (m_wb_we),
        .wb_stb_i   (slave_sel[11] && m_wb_stb),
        .wb_cyc_i   (slave_sel[11] && m_wb_cyc),
        .wb_ack_o   (s_wb_ack[11]),
        .wb_err_o   (s_wb_err[11]),
        .irq_warn_o (irq_watchdog),
        .rst_req_o (wdg_rst_req)
    );

    // -----------------------------------------------------------------
    // Slave 12: Caravel Wrapper @ 0x8000_B000
    // -----------------------------------------------------------------
    caravel_wrapper u_caravel (
        .clk_i          (clk_i),
        .rst_ni         (wb_rst_n),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[12]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[12] && m_wb_stb),
        .wb_cyc_i       (slave_sel[12] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[12]),
        .la_data_in_i   (la_data_in_i),
        .la_data_out_o  (la_data_out_o),
        .la_oenb_i      (la_oenb_i),
        .io_in_i        (io_in_i),
        .irq_caravel_o  (irq_caravel),
        .ready_i        (1'b1)
    );

    // Caravel IO passthrough
    assign io_out_o = 38'd0;
    assign io_oe_o  = 38'd0;

    // -----------------------------------------------------------------
    // Slave 13: CLK/RST Manager @ 0x8000_C000
    // -----------------------------------------------------------------
    clk_rst_mgr u_clkrst (
        .clk_i       (clk_i),
        .rst_ni      (rst_ni),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[13]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[13] && m_wb_stb),
        .wb_cyc_i       (slave_sel[13] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[13]),
        .wdg_rst_req_i  (wdg_rst_req)
    );

    // -----------------------------------------------------------------
    // Slave 14: Custom Timer (RPM telemetry) @ 0x8000_D000
    // -----------------------------------------------------------------
    custom_timer u_custom_timer (
        .wb_clk_i       (clk_i),
        .wb_rst_ni      (wb_rst_n),
        .wb_adr_i       (m_wb_adr),
        .wb_dat_i       (m_wb_dat_o),
        .wb_dat_o       (s_wb_dat[14]),
        .wb_sel_i       (m_wb_sel),
        .wb_we_i        (m_wb_we),
        .wb_stb_i       (slave_sel[14] && m_wb_stb),
        .wb_cyc_i       (slave_sel[14] && m_wb_cyc),
        .wb_ack_o       (s_wb_ack[14]),
        .wb_err_o       (s_wb_err[14]),
        .rpm_capture_i  (rpm_capture_i),
        .irq_rpm_o      (irq_rpm)
    );

endmodule
