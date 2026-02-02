`default_nettype none

module tt_um_prampal_mealy (
    input  wire [7:0] ui_in,
    output wire [7:0] uo_out,
    input  wire [7:0] uio_in,
    output wire [7:0] uio_out,
    output wire [7:0] uio_oe,
    input  wire       ena,
    input  wire       clk,
    input  wire       rst_n
);

    wire x1 = ui_in[0];

    // State encoding
    localparam A = 3'd0,
               B = 3'd1,
               C = 3'd2,
               D = 3'd3,
               E = 3'd4;

    reg [2:0] state;

    // State register
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            state <= A;
        else begin
            case (state)
                A: state <= x1 ? D : B;
                B: state <= x1 ? E : C;
                C: state <= A;
                D: state <= x1 ? C : E;
                E: state <= A;
                default: state <= A;
            endcase
        end
    end

    // Registered Mealy output (prevents race with state update)
    reg z1_reg;
    always @(posedge clk or negedge rst_n) begin
        if (!rst_n)
            z1_reg <= 1'b0;
        else
            z1_reg <= (state == D && !x1) || (state == B && x1);
    end

    assign uo_out[2:0] = state;
    assign uo_out[3]   = z1_reg;
    assign uo_out[7:4] = 4'b0;

    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule
