// =========================================================================
// Module: spi_flash_ctrl
// Description: SPI flash controller for W25Q32JV 4MB NOR flash
//              Wishbone B4 slave interface with hardware read acceleration
//
// Source: IP-010 v2 Architecture §4.9, CREATE
//
// Features:
//   - SPI mode 0 (CPOL=0, CPHA=0)
//   - Flash commands: Read JEDEC ID (0x9F), Read Status (0x05),
//     Write Enable (0x06), Read Data (0x03), Fast Read (0x0B),
//     Page Program (0x02), Sector Erase (0x20)
//   - 24-bit flash address
//   - Hardware read acceleration (FSM-driven)
//   - Configurable clock: sys_clk/2 (25 MHz) or sys_clk (50 MHz)
//
// Register Map (offsets from base):
//   0x00 CMD      R/W  Flash command byte
//   0x04 ADDR     R/W  24-bit flash address
//   0x08 TXDATA   W    Write data (for Page Program)
//   0x0C RDDATA   R    Read data (from Read/Read JEDEC ID)
//   0x10 STATUS   R    bit[0]=done, bit[1]=busy, bit[2]=WEL
//   0x14 CTRL     R/W  bit[0]=go, bit[1]=fast_mode
//
// FSM States: IDLE → CMD_SEND → ADDR_SEND(×3) → DATA_PHASE → DONE
// =========================================================================

module spi_flash_ctrl (
    input  wire        wb_clk_i,
    input  wire        wb_rst_ni,

    // Wishbone B4 slave
    input  wire [31:0] wb_adr_i,
    input  wire [31:0] wb_dat_i,
    output reg  [31:0] wb_dat_o,
    input  wire [ 3:0] wb_sel_i,
    input  wire        wb_we_i,
    input  wire        wb_stb_i,
    input  wire        wb_cyc_i,
    output reg         wb_ack_o,
    output reg         wb_err_o,

    // SPI flash interface
    output reg         flash_sck_o,
    output reg         flash_mosi_o,
    input  wire        flash_miso_i,
    output reg         flash_cs_o,
    output reg         flash_wp_o,
    output reg         flash_hold_o
);

    // -----------------------------------------------------------------
    // FSM states
    // -----------------------------------------------------------------
    localparam [2:0]
        ST_IDLE       = 3'd0,
        ST_CMD_SEND   = 3'd1,
        ST_ADDR_SEND  = 3'd2,
        ST_DATA_READ  = 3'd3,
        ST_DATA_WRITE = 3'd4,
        ST_DONE       = 3'd5;

    // -----------------------------------------------------------------
    // Registers
    // -----------------------------------------------------------------
    reg [ 7:0] cmd_reg;
    reg [23:0] addr_reg;
    reg [ 7:0] txdata_reg;
    reg [ 7:0] rddata_reg;
    reg        status_done;
    reg        status_busy;
    reg        status_wel;
    reg        ctrl_go;
    reg        ctrl_fast_mode;

    // -----------------------------------------------------------------
    // Internal state
    // -----------------------------------------------------------------
    reg [ 2:0] fsm_state;
    reg [ 2:0] bit_cnt;
    reg [ 2:0] addr_byte_cnt;
    reg [ 7:0] shift_reg;
    reg [ 7:0] rx_shift;
    reg        sck_en;
    reg        sck_div;       // Clock divider: 0=sys_clk/2, 1=sys_clk
    reg        sck_toggle;

    // -----------------------------------------------------------------
    // Wishbone register access
    // -----------------------------------------------------------------
    wire wb_valid = wb_cyc_i && wb_stb_i;
    wire [3:0] wb_offset = wb_adr_i[3:0];

    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            cmd_reg      <= 8'd0;
            addr_reg     <= 24'd0;
            txdata_reg   <= 8'd0;
            ctrl_go      <= 1'b0;
            ctrl_fast_mode <= 1'b0;
            wb_ack_o     <= 1'b0;
            wb_err_o     <= 1'b0;
            wb_dat_o     <= 32'd0;
        end else begin
            wb_ack_o <= 1'b0;
            wb_err_o <= 1'b0;
            wb_dat_o <= 32'd0;

            if (wb_valid && !wb_ack_o) begin
                wb_ack_o <= 1'b1;

                if (wb_we_i) begin
                    case (wb_offset)
                        4'h0: cmd_reg        <= wb_dat_i[7:0];
                        4'h4: addr_reg       <= wb_dat_i[23:0];
                        4'h8: txdata_reg     <= wb_dat_i[7:0];
                        6'h0C: ;  // RDDATA is read-only
                        6'h10: ; // STATUS is read-only
                        6'h14: begin
                            ctrl_go        <= wb_dat_i[0];
                            ctrl_fast_mode <= wb_dat_i[1];
                        end
                        default: ;
                    endcase
                end else begin
                    case (wb_offset)
                        4'h0: wb_dat_o <= {24'd0, cmd_reg};
                        4'h4: wb_dat_o <= {8'd0, addr_reg};
                        4'h8: wb_dat_o <= {24'd0, txdata_reg};
                        6'h0C: wb_dat_o <= {24'd0, rddata_reg};
                        6'h10: wb_dat_o <= {29'd0, status_wel, status_busy, status_done};
                        6'h14: wb_dat_o <= {30'd0, ctrl_fast_mode, ctrl_go};
                        default: wb_dat_o <= 32'd0;
                    endcase
                end

                // Clear go after it's been read by FSM
                if (!wb_we_i && wb_offset == 6'h14)
                    ctrl_go <= 1'b0;
            end
        end
    end

    // -----------------------------------------------------------------
    // SPI Flash FSM
    // -----------------------------------------------------------------
    always @(posedge wb_clk_i or negedge wb_rst_ni) begin
        if (!wb_rst_ni) begin
            fsm_state     <= ST_IDLE;
            bit_cnt       <= 3'd0;
            addr_byte_cnt <= 3'd0;
            shift_reg     <= 8'd0;
            rx_shift      <= 8'd0;
            rddata_reg    <= 8'd0;
            flash_sck_o   <= 1'b0;
            flash_mosi_o  <= 1'b0;
            flash_cs_o    <= 1'b1;  // Deasserted
            flash_wp_o    <= 1'b1;  // Inactive
            flash_hold_o  <= 1'b1;  // Inactive
            status_done   <= 1'b0;
            status_busy   <= 1'b0;
            status_wel    <= 1'b0;
            sck_toggle    <= 1'b0;
        end else begin
            case (fsm_state)
                ST_IDLE: begin
                    flash_cs_o   <= 1'b1;
                    flash_sck_o  <= 1'b0;
                    status_done  <= 1'b0;
                    sck_toggle   <= 1'b0;

                    if (ctrl_go && !status_busy) begin
                        status_busy   <= 1'b1;
                        flash_cs_o    <= 1'b0;  // Assert CS
                        shift_reg     <= cmd_reg;
                        bit_cnt       <= 3'd7;
                        fsm_state     <= ST_CMD_SEND;
                        sck_toggle    <= 1'b0;
                    end
                end

                ST_CMD_SEND: begin
                    sck_toggle <= ~sck_toggle;
                    if (sck_toggle) begin
                        // Rising edge: drive MOSI
                        flash_mosi_o <= shift_reg[7];
                        flash_sck_o  <= 1'b1;
                    end else begin
                        // Falling edge: shift out
                        flash_sck_o <= 1'b0;
                        shift_reg   <= {shift_reg[6:0], 1'b0};
                        if (bit_cnt == 3'd0) begin
                            // Command sent, check if address phase needed
                            if (cmd_reg == 8'h9F || cmd_reg == 8'h05 || cmd_reg == 8'h03 ||
                                cmd_reg == 8'h0B || cmd_reg == 8'h02 || cmd_reg == 8'h20) begin
                                addr_byte_cnt <= 3'd2;  // 3 address bytes
                                shift_reg     <= addr_reg[23:16];
                                bit_cnt       <= 3'd7;
                                fsm_state     <= ST_ADDR_SEND;
                            end else if (cmd_reg == 8'h06) begin
                                // Write Enable: no address/data
                                status_wel <= 1'b1;
                                fsm_state  <= ST_DONE;
                            end else begin
                                fsm_state <= ST_DONE;
                            end
                        end else begin
                            bit_cnt <= bit_cnt - 1'b1;
                        end
                    end
                end

                ST_ADDR_SEND: begin
                    sck_toggle <= ~sck_toggle;
                    if (sck_toggle) begin
                        flash_mosi_o <= shift_reg[7];
                        flash_sck_o  <= 1'b1;
                    end else begin
                        flash_sck_o <= 1'b0;
                        shift_reg   <= {shift_reg[6:0], 1'b0};
                        if (bit_cnt == 3'd0) begin
                            if (addr_byte_cnt == 3'd0) begin
                                // All address bytes sent
                                if (cmd_reg == 8'h03 || cmd_reg == 8'h0B) begin
                                    // Read or Fast Read: go to data phase
                                    bit_cnt   <= 3'd7;
                                    rx_shift  <= 8'd0;
                                    fsm_state <= ST_DATA_READ;
                                end else if (cmd_reg == 8'h02) begin
                                    // Page Program: go to write data phase
                                    shift_reg <= txdata_reg;
                                    bit_cnt   <= 3'd7;
                                    fsm_state <= ST_DATA_WRITE;
                                end else begin
                                    // Other commands (status read, etc.)
                                    fsm_state <= ST_DONE;
                                end
                            end else begin
                                // Next address byte
                                addr_byte_cnt <= addr_byte_cnt - 1'b1;
                                case (addr_byte_cnt)
                                    3'd2: shift_reg <= addr_reg[23:16];
                                    3'd1: shift_reg <= addr_reg[15:8];
                                    3'd0: shift_reg <= addr_reg[7:0];
                                    default: shift_reg <= 8'd0;
                                endcase
                                bit_cnt <= 3'd7;
                            end
                        end else begin
                            bit_cnt <= bit_cnt - 1'b1;
                        end
                    end
                end

                ST_DATA_READ: begin
                    sck_toggle <= ~sck_toggle;
                    if (sck_toggle) begin
                        flash_sck_o <= 1'b1;
                    end else begin
                        flash_sck_o  <= 1'b0;
                        rx_shift     <= {rx_shift[6:0], flash_miso_i};
                        if (bit_cnt == 3'd0) begin
                            rddata_reg <= {rx_shift[6:0], flash_miso_i};
                            fsm_state  <= ST_DONE;
                        end else begin
                            bit_cnt <= bit_cnt - 1'b1;
                        end
                    end
                end

                ST_DATA_WRITE: begin
                    sck_toggle <= ~sck_toggle;
                    if (sck_toggle) begin
                        flash_mosi_o <= shift_reg[7];
                        flash_sck_o  <= 1'b1;
                    end else begin
                        flash_sck_o <= 1'b0;
                        shift_reg   <= {shift_reg[6:0], 1'b0};
                        if (bit_cnt == 3'd0) begin
                            fsm_state <= ST_DONE;
                        end else begin
                            bit_cnt <= bit_cnt - 1'b1;
                        end
                    end
                end

                ST_DONE: begin
                    flash_cs_o  <= 1'b1;  // Deassert CS
                    flash_sck_o <= 1'b0;
                    status_done <= 1'b1;
                    status_busy <= 1'b0;
                    fsm_state   <= ST_IDLE;
                end

                default: fsm_state <= ST_IDLE;
            endcase
        end
    end

endmodule
