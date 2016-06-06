from myhdl import block, always, Signal, modbv, ConcatSignal, intbv, always_comb, instances

INIT = 1
SEARCH = 2
BIT_SLIP = 4
RCVD_CTRL_TKN = 8  # Received control token
BLANK_PERIOD = 16
PHASE_ALIGNED = 32   # Phase Alignment Achieved
nSTATES = 6


@block
def phase_aligner(reset, clock, s_data, bit_slip, flip_gear, phase_aligned):

    control_token = [852,  # 00
                     171,  # 01
                     340,  # 10
                     683]  # 11

    open_eye_counter_width = 3
    ctrl_tkn_counter_width = 7
    search_timer_width = 12
    blank_period_counter_width = 1

    received_ctrl_token, _received_ctrl_token, blank_begin = [Signal(False)  for _ in range(3)]

    @always(clock.posedge)
    def assign_control():
        received_ctrl_token.next = (s_data == control_token[0]) or (s_data == control_token[1]) \
                                   or (s_data == control_token[2]) or (s_data == control_token[3])

        _received_ctrl_token.next = received_ctrl_token
        blank_begin.next = not _received_ctrl_token and received_ctrl_token

    ctrl_tkn_search_timer = Signal(modbv(0)[search_timer_width:])
    ctrl_tkn_search_reset = Signal(False)

    @always(clock.posedge)
    def search_timer():
        if ctrl_tkn_search_reset:
            ctrl_tkn_search_timer.next = 0
        else:
            ctrl_tkn_search_timer.next = ctrl_tkn_search_timer + 1

    ctrl_tkn_search_tout = Signal(False)

    @always(clock.posedge)
    def search_time_out():
        ctrl_tkn_search_tout.next = ctrl_tkn_search_timer == ConcatSignal([True for _ in range(search_timer_width)])

    ctrl_tkn_event_timer = Signal(modbv(0)[ctrl_tkn_counter_width:])
    ctrl_tkn_event_reset = Signal(False)

    @always(clock.posedge)
    def event_timer():
        if ctrl_tkn_event_reset:
            ctrl_tkn_event_timer.next = 0
        else:
            ctrl_tkn_event_timer.next = ctrl_tkn_event_timer + 1

    ctrl_tkn_event_tout = Signal(False)

    @always(clock.posedge)
    def event_time_out():
        ctrl_tkn_event_tout.next = ctrl_tkn_event_timer == ConcatSignal([True for _ in range(ctrl_tkn_counter_width)])

    # Below starts the phase alignment state machine
    curr_state = Signal(intbv(1)[nSTATES:])
    next_state = Signal(intbv(0)[nSTATES:])

    @always(clock.posedge, reset.posedge)
    def assign_state():
        if reset:
            curr_state.next = INIT
        else:
            curr_state.next = next_state

    blank_period_counter = Signal(modbv(0)[blank_period_counter_width:])

    @always_comb
    def switch_state():
        if curr_state == INIT:
            next_state.next = SEARCH if ctrl_tkn_search_tout else INIT
        elif curr_state == SEARCH:
            if blank_begin:
                next_state.next = RCVD_CTRL_TKN
            else:
                next_state.next = BIT_SLIP if ctrl_tkn_search_tout else SEARCH
        elif curr_state == BIT_SLIP:
            next_state.next = SEARCH
        elif curr_state == RCVD_CTRL_TKN:
            if received_ctrl_token:
                next_state.next = BLANK_PERIOD if ctrl_tkn_event_tout else RCVD_CTRL_TKN
            else:
                next_state.next = SEARCH
        elif curr_state == BLANK_PERIOD:
            if blank_period_counter == ConcatSignal([True for _ in range(blank_period_counter_width)]):
                next_state.next = PHASE_ALIGNED
            else:
                next_state.next = SEARCH
        elif curr_state == PHASE_ALIGNED:
            next_state.next = PHASE_ALIGNED

    bit_slip_counter = Signal(modbv(0)[3:0])

    @always(clock.posedge, reset.posedge)
    def assign():

        if reset:
            phase_aligned.next = 0
            bit_slip.next = 0
            ctrl_tkn_search_reset.next = 1
            ctrl_tkn_event_reset.next = 1
            bit_slip.next = 0
            bit_slip_counter.next = 0
            flip_gear.next = 0
            blank_period_counter.next = 0

        else:
            if curr_state == INIT:
                ctrl_tkn_search_reset.next = 0
                ctrl_tkn_event_reset.next = 1
                bit_slip.next = 0
                phase_aligned.next = 0
                bit_slip.next = 0
                bit_slip_counter.next = 0
                flip_gear.next = 0
                blank_period_counter.next = 0

            elif curr_state == SEARCH:
                ctrl_tkn_search_reset.next = 0
                ctrl_tkn_event_reset.next = 1
                bit_slip.next = 0
                phase_aligned.next = 0

            elif curr_state == BIT_SLIP:
                ctrl_tkn_search_reset.next = 1
                bit_slip.next = 1
                bit_slip_counter.next = bit_slip_counter + 1
                flip_gear.next = bit_slip_counter[2]

            elif curr_state == RCVD_CTRL_TKN:
                ctrl_tkn_search_reset.next = 0
                ctrl_tkn_event_reset.next = 0

            elif curr_state == BLANK_PERIOD:
                blank_period_counter.next = blank_period_counter + 1

            elif curr_state == PHASE_ALIGNED:
                phase_aligned.next = 1

    return instances()
