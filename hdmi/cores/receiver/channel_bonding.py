from myhdl import block, Signal, always_comb, intbv, always, modbv, instances

from hdmi.cores import control_token_0, control_token_1, control_token_2, control_token_3
from hdmi.cores.primitives import dram16xn


@block
def channel_bonding(clock, raw_data, i_am_valid, other_ch0_valid, other_ch1_valid,
                    other_ch0_ready, other_ch1_ready, i_am_ready, s_data):

    raw_data_valid = Signal(False)

    @always_comb
    def assign_raw_data():
        raw_data_valid.next = other_ch0_valid and other_ch1_valid and i_am_valid

    write_addr, read_addr = [Signal(modbv(0)[4:0]) for _ in range(2)]
    write_enable = Signal(False)

    @always(clock.posedge)
    def assign_write():
        write_enable.next = raw_data_valid
        if raw_data_valid:
            write_addr.next = write_addr + 1
        else:
            write_addr.next = 0

    fo_data_out, fo_data_out_dp = [Signal(intbv(0)[10:0]) for _ in range(2)]
    cbfifo_i = dram16xn(raw_data, write_addr, read_addr, write_enable, clock, fo_data_out, fo_data_out_dp, 10)

    @always(clock.posedge)
    def assign_data():
        s_data.next = fo_data_out_dp

    received_ctrl_token, _received_ctrl_token, blank_begin = [Signal(False) for _ in range(3)]

    @always(clock.posedge)
    def assign_control():
        received_ctrl_token.next = (s_data == control_token_0) or (s_data == control_token_1) \
                                   or (s_data == control_token_2) or (s_data == control_token_3)

        _received_ctrl_token.next = received_ctrl_token
        blank_begin.next = not _received_ctrl_token and received_ctrl_token

    next_blank_begin, skip_line = [Signal(False) for _ in range(2)]

    @always(clock.posedge)
    def skip_curr_line():
        if not raw_data_valid:
            skip_line.next = 0
        elif blank_begin:
            skip_line.next = 1

    @always_comb
    def assign_next_blank():
        next_blank_begin.next = skip_line and blank_begin

    # Declare my own readiness
    @always(clock.posedge)
    def readiness():
        if not raw_data_valid:
            i_am_ready.next = 0
            if __debug__:
                i_am_ready.next = 1
        elif next_blank_begin:
            i_am_ready.next = 1
    _raw_data_valid, raw_data_valid_rising = [Signal(False) for _ in range(2)]

    @always(clock.posedge)
    def assign_raw_data_validity():
        _raw_data_valid.next = raw_data_valid
        raw_data_valid_rising.next = raw_data_valid and not _raw_data_valid

    read_addr_enable = Signal(False)

    @always(clock.posedge)
    def assign_enable():
        if raw_data_valid_rising or (other_ch0_ready and other_ch1_ready and i_am_ready):
            read_addr_enable.next = 1
        elif next_blank_begin and not(other_ch0_ready and other_ch1_ready and i_am_ready):
            read_addr_enable.next = 0

    @always(clock.posedge)
    def read_addr_counter():
        if not raw_data_valid:
            read_addr.next = 0
        elif read_addr_enable:
            read_addr.next = read_addr + 1

    return instances()
