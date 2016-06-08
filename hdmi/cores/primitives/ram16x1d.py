from myhdl import block, Signal, intbv, always_comb, always


@block
def ram16x1d(data_in, write_enable, clock, address, dual_port_address,
             single_port_output, dual_port_output, data_width):

    mem = [Signal(intbv(0)[16:0]) for _ in range(data_width)]

    @always_comb
    def assign():
        for i in range(data_width):
            single_port_output.next[i] = mem[i][address]
            dual_port_output.next[i] = mem[i][dual_port_address]

    @always(clock.posedge)
    def seq_logic():
        if write_enable:
            for i in range(data_width):
                mem[i].next[address] = data_in[i]

    return assign, seq_logic
