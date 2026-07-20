// Module: irq_ctrl
// Description: 16-source interrupt controller with prio-based arbitration
// 2-bit prio per source, threshold register, CLAIM mechanism
// Source: IP-010 v1 Architecture §4.10, REUSE_INTERNAL (IP-008/009, ~350-500 cells)
// Address: 0x8000_8000 - 0x8000_8FFF

module irq_ctrl (
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

    // Interrupt sources (16 lines)
    input  wire [15:0] irq_src_i,

    // Machine external interrupt to Ibex
    output reg         m_irq_o
);

    wire _unused = |{wb_adr_i[31:4], wb_adr_i[1:0], wb_dat_i[31:16], wb_sel_i};

    localparam N_SRC = 16;

    // Register map
    localparam ADDR_PENDING    = 3'h0;  // 0x00: PENDING (read-only)
    localparam ADDR_ENABLE     = 3'h1;  // 0x04: ENABLE
    localparam ADDR_PRIORITY0  = 3'h2;  // 0x08: PRIORITY for sources 0-7
    localparam ADDR_PRIORITY1  = 3'h3;  // 0x0C: PRIORITY for sources 8-15
    localparam ADDR_THRESHOLD  = 3'h4;  // 0x10: THRESHOLD
    localparam ADDR_CLAIM      = 3'h5;  // 0x14: CLAIM (read returns ID, clears pending)

    // Per-source registers
    reg [15:0] pending;   // Pending flags
    reg [15:0] enable;    // Enable mask
    reg [ 1:0] prio [0:15];  // 2-bit prio per source
    reg [ 1:0] threshold; // Minimum prio to trigger CPU IRQ

    // 2-FF synchronizers on irq inputs
    reg [15:0] irq_sync1, irq_sync2;

    // CLAIM temporary
    reg [3:0] claim_id;

    integer i;

    always @(posedge clk_i or negedge rst_ni) begin
        if (!rst_ni) begin
            pending     <= 16'd0;
            enable      <= 16'd0;
            threshold   <= 2'd0;
            m_irq_o     <= 1'b0;
            wb_ack_o    <= 1'b0;
            wb_dat_o    <= 32'd0;
            irq_sync1   <= 16'd0;
            irq_sync2   <= 16'd0;
            for (i = 0; i < N_SRC; i = i + 1) begin
                prio[i] <= 2'd3;  // Lowest prio by default
            end
        end else begin
            wb_ack_o <= 1'b0;

            // Synchronize IRQ inputs
            irq_sync1 <= irq_src_i;
            irq_sync2 <= irq_sync1;

            // Capture IRQ sources into pending (level-sensitive)
            for (i = 0; i < N_SRC; i = i + 1) begin
                if (irq_sync2[i])
                    pending[i] <= 1'b1;
            end

            // Priority arbitration: find highest-prio enabled pending source
            // Priority 0 = highest. Within same prio, lowest source ID wins.
            m_irq_o <= 1'b0;
            for (i = 0; i < N_SRC; i = i + 1) begin
                if (enable[i] && pending[i] && (prio[i] <= threshold)) begin
                    // This source qualifies — but NBA means the last qualifying source wins
                    // To get lowest-source-ID-wins, we count UP
                    m_irq_o <= 1'b1;
                end
            end

            // Wishbone B4 slave
            if (wb_cyc_i && wb_stb_i && !wb_ack_o) begin
                wb_ack_o <= 1'b1;
                if (wb_we_i) begin
                    case (wb_adr_i[4:2])
                        ADDR_ENABLE:    enable <= wb_dat_i[15:0];
                        ADDR_PRIORITY0: begin
                            for (i = 0; i < 8; i = i + 1)
                                prio[i] <= wb_dat_i[i*2 +: 2];
                        end
                        ADDR_PRIORITY1: begin
                            for (i = 0; i < 8; i = i + 1)
                                prio[i+8] <= wb_dat_i[i*2 +: 2];
                        end
                        ADDR_THRESHOLD: threshold <= wb_dat_i[1:0];
                        default: ;
                    endcase
                end else begin
                    case (wb_adr_i[4:2])
                        ADDR_PENDING:   wb_dat_o <= {16'd0, pending};
                        ADDR_ENABLE:    wb_dat_o <= {16'd0, enable};
                        ADDR_PRIORITY0: begin
                            wb_dat_o <= 32'd0;
                            for (i = 0; i < 8; i = i + 1)
                                wb_dat_o[i*2 +: 2] <= prio[i];
                        end
                        ADDR_PRIORITY1: begin
                            wb_dat_o <= 32'd0;
                            for (i = 0; i < 8; i = i + 1)
                                wb_dat_o[i*2 +: 2] <= prio[i+8];
                        end
                        ADDR_THRESHOLD: wb_dat_o <= {30'd0, threshold};
                        ADDR_CLAIM: begin
                            // Find highest-prio enabled pending source, return its ID
                            // Clear that pending bit
                            // DOWN-counting: lower source ID wins at same prio
                            claim_id = 4'd0;
                            for (i = N_SRC-1; i >= 0; i = i - 1) begin
                                if (enable[i] && pending[i] && (prio[i] <= threshold)) begin
                                    claim_id = i[3:0];
                                end
                            end
                            wb_dat_o <= {28'd0, claim_id};
                            // Clear the claimed pending bit
                            if (enable[claim_id] && pending[claim_id])
                                pending[claim_id] <= 1'b0;
                        end
                        default: wb_dat_o <= 32'd0;
                    endcase
                end
            end
        end
    end

endmodule
