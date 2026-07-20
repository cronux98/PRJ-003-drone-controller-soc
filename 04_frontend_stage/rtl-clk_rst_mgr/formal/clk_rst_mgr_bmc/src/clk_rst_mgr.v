// Module: clk_rst_mgr
// Description: Clock & Reset Manager — reset synchronizer, reset sequencer, clock buffer
// Source: IP-010 v1 Architecture §4.14, REUSE_INTERNAL (trivial module)
// Address: 0x8000_C000 - 0x8000_CFFF

module clk_rst_mgr (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Caravel harness
    input  wire        user_clock_i,
    input  wire        user_reset_n_i,

    // Wishbone B4 slave
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,

    // Reset outputs
    output wire        wb_rst_n_o,
    output reg         cpu_rst_n_o,

    // Watchdog reset request
    input  wire        wdg_rst_req_i,

    // System clock output
    output wire        sys_clk_o
);

    wire _unused = |{wb_adr_i[31:4], wb_adr_i[1:0], wb_dat_i[31:4], wb_sel_i};

    // Clock: buffer user_clock to sys_clk (single domain, no divider in v1)
    assign sys_clk_o = user_clock_i;

    // 2-stage reset synchronizer: async assert, sync deassert
    reg [1:0] rst_sync;
    always @(posedge clk_i or negedge user_reset_n_i) begin
        if (!user_reset_n_i) begin
            rst_sync <= 2'b00;
        end else begin
            rst_sync <= {rst_sync[0], 1'b1};
        end
    end
    assign wb_rst_n_o = rst_sync[1];

    // CPU reset hold-off: 16 cycles after bus reset deassert
    reg [4:0] cpu_rst_counter;
    reg       cpu_held;

    always @(posedge clk_i or negedge user_reset_n_i) begin
        if (!user_reset_n_i) begin
            cpu_held        <= 1'b1;
            cpu_rst_counter <= 5'd0;
            cpu_rst_n_o     <= 1'b0;
        end else if (!rst_sync[1]) begin
            cpu_held        <= 1'b1;
            cpu_rst_counter <= 5'd0;
            cpu_rst_n_o     <= 1'b0;
        end else if (wdg_rst_req_i) begin
            // Watchdog reset: hold CPU reset for 16 cycles
            cpu_held        <= 1'b1;
            cpu_rst_counter <= 5'd0;
            cpu_rst_n_o     <= 1'b0;
        end else if (cpu_held) begin
            if (cpu_rst_counter < 5'd16) begin
                cpu_rst_counter <= cpu_rst_counter + 5'd1;
                cpu_rst_n_o     <= 1'b0;
            end else begin
                cpu_held    <= 1'b0;
                cpu_rst_n_o <= 1'b1;
            end
        end
    end

    // Status register
    reg wdg_reset_occurred;

    always @(posedge clk_i or negedge user_reset_n_i) begin
        if (!user_reset_n_i) begin
            wdg_reset_occurred <= 1'b0;
        end else if (wdg_rst_req_i) begin
            wdg_reset_occurred <= 1'b1;
        end
    end

    // Wishbone slave: read-only STATUS register at offset 0x00
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_ack_o <= 1'b0;
            wb_dat_o <= 32'd0;
        end else begin
            wb_ack_o <= 1'b0;
            if (wb_cyc_i && wb_stb_i && !wb_ack_o) begin
                wb_ack_o <= 1'b1;
                if (!wb_we_i) begin
                    // STATUS register at offset 0x00
                    // bit[0]=reset active, bit[1]=cpu held, bit[2]=wdg reset occurred
                    wb_dat_o <= {29'd0, wdg_reset_occurred, cpu_held, !wb_rst_n_o};
                end
            end
        end
    end

endmodule
