from myhdl import block, Signal, modbv, intbv, always

from hdmi.cores.primitives import buffer_ds, cascaded_io_delay
from hdmi.cores.primitives import cascaded_iserdes


@block
def serdes_1_to_5(use_phase_detector, data_in_p, data_in_n, rx_io_clock,
                  rx_serdes_strobe, reset, g_clock, bit_slip, data_out,
                  diff_term='TRUE', bit_slip_enable='TRUE'):

    sim_tap_delay = 49
    d_delay_m, d_delay_s, busy_s, rx_data_in, cascade, pd_edge = [Signal(False) for _ in range(6)]
    counter = Signal(modbv(0)[9:0])
    state = Signal(intbv(0)[4:0])
    cal_data_s_int, busy_data, busy_data_d, cal_data_slave = [Signal(False) for _ in range(4)]
    enable, cal_data_master, reset_data, inc_data_int, inc_data = [Signal(False) for _ in range(5)]
    ce_data, valid_data_d, incdec_data_d, valid_data, incdec_data = [Signal(False) for _ in range(5)]
    pd_counter = Signal(modbv(0)[5:0])
    flag, mux, ce_data_inta, incdec_data_im, valid_data_im, all_ce = [Signal(False) for _ in range(6)]
    incdec_data_or, valid_data_or, busy_data_or, debug_in = [Signal(intbv(0)[2:0]) for _ in range(4)]

    @always(busy_s, cal_data_s_int, inc_data_int, incdec_data, mux, incdec_data_im,
            incdec_data_or, valid_data, valid_data_im, valid_data_or)
    def assign():
        busy_data.next = busy_s
        cal_data_slave.next = cal_data_s_int
        inc_data.next = inc_data_int
        incdec_data_or.next[0] = 0
        valid_data_or.next[0] = 0
        busy_data_or.next[0] = 0
        incdec_data_im.next = incdec_data and mux
        incdec_data_or.next[1] = incdec_data_im or incdec_data_or
        valid_data_im.next = valid_data and mux
        valid_data_or.next[1] = valid_data_im or valid_data_or
        all_ce.next = debug_in[0]

    # IDELAY Calibration FSM
    @always(g_clock.posedge, reset.posedge)
    def sequential_logic():
        if reset == 1:
            state.next = 0
            cal_data_master.next = 0
            cal_data_s_int.next = 0
            counter.next = 0
            enable.next = 0
            mux.next = 1
        else:
            counter.next = counter + 1
            if counter[8]:
                counter.next = 0
            if counter[5]:
                enable.next = 1
            if state == 0 and enable == 1:
                cal_data_master.next = 0
                cal_data_s_int.next = 0
                reset_data.next = 0
                if not busy_data_d:
                    state.next = 1
            elif state == 1:
                cal_data_master.next = 1
                cal_data_s_int.next = 1
                if busy_data_d:
                    state.next = 2
            elif state == 2:
                cal_data_master.next = 0
                cal_data_s_int.next = 0
                if not busy_data_d:
                    reset_data.next = 1
                    state.next = 3
            elif state == 3:
                reset_data.next = 0
                if not busy_data_d:
                    state.next = 4
            elif state == 4:
                if counter[8]:
                    state.next = 5
            elif state == 5:
                if not busy_data_d:
                    cal_data_s_int.next = 1
                    state.next = 6
            elif state == 6:
                cal_data_s_int.next = 0
                if busy_data_d:
                    state.next = 7
            elif state == 7:
                cal_data_s_int.next = 0
                if not busy_data_d:
                    state.next = 4

    # Per-bit phase detection state machine
    @always(g_clock.posedge, reset.posedge)
    def phase_detection():
        if reset:
            pd_counter.next = 8
            ce_data_inta.next = 0
            flag.next = 0
        else:
            busy_data_d.next = busy_data_or[1]
            if use_phase_detector:
                incdec_data_d.next = incdec_data_or[1]
                valid_data_d.next = valid_data_or[1]
                if ce_data_inta:
                    ce_data.next = mux
                else:
                    ce_data.next = 0
                if state == 7:
                    flag.next = 0
                elif state != 4 or busy_data_d:
                    pd_counter.next = 16
                    ce_data_inta.next = 0
                elif pd_counter == 31 and flag == 0:
                    ce_data_inta.next = 1
                    inc_data_int.next = 1
                    pd_counter.next = 16
                    flag.next = 1
                elif pd_counter == 0 and flag == 0:
                    ce_data_inta.next = 1
                    inc_data_int.next = 0
                    pd_counter.next = 16
                    flag.next = 1
                elif valid_data_d:
                    ce_data_inta.next = 0
                    if incdec_data_d == 1 and pd_counter != 31:
                        pd_counter.next = pd_counter + 1
                    elif incdec_data_d == 0 and pd_counter != 0:
                        pd_counter.next = pd_counter + 31
                else:
                    ce_data_inta.next = 0
            else:
                ce_data.next = all_ce
                inc_data_int.next = debug_in[1]

    data_in = buffer_ds(data_in_p, data_in_n, rx_data_in, diff_term)
    io_delay = cascaded_io_delay(rx_data_in, d_delay_m, d_delay_s, rx_io_clock, g_clock, cal_data_master,
                                 cal_data_slave, inc_data, ce_data, reset_data, busy_s, sim_tap_delay)
    iserdes = cascaded_iserdes(d_delay_m, d_delay_s, rx_io_clock, rx_serdes_strobe, reset, g_clock, pd_edge,
                               cascade, bit_slip, valid_data, incdec_data, data_out, bit_slip_enable)

    rx_pd_counter = Signal(modbv(127)[8:])

    @always(g_clock.posedge, reset.posedge)
    def assign_rx_pd_counter():
        if reset:
            rx_pd_counter.next = 127
        elif ce_data:
            if inc_data:
                rx_pd_counter.next = rx_pd_counter + 1
            else:
                rx_pd_counter.next = rx_pd_counter - 1

    return assign, sequential_logic, phase_detection, data_in, io_delay, iserdes, assign_rx_pd_counter