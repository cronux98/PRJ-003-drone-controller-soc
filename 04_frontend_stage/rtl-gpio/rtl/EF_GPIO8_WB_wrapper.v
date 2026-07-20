// =========================================================================
// Module: EF_GPIO8_WB_wrapper
// Description: Wrapper for EF_GPIO8_WB — adapts FOSSi IP to architecture conventions
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_GPIO8_WB_wrapper (
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

    // GPIO interface
    input  wire [ 7:0] gpio_in_i,
    output wire [ 7:0] gpio_out_o,
    output wire [ 7:0] gpio_oe_o,

    // Interrupts (4 pins)
    output wire [ 3:0] irq_gpio_o
);

    // EF_GPIO8 has single IRQ output
    wire irq_combined;

    EF_GPIO8_WB u_ef_gpio (
        .clk_i   (wb_clk_i),
        .rst_i   (~wb_rst_ni),
        .adr_i   (wb_adr_i),
        .dat_i   (wb_dat_i),
        .dat_o   (wb_dat_o),
        .sel_i   (wb_sel_i),
        .cyc_i   (wb_cyc_i),
        .stb_i   (wb_stb_i),
        .ack_o   (wb_ack_o),
        .we_i    (wb_we_i),
        .IRQ     (irq_combined),
        .io_in   (gpio_in_i),
        .io_out  (gpio_out_o),
        .io_oe   (gpio_oe_o)
    );

    // EF_GPIO8 has single IRQ — map to 4 outputs
    // The actual IRQ source is determined by reading the interrupt status register
    assign irq_gpio_o = {4{irq_combined}};

    assign wb_err_o = 1'b0;

endmodule
