from myhdl import Signal, intbv, always, always_comb, instances, block

from hdmi.models.constants import CONTROL_TOKEN


class DecoderModel:

    def __init__(self, clock, data_in, video_preamble, data_island_preamble, c0,
                 c1, vde, ade, video_out, audio_out, channel='BLUE'):

        """
         A non-convertible HDMI Decoder Model which decodes the TMDS data and outputs the video and aux data.
         This is modelled after the xapp495 decoder module.

        Args:
            :param clock: The system clock or the pixel clock
            :param data_in: The TMDS data (10 bits width) to be decoded
            :param video_preamble: signal to detect the video preamble in the input data
            :param data_island_preamble: signal to detect the data island preamble in the input data
            :param c0: Control signal (hsync for Blue channel)
            :param c1: Control signal (vsync for Blue channel)
            :param vde: Video Data enable
            :param ade: Audio data enable
            :param video_out: Output video data
            :param audio_out: Output audio (or aux) data.
            :param channel: Color of the channel ('RED', 'GREEN' or 'BLUE'). Default value is 'BLUE'

        Usage:
            decoder_model = DecoderModel(*params)
            process_inst = decoder_model.process()
            process_inst.run_sim()

        """

        self.clock = clock
        self.data_in = data_in
        self.video_preamble = video_preamble
        self.data_island_preamble = data_island_preamble
        self.c0 = c0
        self.c1 = c1
        self.vde = vde
        self.ade = ade
        self.video_out = video_out
        self.audio_out = audio_out
        self.channel = channel

    def get_video_data(self):

        """
        :return: The output video data
        """

        return self.video_out

    def get_audio_data(self):

        """
        :return: The output audio data(or AUX data)
        """

        return self.audio_out

    def read(self):

        """
        Waits for a positive edge of clock
        """

        yield self.clock.posedge

    def write_data(self, data_in):

        """
        Writes the given data onto the input data signal
        :param data_in: 10 bit intbv value(or a 10 bit integer)
        """

        self.data_in.next = data_in
        yield self.clock.posedge


    @block
    def process(self):

        """
        It simulates the decoding process of the TMDS decoder.

        Usage:
            process_inst = decoder_model.process()
            process_inst.run_sim()
        """

        # Control signals
        control, _control, control_end = [Signal(bool(0)) for _ in range(3)]

        # Signals to detect video period and data island period
        video_period = Signal(bool(0))
        data_island_period = Signal(bool(0))

        data = Signal(intbv(0)[8:0])

        @always_comb
        def continuous_assignment():
            data.next = ~self.data_in[8:0] if self.data_in[9] == 1 else self.data_in[8:0]
            control_end.next = (not control) & _control

        @always(self.clock.posedge)
        def sequential_logic():
            _control.next = control

            if control:
                video_period.next = 0
            elif control_end and self.video_preamble:
                video_period.next = 1

            if control:
                data_island_period.next = 0
            elif control_end and self.data_island_preamble:
                data_island_period.next = 1

            if self.data_in == CONTROL_TOKEN[0]:
                self.c0.next = 0
                self.c1.next = 0
                self.vde.next = 0
                self.ade.next = 0
                control.next = 1

            elif self.data_in == CONTROL_TOKEN[1]:
                self.c0.next = 1
                self.c1.next = 0
                self.vde.next = 0
                self.ade.next = 0
                control.next = 1

            elif self.data_in == CONTROL_TOKEN[2]:
                self.c0.next = 0
                self.c1.next = 1
                self.vde.next = 0
                self.ade.next = 0
                control.next = 1

            elif self.data_in == CONTROL_TOKEN[3]:
                self.c0.next = 1
                self.c1.next = 1
                self.vde.next = 0
                self.ade.next = 0
                control.next = 1

            else:
                control.next = 0
                if video_period:
                    self.video_out.next[0] = data[0]
                    for i in range(1, 8):
                        self.video_out.next[i] = data[i] ^ (data[i-1] if self.data_in[8] == 1 else not data[i-1])
                    self.ade.next = 0
                    self.vde.next = 1

                elif self.channel == 'BLUE' or data_island_period:
                    if self.data_in == int('1010011100', 2):
                        self.audio_out.next = 0
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1001100011', 2):
                        self.audio_out.next = 1
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1011100100', 2):
                        self.audio_out.next = 2
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1011100010', 2):
                        self.audio_out.next = 3
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0101110001', 2):
                        self.audio_out.next = 4
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0100011110', 2):
                        self.audio_out.next = 5
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0110001110', 2):
                        self.audio_out.next = 6
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0100111100', 2):
                        self.audio_out.next = 7
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1011001100', 2):
                        if self.channel == 'BLUE' and _control:
                            self.ade.next = 0
                        else:
                            self.audio_out.next = 8
                            self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0100111001', 2):
                        self.audio_out.next = 9
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0110011100', 2):
                        self.audio_out.next = 10
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1011000110', 2):
                        self.audio_out.next = 11
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1010001110', 2):
                        self.audio_out.next = 12
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1001110001', 2):
                        self.audio_out.next = 13
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('0101100011', 2):
                        self.audio_out.next = 14
                        self.ade.next = 1
                        self.vde.next = 0

                    elif self.data_in == int('1011000011', 2):
                        self.audio_out.next = 15
                        self.ade.next = 1
                        self.vde.next = 0

                    else:
                        self.audio_out.next = self.audio_out
                        self.ade.next = 0
                        self.vde.next = 0

        return instances()