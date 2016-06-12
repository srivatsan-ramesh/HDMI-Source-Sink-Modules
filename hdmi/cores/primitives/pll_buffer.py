from myhdl import block, always_comb, instance

inst_count = 0


@block
def pll_buffer(pll_in, g_clock, locked, io_clock, serdes_strobe, lock, divide=5):

    global inst_count

    @always_comb
    def assign_io_clock():
        io_clock.next = pll_in

    @instance
    def assign_strobe():
        lock.next = 1
        while True:
            for _ in range(divide):
                yield pll_in
            serdes_strobe.next = 1
            yield pll_in
            yield pll_in
            serdes_strobe.next = 0
            for _ in range(divide-2):
                yield pll_in

    inst_count += 1
    return assign_io_clock, assign_strobe

pll_buffer.verilog_code = """
    BUFPLL #(.DIVIDE($divide)) pll_buf_$inst_count (.PLLIN($pll_in), .GCLK($g_clock), .LOCKED($locked),
           .IOCLK($io_clock), .SERDESSTROBE($serdes_strobe), .LOCK($lock));
"""
