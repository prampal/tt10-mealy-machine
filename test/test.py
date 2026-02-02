import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_mealy_fsm(dut):
    dut._log.info("Starting Mealy FSM test")

    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    await ClockCycles(dut.clk, 2)
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # State encoding must match Verilog
    A, B, C, D, E = 0, 1, 2, 3, 4
    state = A

    x1_sequence = [0,1,0,0,1,1,0,1,0,1]

    for x1 in x1_sequence:
        dut.ui_in[0].value = x1

        # WAIT for clock → hardware updates state register
        await RisingEdge(dut.clk)

        # ---- MODEL NEXT STATE (exact copy of RTL logic) ----
        if state == A:
            next_state = D if x1 else B
        elif state == B:
            next_state = E if x1 else C
        elif state == C:
            next_state = A
        elif state == D:
            next_state = C if x1 else E
        elif state == E:
            next_state = A
        else:
            next_state = A

        state = next_state

        # ---- MODEL MEALY OUTPUT (matches RTL equation) ----
        expected_z1 = int((state == D and x1 == 0) or
                          (state == B and x1 == 1))

        # ---- READ HARDWARE OUTPUTS ----
        uo = dut.uo_out.value.integer
        hw_state = uo & 0b111
        hw_z1 = (uo >> 3) & 1

        dut._log.info(f"x1={x1} | expected_state={state} hw_state={hw_state} | expected_z1={expected_z1} hw_z1={hw_z1}")

        assert hw_state == state, f"STATE MISMATCH: expected {state}, got {hw_state}"
        assert hw_z1 == expected_z1, f"OUTPUT MISMATCH: expected {expected_z1}, got {hw_z1}"

    dut._log.info("Mealy FSM test PASSED ✅")
