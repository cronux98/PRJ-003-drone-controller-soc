// Module: wishbone_interconnect
// Description: 14-slave Wishbone B4 one-hot address decoder + registered read-data mux
// Source: IP-010 v2 Architecture §4.2, REUSE_INTERNAL (extended from v1, adapted for native Ibex Wishbone LSU)
// v2 change: Master side now connects directly to Ibex LSU (no bus_bridge_ibex2wb)

module wishbone_interconnect (
    input  wire        wb_clk_i,
    input  wire        wb_rst_ni,

    // Master side (from bus_bridge_ibex2wb)
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,
    output reg         wb_err_o,

    // Slave 0: SRAM
    output wire [31:0] s0_adr_o,   output wire [31:0] s0_dat_o,
    output wire [ 3:0] s0_sel_o,   output wire        s0_we_o,
    output wire        s0_stb_o,    output wire        s0_cyc_o,
    input  wire [31:0] s0_dat_i,    input  wire        s0_ack_i,    input wire s0_err_i,

    // Slave 1: UART0
    output wire [31:0] s1_adr_o,   output wire [31:0] s1_dat_o,
    output wire [ 3:0] s1_sel_o,   output wire        s1_we_o,
    output wire        s1_stb_o,    output wire        s1_cyc_o,
    input  wire [31:0] s1_dat_i,    input  wire        s1_ack_i,    input wire s1_err_i,

    // Slave 2: UART1
    output wire [31:0] s2_adr_o,   output wire [31:0] s2_dat_o,
    output wire [ 3:0] s2_sel_o,   output wire        s2_we_o,
    output wire        s2_stb_o,    output wire        s2_cyc_o,
    input  wire [31:0] s2_dat_i,    input  wire        s2_ack_i,    input wire s2_err_i,

    // Slave 3: UART2
    output wire [31:0] s3_adr_o,   output wire [31:0] s3_dat_o,
    output wire [ 3:0] s3_sel_o,   output wire        s3_we_o,
    output wire        s3_stb_o,    output wire        s3_cyc_o,
    input  wire [31:0] s3_dat_i,    input  wire        s3_ack_i,    input wire s3_err_i,

    // Slave 4: SPI0
    output wire [31:0] s4_adr_o,   output wire [31:0] s4_dat_o,
    output wire [ 3:0] s4_sel_o,   output wire        s4_we_o,
    output wire        s4_stb_o,    output wire        s4_cyc_o,
    input  wire [31:0] s4_dat_i,    input  wire        s4_ack_i,    input wire s4_err_i,

    // Slave 5: I2C0
    output wire [31:0] s5_adr_o,   output wire [31:0] s5_dat_o,
    output wire [ 3:0] s5_sel_o,   output wire        s5_we_o,
    output wire        s5_stb_o,    output wire        s5_cyc_o,
    input  wire [31:0] s5_dat_i,    input  wire        s5_ack_i,    input wire s5_err_i,

    // Slave 6: DShot PWM
    output wire [31:0] s6_adr_o,   output wire [31:0] s6_dat_o,
    output wire [ 3:0] s6_sel_o,   output wire        s6_we_o,
    output wire        s6_stb_o,    output wire        s6_cyc_o,
    input  wire [31:0] s6_dat_i,    input  wire        s6_ack_i,    input wire s6_err_i,

    // Slave 7: GPIO
    output wire [31:0] s7_adr_o,   output wire [31:0] s7_dat_o,
    output wire [ 3:0] s7_sel_o,   output wire        s7_we_o,
    output wire        s7_stb_o,    output wire        s7_cyc_o,
    input  wire [31:0] s7_dat_i,    input  wire        s7_ack_i,    input wire s7_err_i,

    // Slave 8: SPI Flash
    output wire [31:0] s8_adr_o,   output wire [31:0] s8_dat_o,
    output wire [ 3:0] s8_sel_o,   output wire        s8_we_o,
    output wire        s8_stb_o,    output wire        s8_cyc_o,
    input  wire [31:0] s8_dat_i,    input  wire        s8_ack_i,    input wire s8_err_i,

    // Slave 9: IRQ Ctrl
    output wire [31:0] s9_adr_o,   output wire [31:0] s9_dat_o,
    output wire [ 3:0] s9_sel_o,   output wire        s9_we_o,
    output wire        s9_stb_o,    output wire        s9_cyc_o,
    input  wire [31:0] s9_dat_i,    input  wire        s9_ack_i,    input wire s9_err_i,

    // Slave 10: Timer
    output wire [31:0] s10_adr_o,  output wire [31:0] s10_dat_o,
    output wire [ 3:0] s10_sel_o,  output wire        s10_we_o,
    output wire        s10_stb_o,   output wire        s10_cyc_o,
    input  wire [31:0] s10_dat_i,   input  wire        s10_ack_i,   input wire s10_err_i,

    // Slave 11: Watchdog
    output wire [31:0] s11_adr_o,  output wire [31:0] s11_dat_o,
    output wire [ 3:0] s11_sel_o,  output wire        s11_we_o,
    output wire        s11_stb_o,   output wire        s11_cyc_o,
    input  wire [31:0] s11_dat_i,   input  wire        s11_ack_i,   input wire s11_err_i,

    // Slave 12: Caravel Bridge
    output wire [31:0] s12_adr_o,  output wire [31:0] s12_dat_o,
    output wire [ 3:0] s12_sel_o,  output wire        s12_we_o,
    output wire        s12_stb_o,   output wire        s12_cyc_o,
    input  wire [31:0] s12_dat_i,   input  wire        s12_ack_i,   input wire s12_err_i,

    // Slave 13: CLK/RST Mgr
    output wire [31:0] s13_adr_o,  output wire [31:0] s13_dat_o,
    output wire [ 3:0] s13_sel_o,  output wire        s13_we_o,
    output wire        s13_stb_o,   output wire        s13_cyc_o,
    input  wire [31:0] s13_dat_i,   input  wire        s13_ack_i,   input wire s13_err_i
);

    localparam N_SLAVES = 14;
    wire [19:0] addr_top;
    assign addr_top = wb_adr_i[31:12];

    // Address decode: one-hot
    reg [N_SLAVES-1:0] slave_sel;
    integer s;

    always @(*) begin
        slave_sel = {N_SLAVES{1'b0}};
        casez (addr_top)
            20'h00000: slave_sel[0]  = 1'b1;
            20'h80000: slave_sel[1]  = 1'b1;
            20'h80001: slave_sel[2]  = 1'b1;
            20'h80002: slave_sel[3]  = 1'b1;
            20'h80003: slave_sel[4]  = 1'b1;
            20'h80004: slave_sel[5]  = 1'b1;
            20'h80005: slave_sel[6]  = 1'b1;
            20'h80006: slave_sel[7]  = 1'b1;
            20'h80007: slave_sel[8]  = 1'b1;
            20'h80008: slave_sel[9]  = 1'b1;
            20'h80009: slave_sel[10] = 1'b1;
            20'h8000A: slave_sel[11] = 1'b1;
            20'h8000B: slave_sel[12] = 1'b1;
            20'h8000C: slave_sel[13] = 1'b1;
            default:   slave_sel = {N_SLAVES{1'b0}};
        endcase
    end

    // Assign slave outputs
    assign s0_adr_o = wb_adr_i;  assign s0_dat_o = wb_dat_i;
    assign s0_sel_o = wb_sel_i;   assign s0_we_o  = wb_we_i;
    assign s0_stb_o = wb_stb_i && slave_sel[0]; assign s0_cyc_o = wb_cyc_i && slave_sel[0];

    assign s1_adr_o = wb_adr_i;  assign s1_dat_o = wb_dat_i;
    assign s1_sel_o = wb_sel_i;   assign s1_we_o  = wb_we_i;
    assign s1_stb_o = wb_stb_i && slave_sel[1]; assign s1_cyc_o = wb_cyc_i && slave_sel[1];

    assign s2_adr_o = wb_adr_i;  assign s2_dat_o = wb_dat_i;
    assign s2_sel_o = wb_sel_i;   assign s2_we_o  = wb_we_i;
    assign s2_stb_o = wb_stb_i && slave_sel[2]; assign s2_cyc_o = wb_cyc_i && slave_sel[2];

    assign s3_adr_o = wb_adr_i;  assign s3_dat_o = wb_dat_i;
    assign s3_sel_o = wb_sel_i;   assign s3_we_o  = wb_we_i;
    assign s3_stb_o = wb_stb_i && slave_sel[3]; assign s3_cyc_o = wb_cyc_i && slave_sel[3];

    assign s4_adr_o = wb_adr_i;  assign s4_dat_o = wb_dat_i;
    assign s4_sel_o = wb_sel_i;   assign s4_we_o  = wb_we_i;
    assign s4_stb_o = wb_stb_i && slave_sel[4]; assign s4_cyc_o = wb_cyc_i && slave_sel[4];

    assign s5_adr_o = wb_adr_i;  assign s5_dat_o = wb_dat_i;
    assign s5_sel_o = wb_sel_i;   assign s5_we_o  = wb_we_i;
    assign s5_stb_o = wb_stb_i && slave_sel[5]; assign s5_cyc_o = wb_cyc_i && slave_sel[5];

    assign s6_adr_o = wb_adr_i;  assign s6_dat_o = wb_dat_i;
    assign s6_sel_o = wb_sel_i;   assign s6_we_o  = wb_we_i;
    assign s6_stb_o = wb_stb_i && slave_sel[6]; assign s6_cyc_o = wb_cyc_i && slave_sel[6];

    assign s7_adr_o = wb_adr_i;  assign s7_dat_o = wb_dat_i;
    assign s7_sel_o = wb_sel_i;   assign s7_we_o  = wb_we_i;
    assign s7_stb_o = wb_stb_i && slave_sel[7]; assign s7_cyc_o = wb_cyc_i && slave_sel[7];

    assign s8_adr_o = wb_adr_i;  assign s8_dat_o = wb_dat_i;
    assign s8_sel_o = wb_sel_i;   assign s8_we_o  = wb_we_i;
    assign s8_stb_o = wb_stb_i && slave_sel[8]; assign s8_cyc_o = wb_cyc_i && slave_sel[8];

    assign s9_adr_o = wb_adr_i;  assign s9_dat_o = wb_dat_i;
    assign s9_sel_o = wb_sel_i;   assign s9_we_o  = wb_we_i;
    assign s9_stb_o = wb_stb_i && slave_sel[9]; assign s9_cyc_o = wb_cyc_i && slave_sel[9];

    assign s10_adr_o = wb_adr_i; assign s10_dat_o = wb_dat_i;
    assign s10_sel_o = wb_sel_i;  assign s10_we_o  = wb_we_i;
    assign s10_stb_o = wb_stb_i && slave_sel[10]; assign s10_cyc_o = wb_cyc_i && slave_sel[10];

    assign s11_adr_o = wb_adr_i; assign s11_dat_o = wb_dat_i;
    assign s11_sel_o = wb_sel_i;  assign s11_we_o  = wb_we_i;
    assign s11_stb_o = wb_stb_i && slave_sel[11]; assign s11_cyc_o = wb_cyc_i && slave_sel[11];

    assign s12_adr_o = wb_adr_i; assign s12_dat_o = wb_dat_i;
    assign s12_sel_o = wb_sel_i;  assign s12_we_o  = wb_we_i;
    assign s12_stb_o = wb_stb_i && slave_sel[12]; assign s12_cyc_o = wb_cyc_i && slave_sel[12];

    assign s13_adr_o = wb_adr_i; assign s13_dat_o = wb_dat_i;
    assign s13_sel_o = wb_sel_i;  assign s13_we_o  = wb_we_i;
    assign s13_stb_o = wb_stb_i && slave_sel[13]; assign s13_cyc_o = wb_cyc_i && slave_sel[13];

    // Registered read-data mux
    reg [31:0] rd_data_q;
    wire       any_ack;
    assign any_ack = (slave_sel[0]  && s0_ack_i)  || (slave_sel[1]  && s1_ack_i)  ||
                     (slave_sel[2]  && s2_ack_i)  || (slave_sel[3]  && s3_ack_i)  ||
                     (slave_sel[4]  && s4_ack_i)  || (slave_sel[5]  && s5_ack_i)  ||
                     (slave_sel[6]  && s6_ack_i)  || (slave_sel[7]  && s7_ack_i)  ||
                     (slave_sel[8]  && s8_ack_i)  || (slave_sel[9]  && s9_ack_i)  ||
                     (slave_sel[10] && s10_ack_i) || (slave_sel[11] && s11_ack_i) ||
                     (slave_sel[12] && s12_ack_i) || (slave_sel[13] && s13_ack_i);

    // Combinational read-data mux
    reg [31:0] mux_out;
    always @(*) begin
        mux_out = 32'd0;
        if      (slave_sel[0])  mux_out = s0_dat_i;
        else if (slave_sel[1])  mux_out = s1_dat_i;
        else if (slave_sel[2])  mux_out = s2_dat_i;
        else if (slave_sel[3])  mux_out = s3_dat_i;
        else if (slave_sel[4])  mux_out = s4_dat_i;
        else if (slave_sel[5])  mux_out = s5_dat_i;
        else if (slave_sel[6])  mux_out = s6_dat_i;
        else if (slave_sel[7])  mux_out = s7_dat_i;
        else if (slave_sel[8])  mux_out = s8_dat_i;
        else if (slave_sel[9])  mux_out = s9_dat_i;
        else if (slave_sel[10]) mux_out = s10_dat_i;
        else if (slave_sel[11]) mux_out = s11_dat_i;
        else if (slave_sel[12]) mux_out = s12_dat_i;
        else if (slave_sel[13]) mux_out = s13_dat_i;
    end

    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            wb_ack_o  <= 1'b0;
            wb_err_o  <= 1'b0;
            wb_dat_o  <= 32'd0;
            rd_data_q <= 32'd0;
        end else begin
            wb_ack_o <= 1'b0;
            wb_err_o <= 1'b0;

            if (wb_cyc_i && wb_stb_i) begin
                if (any_ack) begin
                    wb_ack_o  <= 1'b1;
                    rd_data_q <= mux_out;
                end
            end

            wb_dat_o <= rd_data_q;
        end
    end

endmodule
