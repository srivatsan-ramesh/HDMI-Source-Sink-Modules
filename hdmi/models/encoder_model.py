import math

from myhdl import always, Signal, intbv, ConcatSignal, always_seq, instances, block


class EncoderModel:

    def __init__(self, clock, reset, video_in, audio_in, c0, c1, vde, ade, data_out, channel='BLUE'):
        """
         A non convertible model to simulate the behaviour of
         a TMDS and TERC4 encoder.

        :param clock: pixel clock as input
        :param reset: asynchronous reset input (active high)
        :param video_in: video input of a single channel
        :param audio_in: audio input
        :param c0: used to determine preamble
        :param c1: used to determine preamble
        :param vde: video data enable
        :param ade: audio data enable
        :param data_out: 10 bit parallel output
        :param channel: Indicates 'RED', 'GREEN' or 'BLUE' channel
        """
        self.channel = channel
        self.clock = clock
        self.reset = reset
        self.video_in = video_in
        self.audio_in = audio_in
        self.c0 = c0
        self.c1 = c1
        self.vde = vde
        self.ade = ade
        self.data_out = data_out
        self.color_depth = int(math.log(video_in.max, 2))

    def write_video(self, video_in):

        yield self.clock.posedge
        self.video_in.next = video_in

    def write_audio(self, audio_in):

        yield self.clock.posedge
        self.audio_in.next = audio_in

    def write_controls(self, c0, c1, vde, ade):

        yield self.clock.posedge
        self.c0.next = c0
        self.c1.next = c1
        self.vde.next = vde
        self.ade.next = ade

    def read(self):

        pass

    @block
    def process(self):

        """
        create an instance of this function and it can be simulated
        """

        control_token = ['1101010100',  # 00
                         '0010101011',  # 01
                         '0101010100',  # 10
                         '1010101011']  # 11

        video_guard_band = {
            'BLUE': int('1011001100', 2),
            'GREEN': int('0100110011', 2)
        }.get(self.channel, int('1011001100', 2))

        data_island_guard_band = {
            'GREEN': int('0100110011', 2),
            'RED': int('0100110011', 2)
        }.get(self.channel, 0)

        no_of_ones_video_in = Signal(intbv(0)[math.log(self.color_depth, 2):])

        decision1 = Signal(bool(0))
        decision2 = Signal(bool(0))
        decision3 = Signal(bool(0))

        # input video delayed by a clock cycle
        _video_in = Signal(intbv(0, min=self.video_in.min,
                                 max=self.video_in.max))

        # 1 bit more than the input (After first stage of encoding)
        q_m = Signal(intbv(0, min=self.video_in.min,
                           max=self.video_in.max * 2))

        no_of_ones_q_m = Signal(intbv(0)[math.log(self.color_depth, 2)+1:])
        no_of_zeros_q_m = Signal(intbv(0)[math.log(self.color_depth, 2)+1:])

        count = Signal(intbv(0)[5:0])

        _vde, __vde = [Signal(bool(0)) for _ in range(2)]

        _ade, __ade, ___ade, ____ade = [Signal(bool(0)) for _ in range(4)]

        _c0, __c0 = [Signal(bool(0)) for _ in range(2)]

        _c1, __c1 = [Signal(bool(0)) for _ in range(2)]

        _audio_in, __audio_in = [Signal(intbv(0, min=self.audio_in.min,
                                              max=self.audio_in.max)) for _ in range(2)]

        _q_m = Signal(intbv(0, min=self.video_in.min,
                            max=self.video_in.max * 2))

        # Digital island guard band period
        digb_period = Signal(bool(0))

        ade_vld = Signal(bool(0))
        audio_in_vld = Signal(intbv(0, min=self.audio_in.min,
                                    max=self.audio_in.max))

        @always(self.clock.posedge)
        def sequential_logic():

            no_of_ones_video_in.next = bin(self.video_in).count("1")
            _video_in.next = self.video_in
            no_of_ones_q_m.next = bin(q_m).count("1")
            no_of_zeros_q_m.next = 8 - bin(q_m).count("1")

            _vde.next = self.vde
            __vde.next = _vde

            _ade.next = self.ade
            __ade.next = _ade
            ___ade.next = __ade
            ____ade.next = ___ade

            _c0.next = self.c0
            __c0.next = _c0
            _c1.next = self.c1
            __c1.next = _c1

            _audio_in.next = self.audio_in
            __audio_in.next = _audio_in

            _q_m.next = q_m

        @always(____ade, self.ade, __ade, no_of_ones_video_in, _video_in, count, no_of_ones_q_m, no_of_zeros_q_m, q_m,
                digb_period, __c1, __c0, __audio_in, decision1)
        def continuous_assignment():

            digb_period.next = (not __ade) and (____ade or self.ade)

            decision1.next = (no_of_ones_video_in > 4) or \
                             (no_of_ones_video_in == 4 and _video_in[0] == False)
            decision2.next = (count == 0) | (no_of_zeros_q_m == no_of_ones_q_m)
            decision3.next = (not count[4]) & (no_of_ones_q_m > no_of_zeros_q_m) | \
                             (count[4]) & (no_of_ones_q_m < no_of_zeros_q_m)

            if self.channel == "BLUE":

                ade_vld.next = self.ade | __ade | ____ade
                if digb_period:
                    audio_in_vld.next = ConcatSignal(bool(1), bool(1), __c1, __c0)
                else:
                    audio_in_vld.next = ConcatSignal(__audio_in[3], __audio_in[2], __c1, __c0)

            else:

                ade_vld.next = __ade
                audio_in_vld.next = __audio_in

            q_m.next[0] = _video_in[0]
            temp = _video_in[0]
            for i in range(1, self.color_depth):
                temp = (temp ^ (not _video_in[i] if decision1 else _video_in[i]))
                q_m.next[i] = 1 if temp else 0
            q_m.next[self.color_depth] = 0 if decision1 else 1

        @always_seq(self.clock.posedge, reset=self.reset)
        def output_logic():
            if __vde:
                if decision2:
                    self.data_out.next[9] = not _q_m[8]
                    self.data_out.next[8] = _q_m[8]
                    if _q_m[8]:
                        self.data_out.next[8:0] = _q_m[8:0]
                        count.next = count + no_of_ones_q_m - no_of_zeros_q_m
                    else:
                        self.data_out.next[8:0] = ~_q_m[8:0]
                        count.next = count + no_of_zeros_q_m - no_of_ones_q_m
                elif decision3:
                    self.data_out.next[9] = True
                    self.data_out.next[8] = _q_m[8]
                    self.data_out.next[8:0] = ~_q_m[8:0]
                    count.next = count - ConcatSignal(_q_m[8], bool(0)) + no_of_zeros_q_m - no_of_ones_q_m
                else:
                    self.data_out.next[9] = False
                    self.data_out.next[8] = _q_m[8]
                    self.data_out.next[8:0] = _q_m[8:0]
                    count.next = count - ConcatSignal(not _q_m[8], bool(0)) + no_of_ones_q_m - no_of_zeros_q_m
            else:
                if self.vde:
                    self.data_out.next = video_guard_band
                elif ade_vld:
                    terc4_encoding = ['1010011100',
                                      '1001100011',
                                      '1011100100',
                                      '1011100010',
                                      '0101110001',
                                      '0100011110',
                                      '0110001110',
                                      '0100111100',
                                      '1011001100',
                                      '0100111001',
                                      '0110011100',
                                      '1011000110',
                                      '1010001110',
                                      '1001110001',
                                      '0101100011',
                                      '1011000011']
                    self.data_out.next = int(terc4_encoding[audio_in_vld], 2)
                elif (self.ade | ____ade) and (self.channel != "BLUE"):
                    self.data_out.next = data_island_guard_band
                else:
                    concat_c = ConcatSignal(__c1, __c0)
                    self.data_out.next = int(control_token[concat_c], 2)

                count.next = 0

        return instances()
