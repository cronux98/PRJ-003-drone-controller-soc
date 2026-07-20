// =========================================================================
// Module: EF_TMR32_WB_wrapper
// Description: Wrapper for EF_TMR32_WB — adapts FOSSi IP to architecture conventions
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_TMR32_WB_wrapper (
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

    // Timer interface
    input  wire        capture_i,
    output wire        irq_overflow_o,
    output wire        irq_capture_o
);

    // EF_TMR32 has single IRQ output and PWM outputs
    wire irq_combined;
    wire pwm0, pwm1;

    EF_TMR32_WB u_ef_tmr (
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
        .IRQ        (irq_combined),
        .pwm0       (pwm0),
        .pwm1       (pwm1),
        .pwm_fault  (1'b0)   // No fault input
    );

    // EF_TMR32 has single IRQ — map to overflow
    assign irq_overflow_o = irq_combined;
    assign irq_capture_o  = 1'b0;  // EF_TMR32 doesn't have capture

    assign wb_err_o = 1'b0;

endmodule
