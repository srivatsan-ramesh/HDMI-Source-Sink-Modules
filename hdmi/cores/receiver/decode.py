from myhdl import block, Signal, always, always_comb, intbv, concat, instances

from hdmi.cores import control_token_0, control_token_1, control_token_2, control_token_3
from hdmi.cores.receiver import phase_aligner, channel_bonding, serdes_1_to_5


@block
def decode(reset, p_clock, p_clockx2, p_clockx10, serdes_strobe, data_in_p, data_in_n,
           other_ch0_valid, other_ch1_valid, other_ch0_ready, other_ch1_ready,
           video_preamble, data_island_preamble, i_am_ready, i_am_valid, phase_align_err,
           c0, c1, vde, ade, s_data_out, video_out, audio_out, channel='BLUE'):

    flip_gear, flip_gearx2, toggle, rx_toggle = [Signal(bool(0)) for _ in range(4)]

    @always(p_clockx2.posedge)
    def assign_flip_gear():
        flip_gearx2.next = flip_gear

    @always(p_clockx2.posedge, reset.posedge)
    def toggle_toggle():
        if reset:
            toggle.next = 0
        else:
            toggle.next = not toggle

    @always_comb
    def assign_toggle():
        rx_toggle.next = toggle ^ flip_gearx2

    raw_5_bit, _raw_5_bit = [Signal(intbv(0)[5:0]) for _ in range(2)]
    raw_word, raw_data = [Signal(intbv(0)[10:0]) for _ in range(2)]

    @always(p_clockx2.posedge)
    def make_10bit():
        _raw_5_bit.next = raw_5_bit
        if rx_toggle:
            raw_word.next = concat(raw_5_bit, _raw_5_bit)
        raw_data.next = raw_word

    bit_slip, _bit_slip, bit_slipx2 = [Signal(bool(0)) for _ in range(3)]

    @always(p_clockx2.posedge)
    def bitslip():
        _bit_slip.next = bit_slip
        bit_slipx2.next = bit_slip and not _bit_slip

    des_0 = serdes_1_to_5.serdes_1_to_5(Signal(True), data_in_p, data_in_n, p_clockx10,
                                        serdes_strobe, reset, p_clockx2, bit_slipx2, raw_5_bit)

    phase_aligner_0 = phase_aligner.phase_aligner(reset, p_clock, raw_data, bit_slip, flip_gear, i_am_valid)

    phase_align_err.next = 0

    data_in = Signal(intbv(0)[10:0])
    channel_bond = channel_bonding.channel_bonding(p_clock, raw_data, i_am_valid, other_ch0_valid, other_ch1_valid,
                                                   other_ch0_ready, other_ch1_ready, i_am_ready, data_in)

    # Control signals
    control, _control, control_end = [Signal(bool(0)) for _ in range(3)]

    # Signals to detect video period and data island period
    video_period = Signal(bool(0))
    data_island_period = Signal(bool(0))

    data = Signal(intbv(0)[8:0])

    is_blue = True if channel == 'BLUE' else False

    @always_comb
    def continuous_assignment():
        data.next = ~data_in[8:0] if data_in[9] else data_in[8:0]
        control_end.next = (not control) & _control

    @always(p_clock.posedge)
    def sequential_logic():
        _control.next = control

        if control:
            video_period.next = 0
        elif control_end and video_preamble:
            video_period.next = 1

        if control:
            data_island_period.next = 0
        elif control_end and data_island_preamble:
            data_island_period.next = 1

        if i_am_ready and other_ch0_ready and other_ch1_ready:
            if data_in == control_token_0:
                c0.next = 0
                c1.next = 0
                vde.next = 0
                ade.next = 0
                control.next = 1

            elif data_in == control_token_1:
                c0.next = 1
                c1.next = 0
                vde.next = 0
                ade.next = 0
                control.next = 1

            elif data_in == control_token_2:
                c0.next = 0
                c1.next = 1
                vde.next = 0
                ade.next = 0
                control.next = 1

            elif data_in == control_token_3:
                c0.next = 1
                c1.next = 1
                vde.next = 0
                ade.next = 0
                control.next = 1

            else:
                control.next = 0
                if video_period:
                    video_out.next[0] = data[0]
                    if data_in[8]:
                        video_out.next[8:1] = data[8:1] ^ data[7:0]
                    else:
                        video_out.next[8:1] = data[8:1] ^ (~ data[7:0])
                    ade.next = 0
                    vde.next = 1

                elif is_blue or data_island_period:
                    if data_in == 668:
                        audio_out.next = 0
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 611:
                        audio_out.next = 1
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 740:
                        audio_out.next = 2
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 738:
                        audio_out.next = 3
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 369:
                        audio_out.next = 4
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 286:
                        audio_out.next = 5
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 398:
                        audio_out.next = 6
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 316:
                        audio_out.next = 7
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 716:
                        if is_blue and _control:
                            ade.next = 0
                        else:
                            audio_out.next = 8
                            ade.next = 1
                        vde.next = 0

                    elif data_in == 313:
                        audio_out.next = 9
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 412:
                        audio_out.next = 10
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 710:
                        audio_out.next = 11
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 654:
                        audio_out.next = 12
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 625:
                        audio_out.next = 13
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 355:
                        audio_out.next = 14
                        ade.next = 1
                        vde.next = 0

                    elif data_in == 707:
                        audio_out.next = 15
                        ade.next = 1
                        vde.next = 0

                    else:
                        audio_out.next = audio_out
                        ade.next = 0
                        vde.next = 0

            s_data_out.next = data_in

    return instances()