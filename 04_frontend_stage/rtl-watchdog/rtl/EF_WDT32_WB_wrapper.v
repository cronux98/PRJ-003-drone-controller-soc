// =========================================================================
// Module: EF_WDT32_WB_wrapper
// Description: Wrapper for EF_WDT32_WB — adapts FOSSi IP to architecture conventions
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_WDT32_WB_wrapper (
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

    // Watchdog interface
    output wire        irq_warn_o,
    output wire        rst_req_o
);

    // EF_WDT32 has single IRQ output
    wire irq_combined;

    EF_WDT32_WB u_ef_wdt (
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
        .IRQ    (irq_combined)
    );

    // EF_WDT32 IRQ maps to warning
    assign irq_warn_o = irq_combined;

    // EF_WDT32 doesn't have explicit reset request output
    // The IRQ itself serves as the warning — firmware must kick before reset
    assign rst_req_o = 1'b0;  // EF_WDT32 handles reset internally

    assign wb_err_o = 1'b0;

endmodule
