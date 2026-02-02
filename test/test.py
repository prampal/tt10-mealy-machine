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

    # Python model of the FSM
    A, B, C, D, E = 0, 1, 2, 3, 4
    state = A

    x1_sequence = [0,1,0,0,1,1,0,1,0,1]

    for x1 in x1_sequence:
        dut.ui_in[0].value = x1

        # Expected Mealy output BEFORE state updates
        expected_z1 = int((state == D and x1 == 0) or
                          (state == B and x1 == 1))

        await RisingEdge(dut.clk)

        # Update model state
        if state == A:
            state = D if x1 else B
        elif state == B:
            state = E if x1 else C
        elif state == C:
            state = A
        elif state == D:
            state = C if x1 else E
        elif state == E:
            state = A

        uo = dut.uo_out.value.integer
        hw_state = uo & 0b111
        hw_z1 = (uo >> 3) & 1

        dut._log.info(f"x1={x1} | state={hw_state} | z1={hw_z1}")

        assert hw_z1 == expected_z1, f"z1 mismatch: expected {expected_z1}, got {hw_z1}"
        assert hw_state == state, f"state mismatch: expected {state}, got {hw_state}"

    dut._log.info("Mealy FSM test PASSED ✅")
