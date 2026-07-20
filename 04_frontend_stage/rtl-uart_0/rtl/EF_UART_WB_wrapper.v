// =========================================================================
// Module: EF_UART_WB_wrapper
// Description: Wrapper for EF_UART_WB — adapts FOSSi IP to architecture conventions
//              Active-low reset, wb_* port prefix, separate IRQ outputs
// Source: IP-010 v2 — FOSSi IP adapter
// =========================================================================

module EF_UART_WB_wrapper (
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

    // UART interface
    output wire        uart_tx_o,
    input  wire        uart_rx_i,

    // Interrupts
    output wire        irq_rx_o,
    output wire        irq_tx_o
);

    // Internal IRQ from EF_UART_WB
    wire irq_combined;

    // Instantiate EF_UART_WB with active-high reset
    EF_UART_WB u_ef_uart (
        .clk_i  (wb_clk_i),
        .rst_i  (~wb_rst_ni),  // Active-high reset
        .adr_i  (wb_adr_i),
        .dat_i  (wb_dat_i),
        .dat_o  (wb_dat_o),
        .sel_i  (wb_sel_i),
        .cyc_i  (wb_cyc_i),
        .stb_i  (wb_stb_i),
        .ack_o  (wb_ack_o),
        .we_i   (wb_we_i),
        .IRQ    (irq_combined),
        .rx     (uart_rx_i),
        .tx     (uart_tx_o)
    );

    // EF_UART has single IRQ output — map to both rx/tx
    // The actual IRQ source is determined by reading the status register
    assign irq_rx_o = irq_combined;
    assign irq_tx_o = 1'b0;  // EF_UART uses single IRQ line

    // No error output from EF_UART
    assign wb_err_o = 1'b0;

endmodule
