// sram_8kb.v — Behavioral SRAM model for RTL simulation
// 8KB (2048 × 32-bit) unified Von Neumann SRAM
// Wishbone B4 slave interface
// For synthesis: use sram_8kb_blackbox.v (real sky130 macro)
//
// v3 — IP-010 Drone Controller SoC
// Single-cycle read, single-cycle write, zero wait states
// Byte-select support via wb_sel_i[3:0]

module sram_8kb (
    input  wire        clk_i,
    input  wire        rst_ni,
    input  wire [12:0] wb_adr_i,   // Word address (2048 entries)
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [3:0]  wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o
);

    // 2048 × 32-bit memory array
    reg [31:0] mem [0:2047];

    // Word address (bits [12:2] of byte address)
    wire [10:0] word_addr = wb_adr_i[12:2];

    // Combinational read
    always @(*) begin
        if (wb_cyc_i && wb_stb_i && !wb_we_i) begin
            wb_dat_o = mem[word_addr];
        end else begin
            wb_dat_o = 32'h0;
        end
    end

    // Registered write with byte select
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_ack_o <= 1'b0;
        end else begin
            wb_ack_o <= 1'b0;
            if (wb_cyc_i && wb_stb_i) begin
                wb_ack_o <= 1'b1;
                if (wb_we_i) begin
                    if (wb_sel_i[0]) mem[word_addr][ 7: 0] <= wb_dat_i[ 7: 0];
                    if (wb_sel_i[1]) mem[word_addr][15: 8] <= wb_dat_i[15: 8];
                    if (wb_sel_i[2]) mem[word_addr][23:16] <= wb_dat_i[23:16];
                    if (wb_sel_i[3]) mem[word_addr][31:24] <= wb_dat_i[31:24];
                end
            end
        end
    end

endmodule
