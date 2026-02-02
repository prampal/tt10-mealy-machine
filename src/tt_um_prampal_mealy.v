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

    // State registers
    reg [2:0] state, next_state;

    localparam A = 3'd0,
               B = 3'd1,
               C = 3'd2,
               D = 3'd3,
               E = 3'd4;

    // State update
    always @(posedge clk) begin
        if (!rst_n)
            state <= A;
        else
            state <= next_state;
    end

    // Next-state logic
    always @(*) begin
        case (state)
            A: next_state = x1 ? D : B;
            B: next_state = x1 ? E : C;
            C: next_state = A;
            D: next_state = x1 ? C : E;
            E: next_state = A;
            default: next_state = A;
        endcase
    end

    // 🔥 Mealy output (depends on state AND input)
    wire z1 = (state == D && !x1) ||
              (state == B &&  x1);

    // Outputs
    assign uo_out[2:0] = state;
    assign uo_out[3]   = z1;
    assign uo_out[7:4] = 4'b0000;

    assign uio_out = 8'b0;
    assign uio_oe  = 8'b0;

    wire _unused = &{ena, ui_in[7:1], uio_in, 1'b0};

endmodule
