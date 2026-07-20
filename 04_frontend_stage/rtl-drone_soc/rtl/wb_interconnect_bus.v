// =========================================================================
// Module: wb_interconnect_bus
// Description: Simple Wishbone B4 decoder/mux for drone_soc synthesis.
//              One-hot address decode → slave_sel_o. Muxes ack/dat/err.
//              Verilog-2005 compatible (no unpacked array ports).
// =========================================================================

module wb_interconnect_bus #(
    parameter NUM_SLAVES = 15
) (
    input  wire        wb_clk_i,
    input  wire        wb_rst_ni,

    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,
    output reg         wb_err_o,

    output wire [NUM_SLAVES-1:0] slave_sel_o,

    // Per-slave data/ack/err — individual ports (Verilog-2005)
    input  wire [31:0] s_wb_dat_i_0,
    input  wire [31:0] s_wb_dat_i_1,
    input  wire [31:0] s_wb_dat_i_2,
    input  wire [31:0] s_wb_dat_i_3,
    input  wire [31:0] s_wb_dat_i_4,
    input  wire [31:0] s_wb_dat_i_5,
    input  wire [31:0] s_wb_dat_i_6,
    input  wire [31:0] s_wb_dat_i_7,
    input  wire [31:0] s_wb_dat_i_8,
    input  wire [31:0] s_wb_dat_i_9,
    input  wire [31:0] s_wb_dat_i_10,
    input  wire [31:0] s_wb_dat_i_11,
    input  wire [31:0] s_wb_dat_i_12,
    input  wire [31:0] s_wb_dat_i_13,
    input  wire [31:0] s_wb_dat_i_14,

    input  wire        s_wb_ack_i_0,
    input  wire        s_wb_ack_i_1,
    input  wire        s_wb_ack_i_2,
    input  wire        s_wb_ack_i_3,
    input  wire        s_wb_ack_i_4,
    input  wire        s_wb_ack_i_5,
    input  wire        s_wb_ack_i_6,
    input  wire        s_wb_ack_i_7,
    input  wire        s_wb_ack_i_8,
    input  wire        s_wb_ack_i_9,
    input  wire        s_wb_ack_i_10,
    input  wire        s_wb_ack_i_11,
    input  wire        s_wb_ack_i_12,
    input  wire        s_wb_ack_i_13,
    input  wire        s_wb_ack_i_14,

    input  wire        s_wb_err_i_0,
    input  wire        s_wb_err_i_1,
    input  wire        s_wb_err_i_2,
    input  wire        s_wb_err_i_3,
    input  wire        s_wb_err_i_4,
    input  wire        s_wb_err_i_5,
    input  wire        s_wb_err_i_6,
    input  wire        s_wb_err_i_7,
    input  wire        s_wb_err_i_8,
    input  wire        s_wb_err_i_9,
    input  wire        s_wb_err_i_10,
    input  wire        s_wb_err_i_11,
    input  wire        s_wb_err_i_12,
    input  wire        s_wb_err_i_13,
    input  wire        s_wb_err_i_14
);

    // One-hot decode
    wire [NUM_SLAVES-1:0] decode;

    // Slave 0: SRAM @ 0x0000_0000
    assign decode[0] = (wb_adr_i[31:13] == 19'd0);

    // Slaves 1-14: peripherals @ 0x8000_0xxx, 4KB each
    assign decode[1]  = (wb_adr_i[31:12] == 20'h80000);
    assign decode[2]  = (wb_adr_i[31:12] == 20'h80001);
    assign decode[3]  = (wb_adr_i[31:12] == 20'h80002);
    assign decode[4]  = (wb_adr_i[31:12] == 20'h80003);
    assign decode[5]  = (wb_adr_i[31:12] == 20'h80004);
    assign decode[6]  = (wb_adr_i[31:12] == 20'h80005);
    assign decode[7]  = (wb_adr_i[31:12] == 20'h80006);
    assign decode[8]  = (wb_adr_i[31:12] == 20'h80007);
    assign decode[9]  = (wb_adr_i[31:12] == 20'h80008);
    assign decode[10] = (wb_adr_i[31:12] == 20'h80009);
    assign decode[11] = (wb_adr_i[31:12] == 20'h8000A);
    assign decode[12] = (wb_adr_i[31:12] == 20'h8000B);
    assign decode[13] = (wb_adr_i[31:12] == 20'h8000C);
    assign decode[14] = (wb_adr_i[31:12] == 20'h8000D);

    assign slave_sel_o = decode & {NUM_SLAVES{wb_stb_i & wb_cyc_i}};

    // Read data mux
    always @(*) begin
        wb_dat_o = 32'd0;
        if (decode[0])  wb_dat_o = s_wb_dat_i_0;
        if (decode[1])  wb_dat_o = s_wb_dat_i_1;
        if (decode[2])  wb_dat_o = s_wb_dat_i_2;
        if (decode[3])  wb_dat_o = s_wb_dat_i_3;
        if (decode[4])  wb_dat_o = s_wb_dat_i_4;
        if (decode[5])  wb_dat_o = s_wb_dat_i_5;
        if (decode[6])  wb_dat_o = s_wb_dat_i_6;
        if (decode[7])  wb_dat_o = s_wb_dat_i_7;
        if (decode[8])  wb_dat_o = s_wb_dat_i_8;
        if (decode[9])  wb_dat_o = s_wb_dat_i_9;
        if (decode[10]) wb_dat_o = s_wb_dat_i_10;
        if (decode[11]) wb_dat_o = s_wb_dat_i_11;
        if (decode[12]) wb_dat_o = s_wb_dat_i_12;
        if (decode[13]) wb_dat_o = s_wb_dat_i_13;
        if (decode[14]) wb_dat_o = s_wb_dat_i_14;
    end

    // Ack/err mux (registered)
    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            wb_ack_o <= 1'b0;
            wb_err_o <= 1'b0;
        end else begin
            wb_ack_o <= (decode[0]  & s_wb_ack_i_0)  |
                        (decode[1]  & s_wb_ack_i_1)  |
                        (decode[2]  & s_wb_ack_i_2)  |
                        (decode[3]  & s_wb_ack_i_3)  |
                        (decode[4]  & s_wb_ack_i_4)  |
                        (decode[5]  & s_wb_ack_i_5)  |
                        (decode[6]  & s_wb_ack_i_6)  |
                        (decode[7]  & s_wb_ack_i_7)  |
                        (decode[8]  & s_wb_ack_i_8)  |
                        (decode[9]  & s_wb_ack_i_9)  |
                        (decode[10] & s_wb_ack_i_10) |
                        (decode[11] & s_wb_ack_i_11) |
                        (decode[12] & s_wb_ack_i_12) |
                        (decode[13] & s_wb_ack_i_13) |
                        (decode[14] & s_wb_ack_i_14);
            wb_err_o <= (decode[0]  & s_wb_err_i_0)  |
                        (decode[1]  & s_wb_err_i_1)  |
                        (decode[2]  & s_wb_err_i_2)  |
                        (decode[3]  & s_wb_err_i_3)  |
                        (decode[4]  & s_wb_err_i_4)  |
                        (decode[5]  & s_wb_err_i_5)  |
                        (decode[6]  & s_wb_err_i_6)  |
                        (decode[7]  & s_wb_err_i_7)  |
                        (decode[8]  & s_wb_err_i_8)  |
                        (decode[9]  & s_wb_err_i_9)  |
                        (decode[10] & s_wb_err_i_10) |
                        (decode[11] & s_wb_err_i_11) |
                        (decode[12] & s_wb_err_i_12) |
                        (decode[13] & s_wb_err_i_13) |
                        (decode[14] & s_wb_err_i_14);
        end
    end

endmodule
