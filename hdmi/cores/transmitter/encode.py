from myhdl import block, Signal, intbv, always, concat, always_seq, instances, modbv


@block
def encode(clock, reset, video_in, audio_in, c0, c1, vde, ade, data_out, channel='BLUE'):
    control_token = [852, 171, 340, 683]

    video_guard_band = 307
    data_island_guard_band = 307
    if channel == 'BLUE':
        video_guard_band = 716
        data_island_guard_band = 0
    elif channel == 'RED':
        video_guard_band = 716

    no_of_ones_video_in = Signal(intbv(0)[4:0])

    decision1 = Signal(bool(0))
    decision2 = Signal(bool(0))
    decision3 = Signal(bool(0))

    # input video delayed by a clock cycle
    _video_in = Signal(intbv(0, min=video_in.min,
                             max=video_in.max))

    # 1 bit more than the input (Signal after first stage of encoding the input)
    q_m = Signal(intbv(0, min=video_in.min,
                       max=video_in.max * 2))

    no_of_ones_q_m = Signal(intbv(0)[4:])
    no_of_zeros_q_m = Signal(intbv(0)[4:])

    count = Signal(modbv(0)[5:0])

    # delayed versions of vde signal
    _vde, __vde = [Signal(bool(0)) for _ in range(2)]

    # delayed versions of ade signal
    _ade, __ade, ___ade, ____ade = [Signal(bool(0)) for _ in range(4)]

    # delayed versions of c0 signal
    _c0, __c0 = [Signal(bool(0)) for _ in range(2)]

    # delayed versions of c1 signal
    _c1, __c1 = [Signal(bool(0)) for _ in range(2)]

    # delayed versions of audio_in signal
    _audio_in, __audio_in = [Signal(intbv(0, min=audio_in.min,
                                          max=audio_in.max)) for _ in range(2)]

    _q_m = Signal(intbv(0, min=video_in.min,
                        max=video_in.max * 2))

    # Digital island guard band period
    digb_period = Signal(bool(0))

    ade_vld = Signal(bool(0))
    audio_in_vld = Signal(intbv(0, min=audio_in.min,
                                max=audio_in.max))

    @always(clock.posedge)
    def sequential_logic():

        no_of_ones_video_in.next = video_in[0] + video_in[1] + video_in[2] + video_in[3] + \
                                   video_in[4] + video_in[5] + video_in[6] + video_in[7]
        _video_in.next = video_in
        no_of_ones_q_m.next = (q_m[0] + q_m[1] + q_m[2] + q_m[3] + q_m[4] +
                               q_m[5] + q_m[6] + q_m[7])
        no_of_zeros_q_m.next = 8 - (q_m[0] + q_m[1] + q_m[2] + q_m[3] + q_m[4] +
                                    q_m[5] + q_m[6] + q_m[7])

        _vde.next = vde
        __vde.next = _vde

        _ade.next = ade
        __ade.next = _ade
        ___ade.next = __ade
        ____ade.next = ___ade

        _c0.next = c0
        __c0.next = _c0
        _c1.next = c1
        __c1.next = _c1

        _audio_in.next = audio_in
        __audio_in.next = _audio_in

        _q_m.next = q_m

    @always(____ade, ade, __ade, no_of_ones_video_in, _video_in, count, no_of_ones_q_m, no_of_zeros_q_m, q_m,
            digb_period, __c1, __c0, __audio_in, decision1)
    def continuous_assignment():

        digb_period.next = (not __ade) and (____ade or ade)

        decision1.next = (no_of_ones_video_in > 4) or \
                         (no_of_ones_video_in == 4 and not _video_in[0])
        decision2.next = (count == 0) | (no_of_zeros_q_m == no_of_ones_q_m)
        decision3.next = (not count[4]) & (no_of_ones_q_m > no_of_zeros_q_m) | \
                         (count[4]) & (no_of_ones_q_m < no_of_zeros_q_m)

        if channel == "BLUE":

            ade_vld.next = ade | __ade | ____ade
            if digb_period:
                audio_in_vld.next = concat(bool(1), bool(1), __c1, __c0)
            else:
                audio_in_vld.next = concat(__audio_in[3], __audio_in[2], __c1, __c0)

        else:

            ade_vld.next = __ade
            audio_in_vld.next = __audio_in

        q_m.next[0] = _video_in[0]
        temp = _video_in[0]
        for i in range(1, 8):
            temp = (temp ^ (not _video_in[i] if decision1 else _video_in[i]))
            q_m.next[i] = 1 if temp else 0
        q_m.next[8] = 0 if decision1 else 1

    @always_seq(clock.posedge, reset=reset)
    def output_logic():
        if __vde:
            if decision2:
                data_out.next[9] = not _q_m[8]
                data_out.next[8] = _q_m[8]
                if _q_m[8]:
                    data_out.next[8:0] = _q_m[8:0]
                    count.next = count + no_of_ones_q_m - no_of_zeros_q_m
                else:
                    data_out.next[8:0] = ~_q_m[8:0]
                    count.next = count + no_of_zeros_q_m - no_of_ones_q_m
            elif decision3:
                data_out.next[9] = True
                data_out.next[8] = _q_m[8]
                data_out.next[8:0] = ~_q_m[8:0]
                count.next = count - concat(_q_m[8], bool(0)) + no_of_zeros_q_m - no_of_ones_q_m
            else:
                data_out.next[9] = False
                data_out.next[8] = _q_m[8]
                data_out.next[8:0] = _q_m[8:0]
                count.next = count - concat(not _q_m[8], bool(0)) + no_of_ones_q_m - no_of_zeros_q_m
        else:
            if vde:
                data_out.next = video_guard_band
            elif ade_vld:
                if audio_in_vld == 0:
                    data_out.next = 668
                elif audio_in_vld == 1:
                    data_out.next = 611
                elif audio_in_vld == 2:
                    data_out.next = 740
                elif audio_in_vld == 3:
                    data_out.next = 738
                elif audio_in_vld == 4:
                    data_out.next = 369
                elif audio_in_vld == 5:
                    data_out.next = 286
                elif audio_in_vld == 6:
                    data_out.next = 398
                elif audio_in_vld == 7:
                    data_out.next = 316
                elif audio_in_vld == 8:
                    data_out.next = 716
                elif audio_in_vld == 9:
                    data_out.next = 313
                elif audio_in_vld == 10:
                    data_out.next = 412
                elif audio_in_vld == 11:
                    data_out.next = 710
                elif audio_in_vld == 12:
                    data_out.next = 654
                elif audio_in_vld == 13:
                    data_out.next = 625
                elif audio_in_vld == 14:
                    data_out.next = 355
                elif audio_in_vld == 15:
                    data_out.next = 707
            elif (ade or ____ade) and (channel != "BLUE"):
                data_out.next = data_island_guard_band
            else:
                concat_c = concat(__c1, __c0)
                data_out.next = control_token[concat_c]

            count.next = 0

    return instances()
