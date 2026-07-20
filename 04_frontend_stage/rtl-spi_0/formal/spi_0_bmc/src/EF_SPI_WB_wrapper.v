// =========================================================================
// Module: EF_SPI_WB_wrapper
// Description: Wrapper for EF_SPI_WB — adapts FOSSi IP to architecture conventions
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_SPI_WB_wrapper (
    input  wire        wb_clk_i,
    input  wire        wb_rst_ni,

    // Wishbone B4 slave
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output wire [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output wire        wb_ack_o,
    output wire        wb_err_o,

    // SPI interface
    output wire        spi_sck_o,
    output wire        spi_mosi_o,
    input  wire        spi_miso_i,
    output wire        spi_cs_o,

    // Interrupt
    output wire        irq_done_o
);

    EF_SPI_WB u_ef_spi (
        .clk_i  (wb_clk_i),
        .rst_i  (~wb_rst_ni),
        .adr_i  (wb_adr_i),
        .dat_i  (wb_dat_i),
        .dat_o  (wb_dat_o),
        .sel_i  (wb_sel_i),
        .cyc_i  (wb_cyc_i),
        .stb_i  (wb_stb_i),
        .ack_o  (wb_ack_o),
        .we_i   (wb_we_i),
        .IRQ    (irq_done_o),
        .miso   (spi_miso_i),
        .mosi   (spi_mosi_o),
        .csb    (spi_cs_o),
        .sclk   (spi_sck_o)
    );

    assign wb_err_o = 1'b0;

endmodule
