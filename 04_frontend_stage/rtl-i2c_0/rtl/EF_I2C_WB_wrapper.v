// =========================================================================
// Module: EF_I2C_WB_wrapper
// Description: Wrapper for EF_I2C_WB — adapts FOSSi IP to architecture conventions
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_I2C_WB_wrapper (
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

    // I2C interface
    output wire        i2c_scl_o,
    output wire        i2c_sda_o,
    input  wire        i2c_sda_i,

    // Interrupt
    output wire        irq_done_o
);

    // I2C open-drain signals
    wire scl_oen, sda_oen;

    EF_I2C_WB u_ef_i2c (
        .clk_i      (wb_clk_i),
        .rst_i      (~wb_rst_ni),
        .adr_i      (wb_adr_i),
        .dat_i      (wb_dat_i),
        .dat_o      (wb_dat_o),
        .sel_i      (wb_sel_i),
        .cyc_i      (wb_cyc_i),
        .stb_i      (wb_stb_i),
        .ack_o      (wb_ack_o),
        .we_i       (wb_we_i),
        .IRQ        (irq_done_o),
        .scl_i      (1'b1),      // Open-drain: read high when not driving
        .scl_o      (i2c_scl_o),
        .scl_oen_o  (scl_oen),
        .sda_i      (i2c_sda_i),
        .sda_o      (i2c_sda_o),
        .sda_oen_o  (sda_oen)
    );

    assign wb_err_o = 1'b0;

endmodule
