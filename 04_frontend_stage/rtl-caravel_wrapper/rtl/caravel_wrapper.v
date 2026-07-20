// Module: caravel_wrapper
// Description: Caravel Management SoC Bridge — Wishbone B4 slave
// Bridges Caravel mgmt SoC to user project for firmware loading, debug, USB-UART passthrough
// Source: IP-010 v1 Architecture §4.13, REUSE_GITHUB (Caravel template, 40+ MPW proven)
// Address: 0x8000_B000 - 0x8000_BFFF

module caravel_wrapper (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Wishbone B4 slave
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,

    // Caravel harness (logic analyzer)
    input  wire [127:0] la_data_in_i,
    output reg  [127:0] la_data_out_o,
    input  wire [127:0] la_oenb_i,

    // Caravel GPIO
    input  wire [37:0]  io_in_i,

    // Caravel interrupt
    output reg          irq_caravel_o,

    // Ready flag from clk_rst_mgr (held low until Caravel releases reset)
    input  wire         ready_i
);

    wire _unused = |{wb_adr_i[31:4], wb_adr_i[1:0], wb_dat_i[31:8], wb_sel_i,
                     la_data_in_i[127:32], la_oenb_i[127:32],
                     io_in_i[37:8]};

    // Bridge is disabled until Caravel releases reset (ready_i asserted)
    // LA bus: only lower 32 bits used for Wishbone bridging
    reg [31:0] bridge_data;
    reg        bridge_valid;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            bridge_data  <= 32'd0;
            bridge_valid <= 1'b0;
        end else if (ready_i) begin
            // Caravel mgmt SoC writes to LA input, which we present as Wishbone data
            bridge_data  <= la_data_in_i[31:0];
            bridge_valid <= 1'b1;
        end else begin
            bridge_valid <= 1'b0;
        end
    end

    // Wishbone slave: passthrough from Caravel LA
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_ack_o       <= 1'b0;
            wb_dat_o       <= 32'd0;
            la_data_out_o  <= 128'd0;
            irq_caravel_o  <= 1'b0;
        end else begin
            wb_ack_o <= 1'b0;

            if (wb_cyc_i && wb_stb_i && !wb_ack_o && ready_i) begin
                wb_ack_o <= 1'b1;
                if (!wb_we_i) begin
                    wb_dat_o <= bridge_data;
                end
                // For writes, echo to LA output
                if (wb_we_i) begin
                    la_data_out_o[31:0] <= wb_dat_i;
                end
            end

            // Caravel interrupt: asserted when bridge is ready and LA has data
            irq_caravel_o <= ready_i && bridge_valid;
        end
    end

endmodule
