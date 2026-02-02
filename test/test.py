import cocotb
from cocotb.clock import Clock
from cocotb.triggers import RisingEdge, ClockCycles

@cocotb.test()
async def test_mealy_fsm(dut):
    dut._log.info("Starting Mealy FSM test")

    # Create clock
    clock = Clock(dut.clk, 10, units="us")
    cocotb.start_soon(clock.start())

    # Initial conditions
    dut.ena.value = 1
    dut.ui_in.value = 0
    dut.uio_in.value = 0
    dut.rst_n.value = 0

    # Hold reset
    await ClockCycles(dut.clk, 2)

    # Release reset
    dut.rst_n.value = 1
    await RisingEdge(dut.clk)

    # Python model of FSM states
    A, B, C, D, E = 0, 1, 2, 3, 4
    state = A

    # Input stimulus
    x1_sequence = [0,1,0,0,1,1,0,1,0,1]

    for x1 in x1_sequence:
        dut.ui_in[0].value = x1

        # Wait for hardware to update state
        await RisingEdge(dut.clk)

        # Update expected state (matches hardware register timing)
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

        # Mealy output depends on *new* state and input
        expected_z1 = int((state == D and x1 == 0) or
                          (state == B and x1 == 1))

        # Read hardware outputs safely
        uo = dut.uo_out.value.integer
        hw_state = uo & 0b111        # bits [2:0]
        hw_z1 = (uo >> 3) & 0x1     # bit [3]

        dut._log.info(f"x1={x1} | state={hw_state} | z1={hw_z1}")

        assert hw_state == state, f"STATE MISMATCH: expected {state}, got {hw_state}"
        assert hw_z1 == expected_z1, f"OUTPUT MISMATCH: expected {expected_z1}, got {hw_z1}"

    dut._log.info("Mealy FSM test PASSED ✅")
