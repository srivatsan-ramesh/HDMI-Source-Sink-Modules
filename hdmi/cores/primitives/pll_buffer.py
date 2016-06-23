from myhdl import block, always_comb, instance, instances

inst_count = 0


@block
def pll_buffer(pll_in, g_clock, locked, io_clock, serdes_strobe, lock, divide=5):

    """

    This is just a model used for simulation and not an exact
    replica of the actual xilinx primitive BUFPLL. This will get
    replaced with the xilinx primitive during conversion.

    Args:
        pll_in: The clock signal from PLL
        g_clock: the global clock (usually the pixel clock)
        locked: A signal to indicate the locked state.
        io_clock: out put same as the pll_in
        serdes_strobe: A strobe signal assigned to the negative edge of g_clock
        lock: A lock signal
        divide: It is the ratio of frequencies of pll_in and g_clock.

    Returns:
        myhdl.instances() : A list of myhdl instances.

    """

    global inst_count

    @always_comb
    def assign_io_clock():
        io_clock.next = pll_in

    @instance
    def assign_strobe():
        lock.next = 1
        yield pll_in.posedge
        while True:
            for _ in range(divide - 1):
                yield pll_in.posedge
            serdes_strobe.next = 1
            yield pll_in.posedge
            serdes_strobe.next = 0

    inst_count += 1
    return instances()

pll_buffer.verilog_code = """
    BUFPLL #(.DIVIDE($divide)) pll_buf_$inst_count (.PLLIN($pll_in), .GCLK($g_clock), .LOCKED($locked),
           .IOCLK($io_clock), .SERDESSTROBE($serdes_strobe), .LOCK($lock));
"""
