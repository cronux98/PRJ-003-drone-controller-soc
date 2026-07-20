// =========================================================================
// Module: ibex_core
// Description: Ibex RV32IMC wrapper with native Wishbone LSU
//              Wraps the v1 ibex_core (memory interface) with a
//              Wishbone B4 master adapter
//
// Source: IP-010 v2 Architecture §4.1, ADAPTER
// =========================================================================

module ibex_core (
    input  wire        clk_i,
    input  wire        rst_ni,

    // Wishbone B4 master
    output wire [31:0] wb_adr_o,
    output wire [31:0] wb_dat_o,
    input  wire [31:0] wb_dat_i,
    output wire [ 3:0] wb_sel_o,
    output wire        wb_we_o,
    output wire        wb_stb_o,
    output wire        wb_cyc_o,
    input  wire        wb_ack_i,
    input  wire        wb_err_i,

    // Interrupts
    input  wire        irq_software_i,
    input  wire        irq_timer_i,
    input  wire        irq_external_i,
    input  wire [14:0] irq_fast_i,

    // Fetch enable
    input  wire        fetch_enable_i
);

    // Internal memory interface from Ibex core
    wire [31:0] imem_addr;
    wire [31:0] imem_rdata;
    wire [31:0] dmem_addr;
    wire [31:0] dmem_wdata;
    wire [31:0] dmem_rdata;
    wire        dmem_we;
    wire        dmem_re;
    wire [ 3:0] dmem_be;
    wire [ 2:0] dmem_funct3;
    wire        stall;

    // Instantiate the v1 Ibex core
    ibex_core_inner u_ibex (
        .clk_i          (clk_i),
        .rst_ni         (rst_ni),
        .imem_addr_o    (imem_addr),
        .imem_rdata_i   (imem_rdata),
        .dmem_addr_o    (dmem_addr),
        .dmem_wdata_o   (dmem_wdata),
        .dmem_rdata_i   (dmem_rdata),
        .dmem_we_o      (dmem_we),
        .dmem_re_o      (dmem_re),
        .dmem_be_o      (dmem_be),
        .dmem_funct3_o  (dmem_funct3),
        .stall_i        (stall)
    );

    // Wishbone adapter: convert memory interface to Wishbone B4
    // Simple: assert STB/CYC on memory access, wait for ACK
    reg        wb_active;
    reg [31:0] wb_adr_reg;
    reg [31:0] wb_dat_w_reg;
    reg [ 3:0] wb_sel_reg;
    reg        wb_we_reg;

    // Determine if this is an instruction fetch or data access
    // Data access has priority (load/store)
    wire data_access = dmem_we || dmem_re;
    wire imem_access = !data_access && fetch_enable_i;

    // Wishbone address mux
    assign wb_adr_o = data_access ? dmem_addr : imem_addr;
    assign wb_dat_o = dmem_wdata;
    assign wb_sel_o = data_access ? dmem_be : 4'hF;
    assign wb_we_o  = dmem_we;
    assign wb_stb_o = (data_access || imem_access) && !wb_active;
    assign wb_cyc_o = (data_access || imem_access) && !wb_active;

    // Stall Ibex while Wishbone transaction is pending
    assign stall = (data_access || imem_access) && !wb_ack_i && !wb_err_i;

    // Read data mux
    assign dmem_rdata = wb_dat_i;
    assign imem_rdata = wb_dat_i;

    // Track active transaction
    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            wb_active <= 1'b0;
        end else begin
            if (wb_stb_o && wb_cyc_o && (wb_ack_i || wb_err_i))
                wb_active <= 1'b0;
            else if (wb_stb_o && wb_cyc_o)
                wb_active <= 1'b1;
        end
    end

endmodule
